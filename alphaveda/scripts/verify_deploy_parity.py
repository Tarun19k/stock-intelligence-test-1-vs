#!/usr/bin/env python3
"""Deploy-parity gate: compares migration files in supabase/migrations/ against
what's actually reachable on live production Supabase.

ROOT CAUSE THIS CLOSES (2026-07-26 incident): code querying `magnitude_hit`/
`outcome` on `accuracy_outcomes` was merged to `main` (auto-deploys to Vercel) before
migration 0018 (supabase/migrations/0018_accuracy_outcomes_add_magnitude.sql) had
been applied to production. `/accuracy` silently showed "0 Resolved" instead of 108
real rows, for an unknown window, with zero errors in Vercel's logs — the Supabase
query errored and a `?? []` fallback swallowed it. `verify_migrations.py` (G-MIG
gate) already existed and would have caught this, but it was never wired into CI —
only documented as a manual step in CONTRIBUTING.md. This script is that gate,
wired into CI (see .github/workflows/deploy-parity-check.yml), running on every
push to main.

HOW IT WORKS
Every migration file must carry at least one `-- PARITY-CHECK: <kind> <spec>`
annotation (see supabase/migrations/0014-0018 for examples). Two kinds:

  column <table>.<column>   Checked live via `select(column).limit(0)` against
                             production Supabase (same PostgREST-based technique
                             verify_migrations.py already uses). This is exactly the
                             incident's failure category — a query against a column
                             that doesn't exist yet — so it's the one this script can
                             mechanically verify and FAILS LOUD on mismatch.

  manual <description>      Declares a change this script cannot verify via
                             PostgREST alone (constraints, column-width changes,
                             renames beyond what a plain select proves). These are
                             listed, not silently skipped, so a human knows what
                             still needs a manual look — but they don't fail the
                             build, since there's no mechanical way to check them
                             without raw SQL access this repo's service role doesn't
                             expose through the REST API.

A migration file with ZERO `PARITY-CHECK` annotations of either kind is itself a
FAILURE: every future migration must declare what parity looks like for it, or the
gate has no way to know it should be checking anything at all. This is what makes
the gate self-maintaining — a migration can't silently skip the check the way this
whole mechanism was skipped for migration 0018.

Exit 0 = every `column` check passes (or there are none) AND every migration file
          has at least one annotation.
Exit 1 = any `column` check fails against live production, OR any migration file
          lacks a PARITY-CHECK annotation. Prints the exact unapplied migration
          file(s) and failing column(s) by name.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

MIGRATIONS_DIR = Path(__file__).parent.parent / "supabase" / "migrations"

PARITY_RE = re.compile(r"--\s*PARITY-CHECK:\s*(column|manual)\s+(\S.*)$")


def parse_migration_checks(path: Path):
    """Return list of (kind, spec) tuples found in a migration file."""
    checks = []
    for line in path.read_text().splitlines():
        m = PARITY_RE.search(line.strip())
        if m:
            kind, spec = m.group(1), m.group(2).strip()
            checks.append((kind, spec))
    return checks


def main():
    if not MIGRATIONS_DIR.is_dir():
        print(f"FAIL: migrations directory not found at {MIGRATIONS_DIR}")
        sys.exit(1)

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        print(f"FAIL: no migration files found in {MIGRATIONS_DIR}")
        sys.exit(1)

    print(f"Found {len(migration_files)} migration file(s) in {MIGRATIONS_DIR}")

    # --- Step 1: every migration file must declare what parity looks like ---
    unannotated = []
    file_checks = {}
    for f in migration_files:
        checks = parse_migration_checks(f)
        file_checks[f] = checks
        if not checks:
            unannotated.append(f)

    if unannotated:
        print("\nFAIL: migration file(s) with no PARITY-CHECK annotation — cannot")
        print("verify these were applied to production. Add at least one")
        print("'-- PARITY-CHECK: column <table>.<col>' or")
        print("'-- PARITY-CHECK: manual <description>' line before merging:")
        for f in unannotated:
            print(f"  {f.name}")
        sys.exit(1)

    # --- Step 2: connect to live production Supabase ---
    from supabase import create_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print("FAIL: SUPABASE_URL or SUPABASE_SERVICE_KEY not set (env or .env)")
        sys.exit(1)

    sb = create_client(url, key)

    unapplied = []  # list of (migration_file, spec) that failed a live check
    manual_notes = []  # list of (migration_file, spec) not mechanically checkable

    for f in migration_files:
        for kind, spec in file_checks[f]:
            if kind == "manual":
                manual_notes.append((f, spec))
                continue

            # kind == "column" -> spec is "table.column"
            if "." not in spec:
                print(f"FAIL: malformed PARITY-CHECK in {f.name}: 'column {spec}'"
                      " (expected 'table.column')")
                unapplied.append((f, spec))
                continue

            table, col = spec.split(".", 1)
            try:
                sb.table(table).select(col).limit(0).execute()
                print(f"  OK    {f.name}: {table}.{col}")
            except Exception as e:
                print(f"  FAIL  {f.name}: {table}.{col} — {e}")
                unapplied.append((f, spec))

    print()
    if manual_notes:
        print(f"{len(manual_notes)} manual-verification item(s) — not mechanically")
        print("checkable via PostgREST, confirm by hand if in doubt:")
        for f, spec in manual_notes:
            print(f"  {f.name}: {spec.splitlines()[0]}")
        print()

    if unapplied:
        unapplied_files = sorted({f.name for f, _ in unapplied})
        print(f"DEPLOY-PARITY FAIL — {len(unapplied)} check(s) failed against live "
              f"production Supabase.")
        print(f"Unapplied migration file(s): {', '.join(unapplied_files)}")
        print("These migration files exist in the repo but their columns are not")
        print("reachable on production. Apply them via Supabase Dashboard -> SQL")
        print("Editor (or `supabase db push`) before this code path ships, or the")
        print("live queries against these columns will error and get silently")
        print("swallowed by any `?? []`-style fallback, same as the 2026-07-26")
        print("incident this gate exists to catch.")
        sys.exit(1)

    print(f"DEPLOY-PARITY PASS — all {len(migration_files)} migration file(s) "
          f"accounted for, all mechanically-checkable columns present on "
          f"production.")


if __name__ == "__main__":
    main()

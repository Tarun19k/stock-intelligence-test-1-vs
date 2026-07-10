"""Codegen: alphaveda/constants.py SEBI_DISCLAIMER -> alphaveda/web/lib/sebi-disclaimer.generated.ts

Why this exists (NG-4 / A2):
Regulatory disclaimer text must be a hardcoded, build-time constant — never a
runtime-mutable Vercel env var (that would let anyone change SEBI-facing legal
copy via a dashboard edit, with zero code review). constants.py is the
Python-side source of truth; this script mechanically derives the TS constant
from it so there is exactly one place a human edits the wording.

Run manually after any change to SEBI_DISCLAIMER in constants.py:
    python3 alphaveda/scripts/generate_sebi_disclaimer_ts.py

tests/test_constants.py::test_generated_ts_disclaimer_matches_source re-runs
this generation logic and diffs it against the checked-in .generated.ts file,
so CI fails loudly if someone edits constants.py without regenerating, or
edits the .generated.ts file by hand instead of through this script.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALPHAVEDA_DIR = REPO_ROOT / "alphaveda"
OUTPUT_PATH = ALPHAVEDA_DIR / "web" / "lib" / "sebi-disclaimer.generated.ts"

sys.path.insert(0, str(ALPHAVEDA_DIR))


def render(disclaimer: str) -> str:
    # JSON-style escaping is sufficient for TS string literals (same escape rules
    # for the characters this text can plausibly contain).
    import json

    escaped = json.dumps(disclaimer)
    return (
        "// GENERATED FILE — do not edit by hand.\n"
        "// Source of truth: alphaveda/constants.py SEBI_DISCLAIMER.\n"
        "// Regenerate with: python3 alphaveda/scripts/generate_sebi_disclaimer_ts.py\n"
        "// CI sync check: alphaveda/tests/test_constants.py::test_generated_ts_disclaimer_matches_source\n"
        "\n"
        f"export const SEBI_DISCLAIMER: string = {escaped}\n"
    )


def main() -> None:
    from constants import SEBI_DISCLAIMER  # local import: needs ALPHAVEDA_DIR on sys.path

    OUTPUT_PATH.write_text(render(SEBI_DISCLAIMER), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

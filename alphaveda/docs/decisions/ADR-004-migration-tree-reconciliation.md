# ADR-004: Migration-Tree Reconciliation — Root Tree Is Canonical

**Status:** Accepted (2026-07-30)
**Related commits:** `b5ae1e2`, `9aa6e73`

## Context

Two separate migration trees existed: `supabase/migrations/` (root, CLI-tracked, matched
`supabase migration list`'s remote history) and `alphaveda/supabase/migrations/` (0001-0019,
untracked by the CLI, applied to production by an unknown historical process). Additionally, 9
migrations were recorded as applied in production's `schema_migrations` table with no
corresponding file in either tree — the root cause of the long-open GHA issue #5 (deploy-parity
alert).

## Decision

The root `supabase/migrations/` tree is canonical going forward — it is what the CLI, `supabase
migration list`, and the deploy-parity GHA check all actually operate against. The 9 fileless
migrations were reconstructed from live schema introspection (verified column types/defaults
against `information_schema`, not assumed) and added as real files under the root tree with
matching version timestamps. `alphaveda/supabase/migrations/`'s remaining files (e.g. `0018`)
were copied into the root tree under their real recorded timestamp rather than left orphaned.

## Consequences

- `supabase migration list` shows full local/remote parity (22/22 versions matched) as of this
  ADR — verified live, not asserted.
- `deploy-parity-check.yml` passes green for the first time (run `30555334025`); GHA issue #5
  closed with evidence.
- A real regression was found and fixed during the same diagnosis: 3 tables
  (`bt_backtest_attribution`, `bt_backtest_runs`, `prediction_components`) had RLS disabled,
  created after the original blanket RLS-enable migration ran and never re-covered.
- Going forward, any new migration must use `supabase migration new <name>` (root tree, correct
  timestamp naming) — not the `alphaveda/supabase/migrations/` sequential-number convention, which
  is now deprecated in favor of the canonical tree.

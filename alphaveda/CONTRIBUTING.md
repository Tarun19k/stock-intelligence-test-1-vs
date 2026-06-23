# AlphaVeda — Contributing & Quality Rules

## Isolation Rule
AlphaVeda code lives entirely inside `alphaveda/`. No file in `alphaveda/` may import from the
workspace root (GSI app). No GSI file may import from `alphaveda/`. The only shared resource is
`supabase/migrations/` (schema source of truth) and the workspace `.env` (read-only credentials).

## Quality Rule 1 — Test Before Implementation (TDD)
Every module file must have a test file written and committed BEFORE the implementation:

1. Write `alphaveda/tests/test_<module>.py` with all test function stubs
2. Run `pytest alphaveda/tests/test_<module>.py` → confirm RED (ImportError or AssertionError)
3. Write `alphaveda/src/<path>/<module>.py` implementation
4. Run pytest → fix until GREEN
5. Declare module complete only when `pytest alphaveda/tests/test_<module>.py` passes

## Quality Rule 2 — GSI Regression Must Stay Green
After every commit that touches `alphaveda/`:
```bash
cd /path/to/workspace && python3 regression.py
```
AlphaVeda changes must never break the GSI 480/480 baseline.
If regression breaks: revert the AlphaVeda commit, identify the import/path collision, fix, re-commit.

## Quality Rule 3 — Migration Verify Before Code
Before writing any Python that reads from or writes to Supabase:
```bash
# Check all 13 AlphaVeda tables exist
python3 alphaveda/scripts/verify_migrations.py
```
If any table is missing, apply the missing migration via Supabase dashboard SQL editor before proceeding.
Supabase project: kowlkczswaglbmabygtl (ap-south-1). Credentials: workspace .env.

## Agent-Builder Feedback Loop
For each Phase, a build agent is dispatched with this contract:
1. Read the module spec from the design doc (Section 2–6)
2. Write test file FIRST (RED)
3. Write implementation file
4. Run pytest — fix all failures
5. Run regression.py — confirm GSI is GREEN
6. Report: module path + N tests passing + regression status

CoS signs off each Phase before the next begins. No Phase starts on a RED prior Phase.

## File Inventory
Current tracked files: see `alphaveda/FILE_INVENTORY.md` (updated by housekeeping after each Phase).

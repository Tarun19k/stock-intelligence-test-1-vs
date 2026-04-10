---
paths:
  - "requirements.txt"
---

# Scoped Rules — requirements.txt

These rules activate automatically when editing `requirements.txt`.

## Mandatory: update GSI_DEPENDENCIES.md

Every change to `requirements.txt` (add, remove, or version change) **must** be accompanied by a GSI_DEPENDENCIES.md update in the same sprint.

compliance_check.py C9 checks this mechanically: if `git log -1` date of requirements.txt > date of GSI_DEPENDENCIES.md, the pre-push gate fails.

## When adding a new package

1. Add to requirements.txt (pinned version or >=constraint with comment)
2. Add a new `CONSTRAINT-NNN` entry to GSI_DEPENDENCIES.md:
   - Package name, constraint type, symptom/reason, date, status: ACTIVE
   - Include: what it does, known conflicts, upgrade risks
3. If the package has compatibility constraints with existing deps (e.g. streamlit pandas<3 rule), note them explicitly

## When upgrading a package

1. Check GSI_DEPENDENCIES.md for any ACTIVE constraints on that package first
2. If upgrading past a constraint boundary, mark the old constraint RESOLVED
3. Document why the upgrade is safe (tested version, what was verified)
4. Run full regression suite after any upgrade

## Known risky packages (read GSI_DEPENDENCIES.md before touching)

- `streamlit` — CSS selectors break on minor versions (CONSTRAINT-002)
- `yfinance` — MultiIndex structure changes between versions (CONSTRAINT-003)
- `pandas` — streamlit==1.55.0 metadata declares pandas<3; don't pin >=3.0.0 (CONSTRAINT-001)
- `cvxpy` — solver backend changes in 1.8.x; test portfolio optimiser (CONSTRAINT-007)

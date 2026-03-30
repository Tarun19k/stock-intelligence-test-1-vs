---
description: Start a new GSI Dashboard development session — reads all context files, confirms regression baseline, and summarises open items ready to work on.
---

Read the following files fully before doing anything else:
1. `CLAUDE.md` — architecture reference, DO NOT UNDO rules, open items
2. `GSI_GOVERNANCE.md` — 7 policies that govern all development

Then run:
```bash
python3 regression.py
```

Confirm the output is `ALL 378 CHECKS PASS` (or the current baseline in CLAUDE.md).

Then read `GSI_session.json` and report:
- Current app version
- Regression baseline
- Last session summary (1 sentence)
- All OPEN items sorted by priority (HIGH first)
- Any pending pushes listed in the last session

Finally, ask: **"What would you like to work on this session?"**

Do not write any code or make any changes until the user responds.

# GSI Dashboard — Snapshot Question Set
# ════════════════════════════════════════════════════════════════════════
#
# PURPOSE: Defines the fixed probes Claude uses to write each session's
# understanding snapshot. Questions are stable IDs pointing at source
# files. When the application changes, update the source pointer — not
# the historical snapshot answers.
#
# SEPARATION OF CONCERNS:
#   This file  = WHAT to ask and WHERE to look (probe definitions)
#   GSI_SESSION_SNAPSHOT.md = WHAT Claude extracted (answers per session)
#
# RULES:
#   1. Questions are never deleted — only RETIRED (with reason + date).
#   2. Adding a question: append with next Q-number, note QSet version.
#   3. Retiring a question: mark RETIRED inline, do not remove the line.
#   4. When a question's source file changes, update the Source field.
#      This is NOT a version bump — just a pointer correction.
#   5. A version bump is required when questions are ADDED or RETIRED.
#   6. Each question has a TRIGGER — the condition that would make this
#      question need review or retirement. Check triggers during Phase 3.
#
# HOW CLAUDE USES THIS FILE:
#   At session start (Step 4 of /new-session), Claude reads this file,
#   reads each question's source files, extracts the answer, and writes
#   it to GSI_SESSION_SNAPSHOT.md. Claude does NOT answer from memory —
#   every answer must be traced to a source file read in this session.
#
# VERSION LOG:
#   QSet-v1 | 2026-04-01 | session_013 | 10 questions (Q01–Q10)
#
# ════════════════════════════════════════════════════════════════════════

## Current Question Set: QSet-v1 (2026-04-01)

---

### Q01 — Regression baseline
**Status:** ACTIVE
**Source:** Run `python3 regression.py`; read CLAUDE.md "Current State" section
**Extract:** The exact integer count of passing checks AND its composition (how many are structural, R26, R27-permanent vs R27-active)
**Trigger for review:** Any sprint that adds or removes regression checks (i.e., any sprint touching regression.py)

---

### Q02 — R27 enforcement scope
**Status:** ACTIVE
**Source:** regression.py R27 block (search for `# R27`); GSI_SPRINT_MANIFEST.json `status` field
**Extract:** What R27 enforces, and the exact condition that activates vs. deactivates its content checks
**Trigger for review:** Any change to the sprint manifest system or R27 logic

---

### Q03 — yfinance import restriction
**Status:** ACTIVE
**Source:** regression.py R3 block (search for `# R3`); CLAUDE.md File Structure section
**Extract:** Which files are banned from importing yfinance, which file is the sole permitted importer, and which regression check enforces this
**Trigger for review:** Any new module added to the project

---

### Q04 — DataManager bypass mode
**Status:** ACTIVE — RETIRE when OPEN-007 (M4) ships
**Source:** CLAUDE.md DataManager section; data_manager.py module docstring or class comment; CLAUDE.md Open Items
**Extract:** Current M-level, what "bypass mode" means operationally, which pages are affected, which check enforces it
**Trigger for review:** When OPEN-007 M4 is implemented — this question's answer will change fundamentally and must be re-anchored

---

### Q05 — Signal arbitration hierarchy
**Status:** ACTIVE
**Source:** CLAUDE.md Governance Policy 6; indicators.py `compute_unified_verdict()`; GSI_DECISIONS.md (search for "arbitration" or "Weinstein")
**Extract:** The full precedence order (which signal wins when), whether the veto must be disclosed in UI, and where in the code this is enforced
**Trigger for review:** Any change to `compute_unified_verdict()` or Policy 6

---

### Q06 — M3 routing guard
**Status:** ACTIVE
**Source:** ADR-007 in GSI_DECISIONS.md; app.py (search for `grp_explicitly_selected`); regression.py R22 block
**Extract:** What the guard prevents, the session_state key name, and what regression check enforces it
**Trigger for review:** Any change to app.py routing logic or group overview rendering

---

### Q07 — DO NOT UNDO rule 12
**Status:** ACTIVE
**Source:** CLAUDE.md "DO NOT UNDO" list rule 12; dashboard.py `_render_header_static()` (confirm raw score absent); ADR-008
**Extract:** What is prohibited, where the score IS permitted, and the ADR that made this decision final
**Trigger for review:** Any new DO NOT UNDO rule added (Q07 stays anchored to rule 12; new rules get new questions)

---

### Q08 — Permanent Tier A manifest checks
**Status:** ACTIVE
**Source:** CLAUDE.md Rule 2 "Permanent Tier A checks" block
**Extract:** All 5 check IDs and what each verifies. If fewer or more than 5 exist, that itself is a deviation.
**Trigger for review:** Any sprint that adds or removes a Permanent Tier A check

---

### Q09 — Current sprint and pending pre-sprint work
**Status:** ACTIVE — answer changes every sprint
**Source:** GSI_WIP.md Session Status block; GSI_SPRINT.md (current sprint section)
**Extract:** Sprint version, status (COMPLETE / IN_PROGRESS), and any pending infrastructure tasks that must run before the next sprint begins
**Trigger for review:** Never — this question's answer is expected to change every sprint. Differences are always UPDATED, not DEVIATION.

---

### Q10 — Pre-push gate
**Status:** ACTIVE
**Source:** CLAUDE.md Run Commands section; CLAUDE.md "Before every commit" line; GSI_COMPLIANCE_CHECKLIST.md preamble
**Extract:** Both commands required before push (regression + compliance), and why compliance can catch violations that regression alone misses
**Trigger for review:** Any change to the compliance script or pre-push protocol

---

## How to add a new question

When a new architectural invariant is introduced (new DO NOT UNDO rule, new ADR with
ongoing enforcement, new module boundary, new deployment constraint), add a probe:

```
### Q[NN] — [short title]
**Status:** ACTIVE
**Source:** [file(s) to read — be specific: function name, section heading, search term]
**Extract:** [exactly what Claude should pull out — a fact, a rule, a number, a hierarchy]
**Trigger for review:** [the condition that means this question needs updating or retiring]
```

Then:
1. Bump the QSet version in the VERSION LOG above (QSet-v2, date, session, question count)
2. Update the snapshot block header in GSI_SESSION_SNAPSHOT.md to reference the new QSet version
3. Note in the next snapshot: "Q[NN]: first answer — no prior comparison available"

## How to retire a question

When an invariant no longer exists (milestone shipped, rule removed, module deleted):

1. Change `**Status:** ACTIVE` to `**Status:** RETIRED — [reason] ([date])`
2. Bump QSet version
3. Future sessions skip RETIRED questions
4. Historical snapshots that answered it remain valid and readable

## Trigger review checklist (run during Phase 3 close)

Before closing a sprint, scan this list:
- [ ] Was regression.py modified? → Review Q01, Q02
- [ ] Was a new .py module added? → Review Q03
- [ ] Did OPEN-007 M4 ship? → Retire Q04, write replacement
- [ ] Was `compute_unified_verdict()` or Policy 6 changed? → Review Q05
- [ ] Was app.py routing changed? → Review Q06
- [ ] Was a DO NOT UNDO rule added or removed? → Add new question or retire old one
- [ ] Did Permanent Tier A checks change? → Review Q08
- [ ] Did the pre-push protocol change? → Review Q10

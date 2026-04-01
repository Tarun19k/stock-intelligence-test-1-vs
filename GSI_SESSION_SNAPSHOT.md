# GSI Dashboard — Session Understanding Snapshots
# ════════════════════════════════════════════════════════════════════════
#
# PURPOSE: Each session, Claude answers a fixed set of questions about
# the system AFTER reading all context files. The next session reads the
# previous answers and writes new ones. Differences = deviations to
# investigate before any code is written.
#
# This catches SEMANTIC DRIFT — where Claude reads the same files but
# extracts different meanings, silently corrupting decisions downstream.
# It is distinct from GSI_SESSION_LEARNINGS.md (which tracks stale docs).
#
# RULES:
#   1. Claude writes a snapshot block at the START of every session,
#      AFTER reading GSI_WIP.md, CLAUDE.md, and GSI_CONTEXT.md.
#   2. Questions come from GSI_SNAPSHOT_QUESTIONS.md (active, non-retired).
#      Do NOT answer from memory — trace every answer to a source file.
#   3. Claude reads the PREVIOUS block before writing the new one.
#   4. Any answer that differs meaningfully from the previous session's
#      answer is a DEVIATION — log it in GSI_SESSION_LEARNINGS.md as
#      type DEVIATION before starting any implementation work.
#   5. Legitimate changes (e.g. baseline incremented, sprint changed)
#      are NOT deviations — note them as UPDATED.
#   6. Append only. Never edit a previous block.
#   7. Each block header records the QSet version used (from
#      GSI_SNAPSHOT_QUESTIONS.md VERSION LOG). If QSet version changed,
#      note which questions are new (no prior comparison) and which
#      were retired (skip comparison for those).
#
# DEVIATION vs UPDATED:
#   DEVIATION — the same fact is described differently, incompletely, or
#               contradictorily. Investigate the discrepancy before coding.
#   UPDATED   — a value legitimately changed (new baseline, sprint closed,
#               new rule added). No investigation needed, just log it.
#   NEW       — question added this session (QSet version bumped).
#               No prior answer exists; first comparison will be next session.
#
# To change the question set: edit GSI_SNAPSHOT_QUESTIONS.md, not this file.
# ════════════════════════════════════════════════════════════════════════

---

## SNAPSHOT-001 | 2026-04-01 | session_013 | v5.34 | QSet-v1
*Seed snapshot — written at session close. No prior block to compare against. All future sessions compare against the previous block.*

**Q1. Regression baseline:**
427. Composed of: 415 structural checks + 5 R26 permanent observability checks + 7 R27 checks that run regardless of manifest status (manifest_valid_json + per-file change_log_complete gates). R27 content checks (Tier A/B must_contain) only run when manifest status == IN_PROGRESS.

**Q2. R27 enforcement and activation:**
R27 enforces the GSI_SPRINT_MANIFEST.json living manifest. It checks: (a) every file committed during a sprint is listed in file_change_log, and (b) Tier A/Tier B must_contain strings appear in their target files. R27 content checks are ONLY active when manifest status == "IN_PROGRESS". When status is COMPLETE or manifest is absent, only the structural JSON validity and change_log_complete checks run (7 checks, always-on).

**Q3. yfinance import restriction:**
Only market_data.py may import yfinance. All other files — pages, indicators, forecast, portfolio, app.py — are banned from importing yfinance directly. R3 regression check enforces this.

**Q4. DataManager bypass mode:**
DataManager (data_manager.py) M1 skeleton exists but is in BYPASS MODE until M4 is implemented. Pages must NOT call DataManager.fetch() until M4. The bypass mode means pages call market_data.py functions directly as before. DataManager.fetch() is blocked in pages by R24 regression check.

**Q5. Signal arbitration hierarchy:**
Weinstein Stage overrides Elder screens when they conflict. The hierarchy is: Weinstein Stage > Elder Triple Screen > raw signal score. A Weinstein Stage 4 (distribution/decline) vetoes a BUY from Elder. The veto must be visibly disclosed in the UI. Documented in ADR-006 (indirectly) and enforced by Policy 6.

**Q6. M3 routing guard (grp_explicitly_selected):**
A session_state flag set only when the user explicitly clicks a market group. It gates the group overview render so that yfinance batch downloads for 49 tickers do NOT fire on cold start or page reload. Without this guard, every cold start would trigger a 49-ticker batch, causing rate limit spirals. DO NOT remove — R22 regression check enforces it.

**Q7. DO NOT UNDO rule 12:**
Do NOT display the raw Momentum score (X/100) in the dashboard header (_render_header_static()). Option B is final: verdict badge + plain-English reason only. The score is visible in the "Momentum Signal Panel" KPI section below the header. Root cause: score 59/100 appearing alongside WATCH verdict confused users (59 is in BUY territory).

**Q8. Five Permanent Tier A manifest checks:**
Every sprint manifest must include these 5 checks regardless of sprint content:
1. sync_docs_passes — python3 sync_docs.py exits 0 (covers CHANGELOG/README/AGENTS auto-sync)
2. compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"
3. pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"
4. decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"
5. qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}"
These were added in CLAUDE.md Rule 2 step 4 after the session_013 post-mortem revealed 7 missed files.

**Q9. Current sprint and status:**
v5.34 — COMPLETE (2026-04-01). All phases done. GSI_SPRINT_MANIFEST_v5.34.json archived. Next sprint is v5.35. Before v5.35 sprint items begin, session_014 must implement the session_013 infrastructure fix (CLAUDE.md Rule 2 Permanent Tier A + Phase 3 sync_docs step) — documented in GSI_WIP.md pending infrastructure block.

**Q10. Single most important check before push:**
python3 regression.py (all 427 checks must pass) AND python3 -c "..." compliance script (8/8 gates: SEBI disclaimer, algo disclosure, no raw score, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate). Both must pass. Compliance failures have been found as pre-existing violations even when regression passed.

---

## How to write a new snapshot block

```
## SNAPSHOT-[NNN] | [YYYY-MM-DD] | [session_NNN] | [vX.XX]
*Compared to SNAPSHOT-[NNN-1]. Deviations: [list or "none"]. Updated values: [list or "none"].*

**Q1. Regression baseline:** [exact number + composition]
**Q2. R27 enforcement and activation:** [when active, what it checks]
**Q3. yfinance import restriction:** [which files banned, which check enforces]
**Q4. DataManager bypass mode:** [current M-level, what is blocked, which check]
**Q5. Signal arbitration hierarchy:** [order of precedence, veto disclosure rule]
**Q6. M3 routing guard (grp_explicitly_selected):** [what it prevents, which check]
**Q7. DO NOT UNDO rule 12:** [what is prohibited, where score IS allowed]
**Q8. Five Permanent Tier A manifest checks:** [all 5, with their IDs]
**Q9. Current sprint and status:** [sprint version, status, any pending pre-sprint tasks]
**Q10. Single most important check before push:** [both commands, why compliance can catch what regression misses]
```

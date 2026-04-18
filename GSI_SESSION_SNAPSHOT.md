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

## SNAPSHOT-002 | 2026-04-06 | session_017 | v5.34.2 | QSet-v1
*Compared to SNAPSHOT-001 (QSet-v1). Deviations: none. Updated: Q01 (baseline 427→432), Q09 (sprint advanced to v5.35), Q10 (compliance now compliance_check.py script). New questions: none.*

**Q01. Regression baseline:** 432/432 PASS. Confirmed by running python3 regression.py this session. Composition: 422 structural/contract checks + 5 R26 observability checks + 5 R28 hook infrastructure checks. R27 content checks inactive (manifest status = COMPLETE for v5.34.2). Always-on R27 structural checks (manifest_valid_json, change_log_complete) included in the 432 total.

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is COMPLETE (v5.34.2), so Tier A/B must_contain content checks are inactive. Only structural checks (valid JSON, change_log_complete per-file gates) run — these are always-on regardless of manifest status. Content checks reactivate when status = "IN_PROGRESS" at start of next sprint.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules (pages, indicators, forecast, portfolio, app.py) are banned. R3 regression check enforces this. Unchanged from SNAPSHOT-001.

**Q04. DataManager bypass mode:** DataManager M1 skeleton exists in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007). Pages must NOT call DataManager.fetch() — they call market_data.py functions directly. R24 regression check enforces the bypass. Unchanged from SNAPSHOT-001.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 (distribution/decline) vetoes a BUY from Elder screens. Veto must be visibly disclosed in the UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-001.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user click of a market group. Gates 49-ticker batch download to prevent rate limit spirals on cold start/reload. DO NOT remove. R22 regression check enforces it. Unchanged from SNAPSHOT-001.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score is permitted in the KPI "Momentum Signal Panel" section below the header. ADR-008 is the final record. Unchanged from SNAPSHOT-001.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes — python3 sync_docs.py exits 0; (2) compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"; (3) pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"; (4) decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"; (5) qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}". Unchanged from SNAPSHOT-001.

**Q09. Current sprint and status:** v5.34.2 COMPLETE (2026-04-05). Current sprint is v5.35 — Launch Readiness, status: Planning (sign-offs complete, ready to execute). No pending pre-sprint infrastructure tasks — GSI_WIP.md is IDLE. UPDATED from SNAPSHOT-001 (was v5.34 COMPLETE → v5.35 Planning).

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — all 432 checks must pass; (2) python3 compliance_check.py — 8/8 gates (SEBI disclaimer, algo disclosure, no raw score, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate). As of v5.34.1, compliance_check.py is a dedicated script (extracted from the inline python3 -c block). UPDATED from SNAPSHOT-001 (compliance now runs via compliance_check.py, not inline).

---

## SNAPSHOT-003 | 2026-04-07 | session_018 | v5.35.1 | QSet-v1
*Compared to SNAPSHOT-002 (QSet-v1). Deviations: none. Updated: Q01 (baseline 432→434), Q09 (v5.35.1 COMPLETE, v5.36 Planning). New questions: none.*

**Q01. Regression baseline:** 434/434 PASS. Confirmed by running python3 regression.py this session. Composition: structural/contract checks + R26 (5) + R28 (5) + R29 (1) + R10b extended. R27 content checks inactive (manifest status = COMPLETE for v5.35.1). UPDATED from SNAPSHOT-002 (was 432 — R10b extended 433→434 added in v5.35.1 governance patch).

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is COMPLETE (v5.35.1), so Tier A/B must_contain content checks are inactive. Only structural checks (valid JSON, change_log_complete per-file gates) run — always-on regardless of manifest status. Content checks reactivate when status = "IN_PROGRESS" at sprint start. Unchanged from SNAPSHOT-002.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules (pages, indicators, forecast, portfolio, app.py) are banned. R3 regression check enforces this. Unchanged from SNAPSHOT-002.

**Q04. DataManager bypass mode:** DataManager M1 skeleton exists in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages must NOT call DataManager.fetch() — they call market_data.py functions directly. R24 regression check enforces the bypass. Unchanged from SNAPSHOT-002.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 (distribution/decline) vetoes a BUY from Elder screens. Stage 1/3 forces WATCH. Veto must be visibly disclosed in the UI as "⚠️ Stage override applied" (Policy 6, OPEN-012). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-002.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user click of a market group. Gates 49-ticker batch download to prevent rate limit spirals on cold start/reload. Resets to False on market switch (_on_market_change). DO NOT remove. R22 regression check enforces it. Unchanged from SNAPSHOT-002.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in the KPI "Momentum Signal Panel" section below the header and in _tab_insights (~line 948). ADR-008 is the final record. Unchanged from SNAPSHOT-002.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes — python3 sync_docs.py exits 0; (2) compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"; (3) pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"; (4) decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"; (5) qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}". Unchanged from SNAPSHOT-002.

**Q09. Current sprint and status:** v5.35.1 COMPLETE (2026-04-06). Current sprint is v5.36 — Post-Launch Hardening, status: Planning (backlog candidates defined, nothing in progress). No pending pre-sprint infrastructure tasks — GSI_WIP.md is IDLE. UPDATED from SNAPSHOT-002 (was v5.35 Planning → v5.35.1 COMPLETE, v5.36 Planning).

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — all 434 checks must pass; (2) python3 compliance_check.py — 8/8 gates (SEBI disclaimer, algo disclosure, no raw score in header, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate). compliance_check.py is the dedicated script (extracted v5.34.1). Unchanged from SNAPSHOT-002.

---

## SNAPSHOT-005 | 2026-04-07 | session_020 | v5.36 | QSet-v1
*Compared to SNAPSHOT-004 (QSet-v1). Deviations: none. Updated: Q09 (v5.36 now COMPLETE; was Planning). New questions: none.*

**Q01. Regression baseline:** 434/434 PASS. Confirmed by running python3 regression.py this session. Composition: structural/contract checks + R26 (5) + R28 (5) + R29 (1) + R10b extended. R27 content checks inactive (manifest status = COMPLETE for v5.36). Unchanged from SNAPSHOT-004.

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is COMPLETE (v5.36), so Tier A/B must_contain content checks are inactive. Only structural checks (valid JSON, change_log_complete per-file gates) run — always-on regardless of manifest status. Content checks reactivate when status = "IN_PROGRESS" at sprint start. Unchanged from SNAPSHOT-004.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules (pages, indicators, forecast, portfolio, app.py) are banned. R3 regression check enforces this. Unchanged from SNAPSHOT-004.

**Q04. DataManager bypass mode:** DataManager M1 skeleton exists in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages must NOT call DataManager.fetch() — they call market_data.py functions directly. R24 regression check enforces the bypass. Unchanged from SNAPSHOT-004.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 (distribution/decline) vetoes a BUY from Elder screens. Stage 1/3 forces WATCH. Veto must be visibly disclosed in the UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-004.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user click of a market group. Gates 49-ticker batch download to prevent rate limit spirals on cold start/reload. Resets to False on market switch. DO NOT remove. R22 regression check enforces it. Unchanged from SNAPSHOT-004.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in the KPI "Momentum Signal Panel" section and in _tab_insights. ADR-008 is the final record. Unchanged from SNAPSHOT-004.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes — python3 sync_docs.py exits 0; (2) compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"; (3) pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"; (4) decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"; (5) qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}". Unchanged from SNAPSHOT-004.

**Q09. Current sprint and status:** v5.36 — Post-Launch Hardening, COMPLETE (2026-04-07). Next sprint is v5.37. No pending pre-sprint infrastructure tasks — GSI_WIP.md is IDLE. UPDATED from SNAPSHOT-004 (was Planning → now COMPLETE; v5.36 done items: PROXY-01–07, D-02, OPEN-006, EQA-41).

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — all 434 checks must pass; (2) python3 compliance_check.py — 8/8 gates (SEBI disclaimer, algo disclosure, no raw score in header, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate). compliance_check.py is the dedicated script (extracted v5.34.1). Unchanged from SNAPSHOT-004.

---

## SNAPSHOT-006 | 2026-04-07 | session_020 (post-/clear) | v5.36 | QSet-v1
*Compared to SNAPSHOT-005 (QSet-v1). Deviations: none. Updated: none. New questions: none. Note: continuation of session_020 after /clear; no code written between SNAPSHOT-005 and this block.*

**Q01. Regression baseline:** 434/434 PASS. Confirmed by running python3 regression.py this session. Composition: structural/contract checks + R26 (5) + R28 (5) + R29 (1) + R10b extended. R27 content checks inactive (manifest status = COMPLETE for v5.36). Unchanged from SNAPSHOT-005.

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is COMPLETE (v5.36), so Tier A/B must_contain content checks are inactive. Only structural checks (valid JSON, change_log_complete per-file gates) run — always-on regardless of manifest status. Content checks reactivate when status = "IN_PROGRESS" at sprint start. Unchanged from SNAPSHOT-005.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules (pages, indicators, forecast, portfolio, app.py) are banned. R3 regression check enforces this. Unchanged from SNAPSHOT-005.

**Q04. DataManager bypass mode:** DataManager M1 skeleton exists in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages must NOT call DataManager.fetch() — they call market_data.py functions directly. R24 regression check enforces the bypass. Unchanged from SNAPSHOT-005.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 (distribution/decline) vetoes a BUY from Elder screens. Stage 1/3 forces WATCH. Veto must be visibly disclosed in the UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-005.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user click of a market group. Gates 49-ticker batch download to prevent rate limit spirals on cold start/reload. Resets to False on market switch. DO NOT remove. R22 regression check enforces it. Unchanged from SNAPSHOT-005.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in the KPI "Momentum Signal Panel" section and in _tab_insights. ADR-008 is the final record. Unchanged from SNAPSHOT-005.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes — python3 sync_docs.py exits 0; (2) compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"; (3) pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"; (4) decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"; (5) qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}". Unchanged from SNAPSHOT-005.

**Q09. Current sprint and status:** v5.36 — Post-Launch Hardening, COMPLETE (2026-04-07). Next sprint is v5.37 — NOT STARTED. No pending pre-sprint infrastructure tasks — GSI_WIP.md is IDLE. Unchanged from SNAPSHOT-005.

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — all 434 checks must pass; (2) python3 compliance_check.py — 8/8 gates (SEBI disclaimer, algo disclosure, no raw score in header, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate). compliance_check.py is the dedicated script (extracted v5.34.1). Unchanged from SNAPSHOT-005.

---

## SNAPSHOT-007 | 2026-04-09 | session_022 | v5.36 | QSet-v1
*Compared to SNAPSHOT-006 (QSet-v1). Deviations: none. Updated: Q09 (v5.37 moved from "NOT STARTED" to "Planning" with draft item specs committed 2026-04-08). New questions: none.*

**Q01. Regression baseline:** 434/434 PASS. Confirmed by running `python3 regression.py` this session. Composition: structural/contract checks + R26 (5) + R28 (5) + R29 (1) + R10b extended. R27 content checks inactive (manifest status = COMPLETE for v5.36). Unchanged from SNAPSHOT-006.

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is COMPLETE (v5.36), so Tier A/B must_contain content checks are inactive. Only structural checks (valid JSON, change_log_complete per-file gates) run — always-on regardless of manifest status. Content checks reactivate when status = "IN_PROGRESS" at sprint start. Unchanged from SNAPSHOT-006.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules (pages, indicators, forecast, portfolio, app.py) are banned. R3 regression check enforces this. Unchanged from SNAPSHOT-006.

**Q04. DataManager bypass mode:** DataManager M1 skeleton exists in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages must NOT call DataManager.fetch() — they call market_data.py functions directly. R24 regression check enforces the bypass. Unchanged from SNAPSHOT-006.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 (distribution/decline) vetoes a BUY from Elder screens. Stage 1/3 forces WATCH. Veto must be visibly disclosed in the UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-006.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user click of a market group. Gates 49-ticker batch download to prevent rate limit spirals on cold start/reload. Resets to False on market switch. DO NOT remove. R22 regression check enforces it. Unchanged from SNAPSHOT-006.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in the KPI "Momentum Signal Panel" section and in _tab_insights. ADR-008 is the final record. Unchanged from SNAPSHOT-006.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes — python3 sync_docs.py exits 0; (2) compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"; (3) pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"; (4) decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"; (5) qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}". Unchanged from SNAPSHOT-006.

**Q09. Current sprint and status:** v5.37 — Planning. Draft item specifications committed 2026-04-08 (session_021): v5.37a (SEBI Compliance: OPEN-022, OPEN-027, OPEN-028, OPEN-029) + v5.37b (Governance/Proxy: ALERT-01, HOOK-01, PROXY-08+OPEN-023, QUANT-01, OPEN-024, OPEN-025+OPEN-026). Sprint not yet locked — pending this session's review. No pending pre-sprint infrastructure tasks — GSI_WIP.md is IDLE. UPDATED from SNAPSHOT-006 (was "NOT STARTED" → now "Planning" with draft items).

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — all 434 checks must pass; (2) python3 compliance_check.py — 8/8 gates (SEBI disclaimer, algo disclosure, no raw score in header, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate). compliance_check.py is the dedicated script (extracted v5.34.1). Unchanged from SNAPSHOT-006.

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

---

## SNAPSHOT-004 | 2026-04-07 | session_019 | v5.35.1 | QSet-v1
*Compared to SNAPSHOT-003 (QSet-v1). Deviations: none. Updated: none. New questions: none.*

**Q01. Regression baseline:** 434/434 PASS. Confirmed by running python3 regression.py this session. R27 content checks inactive (manifest status = COMPLETE for v5.35). Unchanged from SNAPSHOT-003.

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is COMPLETE (v5.35), so Tier A/B must_contain content checks are inactive. Only structural checks (valid JSON, change_log_complete per-file gates) run — always-on regardless of manifest status. Content checks reactivate when status = "IN_PROGRESS" at sprint start. Unchanged from SNAPSHOT-003.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules (pages, indicators, forecast, portfolio, app.py) are banned. R3 regression check enforces this. Unchanged from SNAPSHOT-003.

**Q04. DataManager bypass mode:** DataManager M1 skeleton exists in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages must NOT call DataManager.fetch() — they call market_data.py functions directly. R24 regression check enforces the bypass. Unchanged from SNAPSHOT-003.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 (distribution/decline) vetoes a BUY from Elder screens. Stage 1/3 forces WATCH. Veto must be visibly disclosed in the UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-003.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user click of a market group. Gates 49-ticker batch download to prevent rate limit spirals on cold start/reload. Resets to False on market switch. DO NOT remove. R22 regression check enforces it. Unchanged from SNAPSHOT-003.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in the KPI "Momentum Signal Panel" section and in _tab_insights. ADR-008 is the final record. Unchanged from SNAPSHOT-003.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes — python3 sync_docs.py exits 0; (2) compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"; (3) pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"; (4) decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"; (5) qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}". Unchanged from SNAPSHOT-003.

**Q09. Current sprint and status:** v5.36 — Post-Launch Hardening, status: Planning (backlog defined, nothing in progress). No pending pre-sprint infrastructure tasks — GSI_WIP.md is IDLE. Unchanged from SNAPSHOT-003.

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — all 434 checks must pass; (2) python3 compliance_check.py — 8/8 gates (SEBI disclaimer, algo disclosure, no raw score in header, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate). compliance_check.py is the dedicated script (extracted v5.34.1). Unchanged from SNAPSHOT-003.

## SNAPSHOT-008 | 2026-04-11 | session_023 | v5.36 | QSet-v1
*Compared to SNAPSHOT-007 (QSet-v1). Deviations: none. Updated: Q01 (baseline 434→436), Q02 (manifest now PLANNING for v5.37), Q09 (prereq governance work complete), Q10 (compliance 8→9 checks). New questions: none.*

**Q01. Regression baseline:** 436/436 PASS. Confirmed this session. New checks: R28+2 (rules_sprint_manifest_exists, rules_dependencies_exists), R30 (model/mode completeness — fires IN_PROGRESS), R31 (PLAYWRIGHT-ID coverage — fires IN_PROGRESS/COMPLETE), R32 (log-learnings enforcement — fires COMPLETE). UPDATED from SNAPSHOT-007 (was 434/434).

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is PLANNING (v5.37), so all dynamic checks (R27 content, R30, R31, R32) are inactive — 0 additional checks fire. They reactivate when status → IN_PROGRESS at sprint open. R28 (hook/rules existence) always-on regardless of status. UPDATED from SNAPSHOT-007 (status was COMPLETE for v5.36, now PLANNING for v5.37).

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules (pages, indicators, forecast, portfolio, app.py) are banned. R3 regression check enforces this. Unchanged from SNAPSHOT-007.

**Q04. DataManager bypass mode:** DataManager M1 skeleton exists in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages must NOT call DataManager.fetch() — they call market_data.py functions directly. R24 regression check enforces the bypass. Unchanged from SNAPSHOT-007.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 (distribution/decline) vetoes a BUY from Elder screens. Stage 1/3 forces WATCH. Veto must be visibly disclosed in the UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-007.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user click of a market group. Gates 49-ticker batch download to prevent rate limit spirals on cold start/reload. Resets to False on market switch. DO NOT remove. R22 regression check enforces it. Unchanged from SNAPSHOT-007.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in the KPI "Momentum Signal Panel" section and in _tab_insights. ADR-008 is the final record. Unchanged from SNAPSHOT-007.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes — python3 sync_docs.py exits 0; (2) compliance_baseline_current — GSI_COMPLIANCE_CHECKLIST.md contains "ALL {N} CHECKS PASS"; (3) pr_template_baseline_current — .github/PULL_REQUEST_TEMPLATE.md contains "ALL {N} CHECKS PASS"; (4) decisions_has_sprint_adr — GSI_DECISIONS.md contains "v{sprint_version}"; (5) qa_standards_has_brief — GSI_QA_STANDARDS.md contains "v{sprint_version}". Unchanged from SNAPSHOT-007.

**Q09. Current sprint and status:** v5.37 — PLANNING. Prereq governance wiring complete and committed (7ed98b7, 6dcb58c): R30/R31/R32/C9 hard gates, .claude/rules/ scoped files, new-session/sprint-review/ui-test command rewrites, docs/ai-ops/ knowledge base, CLAUDE.md consolidation (DO NOT UNDO 16-17, anti-patterns, failure classes). GSI_WIP.md is IDLE. Sprint execution NOT yet started — ready to open v5.37 next session. UPDATED from SNAPSHOT-007.

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — all 436 checks must pass; (2) python3 compliance_check.py — 9/9 gates (SEBI disclaimer, algo disclosure, no raw score in header, no red flags fallback, ROE guard, next steps removed, RATES CONTEXT, rate limit gate, deps doc current). UPDATED from SNAPSHOT-007 (was 434/8 → now 436/9).

---

## SNAPSHOT-009 | 2026-04-12 | session_024 | v5.36 | QSet-v1
*Compared to SNAPSHOT-008 (QSet-v1). Deviations: none. Updated: none. New questions: none.*

**Q01. Regression baseline:** 436/436 PASS. Confirmed this session. Unchanged from SNAPSHOT-008.

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is PLANNING (v5.37), so all dynamic checks (R27 content, R30, R31, R32) are inactive. R28 (hook/rules existence) always-on. Unchanged from SNAPSHOT-008.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules banned. R3 regression check enforces this. Unchanged from SNAPSHOT-008.

**Q04. DataManager bypass mode:** DataManager M1 skeleton in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages call market_data.py directly. R24 enforces bypass. Unchanged from SNAPSHOT-008.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 vetoes BUY from Elder. Stage 1/3 forces WATCH. Veto must be visibly disclosed in UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-008.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user group click. Gates 49-ticker batch download to prevent rate limit spirals. Resets on market switch. R22 enforces it. Unchanged from SNAPSHOT-008.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in KPI panel and _tab_insights. ADR-008 is final record. Unchanged from SNAPSHOT-008.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes; (2) compliance_baseline_current; (3) pr_template_baseline_current; (4) decisions_has_sprint_adr; (5) qa_standards_has_brief. Unchanged from SNAPSHOT-008.

**Q09. Current sprint and status:** v5.37 — PLANNING. Prereq governance wiring complete and committed. GSI_WIP.md is IDLE. Sprint execution not yet started — ready to open v5.37 this session. Unchanged from SNAPSHOT-008.

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — 436 checks pass; (2) python3 compliance_check.py — 9/9 gates confirmed this session. Unchanged from SNAPSHOT-008.

## SNAPSHOT-010 | 2026-04-13 | session_025 | v5.36 | QSet-v1
*Compared to SNAPSHOT-009 (QSet-v1). Deviations: none. Updated: none. New questions: none.*

**Q01. Regression baseline:** 436/436 PASS. Confirmed by running python3 regression.py this session. Unchanged from SNAPSHOT-009.

**Q02. R27 enforcement and activation:** R27 enforces GSI_SPRINT_MANIFEST.json. Current manifest is PLANNING (v5.37), so all dynamic checks (R27 content, R30, R31, R32) are inactive. R28 (hook/rules existence) always-on. Unchanged from SNAPSHOT-009.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules banned. R3 regression check enforces this. Unchanged from SNAPSHOT-009.

**Q04. DataManager bypass mode:** DataManager M1 skeleton in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages call market_data.py directly. R24 enforces bypass. Unchanged from SNAPSHOT-009.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 vetoes BUY from Elder. Stage 1/3 forces WATCH. Veto must be visibly disclosed in UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-009.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user group click. Gates 49-ticker batch download to prevent rate limit spirals. Resets on market switch. R22 enforces it. Unchanged from SNAPSHOT-009.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in KPI panel and _tab_insights. ADR-008 is final record. Unchanged from SNAPSHOT-009.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes; (2) compliance_baseline_current; (3) pr_template_baseline_current; (4) decisions_has_sprint_adr; (5) qa_standards_has_brief. Unchanged from SNAPSHOT-009.

**Q09. Current sprint and status:** v5.37 — PLANNING. Prereq governance wiring complete and committed. GSI_WIP.md is IDLE (session_025 NOT YET STARTED). Ready to execute v5.37 sprint this session. Unchanged from SNAPSHOT-009.

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — 436 checks pass; (2) python3 compliance_check.py — 9/9 gates. Unchanged from SNAPSHOT-009.

## SNAPSHOT-011 | 2026-04-14 | session_026 | v5.37.1 | QSet-v1
*Compared to SNAPSHOT-010 (QSet-v1). Deviations: none. Updated: Q01 (baseline changed), Q09 (sprint complete, new pending items). New questions: none.*

**Q01. Regression baseline:** Last confirmed run: 444/444 PASS (2026-04-14, session_026, during v5.37.1 close sequence while manifest was IN_PROGRESS). With manifest now COMPLETE, R27 content checks (R30/R31/R32) are inactive — expected current baseline: 437/437 (436 stable base + 1 R8 check added by open-026 for compute_stability_score). Next session `python3 regression.py` will confirm. UPDATED from SNAPSHOT-010 (was 436/436).

**Q02. R27 enforcement scope:** R27 enforces GSI_SPRINT_MANIFEST.json completeness. Dynamic content checks (R27 content-level, R30, R31, R32) activate when manifest `status == "IN_PROGRESS"` and deactivate when `status == "COMPLETE"`. R28 (hook/rules file existence) always-on. Current manifest status: COMPLETE. Unchanged from SNAPSHOT-010.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules banned. R3 regression check enforces this. Unchanged from SNAPSHOT-010.

**Q04. DataManager bypass mode:** DataManager M1 skeleton in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages call market_data.py directly. R24 enforces bypass. Unchanged from SNAPSHOT-010.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 vetoes BUY from Elder. Stage 1/3 forces WATCH. Veto must be visibly disclosed in UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-010.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user group click. Gates 49-ticker batch download to prevent rate limit spirals. Resets on market switch. R22 enforces it. Unchanged from SNAPSHOT-010.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in KPI panel. ADR-008 is final record. Unchanged from SNAPSHOT-010.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes; (2) compliance_baseline_current; (3) pr_template_baseline_current; (4) decisions_has_sprint_adr; (5) qa_standards_has_brief. Unchanged from SNAPSHOT-010.

**Q09. Current sprint and status:** v5.37 COMPLETE (including v5.37.1 hotfix, committed 2026-04-14). Next sprint: v5.38 (not yet planned). Pending pre-sprint work: (a) Playwright PLAYWRIGHT-01 through PLAYWRIGHT-06 never run — deferred from v5.37 close, require running Streamlit instance + ui-test skill; (b) quant_audit_pending.json shows pending=true for D3/D5 — false positive from post-edit hook on market_data.py RSS constant edit (not a real quant trigger). GSI_WIP.md Status: IDLE. UPDATED from SNAPSHOT-010.

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py — currently 437 checks expected (436 + open-026 R8 addition); (2) python3 compliance_check.py — 9/9 gates (GSI_COMPLIANCE_CHECKLIST.md shows ALL 436 CHECKS PASS). Note: compliance count reflects last sprint close state. Unchanged from SNAPSHOT-010.

## SNAPSHOT-012 | 2026-04-14 | session_027 | v5.37.1 | QSet-v1
*Compared to SNAPSHOT-011 (QSet-v1). Deviations: none. Updated: Q01 (confirmed 437/437 actual run), Q09 (quant audit flag still pending). New questions: none.*

**Q01. Regression baseline:** Confirmed 437/437 PASS (actual run this session). Composition: 436 stable base + 1 R8 check (compute_stability_score EP, added open-026). CLAUDE.md still shows 436 — minor doc lag; not a functional discrepancy. UPDATED from SNAPSHOT-011 (was "expected 437" → "confirmed 437").

**Q02. R27 enforcement scope:** R27 enforces GSI_SPRINT_MANIFEST.json completeness. Dynamic content checks (R27 content-level, R30, R31, R32) activate when manifest `status == "IN_PROGRESS"` and deactivate when `status == "COMPLETE"`. R28 (hook/rules file existence) always-on. Current manifest status: COMPLETE. Unchanged from SNAPSHOT-011.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules banned. R3 regression check enforces this. Unchanged from SNAPSHOT-011.

**Q04. DataManager bypass mode:** DataManager M1 skeleton in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages call market_data.py directly. R24 enforces bypass. Unchanged from SNAPSHOT-011.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 vetoes BUY from Elder (hard veto → AVOID). Stage 1/3 forces WATCH. Veto must be visibly disclosed in UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Confirmed unchanged — source read this session.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user group click. Gates 49-ticker batch download to prevent rate limit spirals. Resets on market switch. R22 enforces it. Unchanged from SNAPSHOT-011.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in KPI panel. ADR-008 is final record. Unchanged from SNAPSHOT-011.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes; (2) compliance_baseline_current; (3) pr_template_baseline_current; (4) decisions_has_sprint_adr; (5) qa_standards_has_brief. Unchanged from SNAPSHOT-011.

**Q09. Current sprint and status:** v5.37 COMPLETE (v5.37.1 hotfix committed 2026-04-14). Next sprint: v5.38 (not yet planned). Pending pre-sprint work: (a) Playwright PLAYWRIGHT-01 through PLAYWRIGHT-06 never run — deferred, require live Streamlit instance; (b) quant_audit_pending.json pending=true for D3/D5 (last_full_audit 2026-04-13 — within 90 days); previous snapshot assessed as false positive from market_data.py RSS edit. GSI_WIP.md Status: IDLE. UPDATED from SNAPSHOT-011 (quant audit still pending, flag persists into session_027).

**Q10. Pre-push gate:** Two commands required: (1) python3 regression.py (437 checks confirmed); (2) python3 compliance_check.py — 9/9 gates. Unchanged from SNAPSHOT-011.

## SNAPSHOT-013 | 2026-04-14 | session_028 | v5.38 | QSet-v1
*Compared to SNAPSHOT-012 (QSet-v1). Deviations: Q01 (regression 437→446), Q09 (sprint v5.38 now COMPLETE), Q10 (compliance 9→10 gates). Updated: Q01, Q09, Q10. New questions: none.*

**Q01. Regression baseline:** 446/446 PASS (actual run this session). CLAUDE.md "Current State" still shows 436/436 — doc lag from sprint v5.38 adding 10 additional checks (R27, R30, R31, R32, and v5.38 sprint checks). GSI_WIP.md shows Regression: 446/446 PASS (439 always-on base). DEVIATION from SNAPSHOT-012 (was 437).

**Q02. R27 enforcement scope:** R27 enforces GSI_SPRINT_MANIFEST.json completeness. Dynamic checks (R27 content-level, R30, R31, R32) activate when manifest status == "IN_PROGRESS". R28 (hook/rules file existence) always-on. Current manifest: v5.38 status COMPLETE. Unchanged from SNAPSHOT-012.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All other modules banned. R3 regression check enforces this. Unchanged from SNAPSHOT-012.

**Q04. DataManager bypass mode:** DataManager M1 skeleton in data_manager.py. BYPASS MODE active until M4 ships (OPEN-007, HIGH priority). Pages call market_data.py directly. R24 enforces bypass. Unchanged from SNAPSHOT-012.

**Q05. Signal arbitration hierarchy:** Weinstein Stage > Elder Triple Screen > raw signal score. Stage 4 vetoes BUY from Elder (hard veto → AVOID). Stage 1/3 forces WATCH. Veto must be visibly disclosed in UI (Policy 6). Enforced in indicators.py compute_unified_verdict(). Unchanged from SNAPSHOT-012.

**Q06. M3 routing guard (grp_explicitly_selected):** Session_state flag set only on explicit user group click. Gates 49-ticker batch download to prevent rate limit spirals. Resets on market switch. R22 enforces it. Unchanged from SNAPSHOT-012.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in dashboard header _render_header_static(). Option B is final: verdict badge + plain-English reason only. Score IS permitted in KPI panel. ADR-008 is final record. Unchanged from SNAPSHOT-012.

**Q08. Five Permanent Tier A manifest checks:** Every sprint manifest must contain all 5: (1) sync_docs_passes; (2) compliance_baseline_current; (3) pr_template_baseline_current; (4) decisions_has_sprint_adr; (5) qa_standards_has_brief. Unchanged from SNAPSHOT-012.

**Q09. Current sprint and pending pre-sprint work:** v5.38 COMPLETE (session_027, 2026-04-14). Next sprint: v5.39 (not yet planned). GSI_WIP.md Status: IDLE. Pending pre-sprint work: PLAYWRIGHT-07 (obs-P1b Sprint Monitor tab) and PLAYWRIGHT-08 (obs-P1c Risk & Compliance tab) deferred — no live Streamlit instance at sprint close. Also: Playwright-01 through -06 still never run. Note: GSI_session.json meta.last_session shows session_026 — likely not updated at session_027 close (minor doc gap). UPDATED from SNAPSHOT-012.

**Q10. Pre-push gate:** Two commands: (1) python3 regression.py (446 checks confirmed this session); (2) python3 compliance_check.py — 10/10 gates confirmed this session. UPDATED from SNAPSHOT-012 (was 9/9).

## SNAPSHOT-014 | 2026-04-17 | session_029 | v5.39 | QSet-v1
*Compared to SNAPSHOT-013 (QSet-v1). Deviations: none. Updated: Q01 (446→451 baseline), Q04 (M1→M2 DataManager shipped), Q09 (v5.39 COMPLETE), Q10 (446→451 count). New questions: none.*

**Q01. Regression baseline:** 451/451 PASS (run this session). CLAUDE.md and GSI_session.json show 452 — baseline drift: 452 was documented when manifest was IN_PROGRESS (R27.struct = 4 checks active); at COMPLETE, R27.struct stops, R27.complete starts (1 check), net −3. Correct always-on COMPLETE-mode baseline is 451. UPDATED from SNAPSHOT-013 (was 446).

**Q02. R27 enforcement scope:** R27 enforces GSI_SPRINT_MANIFEST.json completeness. IN_PROGRESS: R27.log (per-file change-log checks), R27.A/B (tier content checks), R27.struct (4 structural gates: token_budget_present, tier_a_checks_complete, token_burn_log_is_last, cross_sprint_log_closed). COMPLETE: R27.complete (1 check: wip_idle_at_sprint_close). Current manifest: v5.39 COMPLETE. Unchanged from SNAPSHOT-013.

**Q03. yfinance import restriction:** Only market_data.py may import yfinance. All 14 other project files are banned. R3 regression check (15 checks) enforces this. Unchanged from SNAPSHOT-013.

**Q04. DataManager bypass mode:** DataManager is now at M2 (v5.39). CacheManager (bounded LRU L2, 200 entries, OrderedDict) + DataContract wire-level validator are implemented and wired. bypass_mode property returns True (self._bypass = True hardcoded, set False in M3). Pages still use market_data.py directly. M3 (worker thread) deferred — replaced by Vercel Workflow DevKit. M4 = YAHOO adapter + pages migration. R24 (10 checks) + R24.M2 (6 new checks, added v5.39) enforce module structure. UPDATED from SNAPSHOT-013 (was M1 skeleton only).

**Q05. Signal arbitration hierarchy:** Weinstein Stage veto → Elder Triple Screen → momentum score. Stage AVOID veto → hard AVOID regardless of score. Stage WATCH veto → caps at WATCH. Elder suppress_buy=True → caps at WATCH. All vetoes produce conflict strings disclosed in UI. Implemented in compute_unified_verdict() in indicators.py (line 520). Unchanged from SNAPSHOT-013.

**Q06. M3 routing guard (grp_explicitly_selected):** session_state flag (default False). Set True by group selector on_change callback (app.py line 120). Reset False on market switch (app.py line 59). Gates 49-ticker batch download at app.py line 258. R22 (20 checks) enforces lazy-loading contracts. Unchanged from SNAPSHOT-013.

**Q07. DO NOT UNDO rule 12:** Raw Momentum score (X/100) must NOT appear in _render_header_static(). Confirmed: score variable is set (line 116) but NOT rendered in the markdown output — only verdict badge, plain-English reason, and align text are shown. Score IS present in _tab_insights() KPI panel (line 949) as permitted. ADR-008 is the final record. Unchanged from SNAPSHOT-013.

**Q08. Permanent Tier A manifest checks:** Five required: (1) sync_docs_passes; (2) compliance_baseline_current; (3) pr_template_baseline_current; (4) decisions_has_sprint_adr; (5) qa_standards_has_brief. Unchanged from SNAPSHOT-013.

**Q09. Current sprint and pending pre-sprint work:** v5.39 COMPLETE (session_028, 2026-04-17). GSI_WIP.md Status: IDLE. Carry-forward: (1) PLAYWRIGHT-09 deferred — navigate to /observability, DEV_TOKEN gsi-dev-2026, Sprint Monitor tab, assert no opacity error banner (Playwright MCP backend closed mid-session); (2) tests/test_data_manager_m2.py — 36 unit tests require Python 3.9 (/Users/home/Library/Python/3.9/bin/python3), not system Python 3.14. UPDATED from SNAPSHOT-013.

**Q10. Pre-push gate:** Two commands: (1) python3 regression.py — 451 checks (COMPLETE-mode baseline); (2) python3 compliance_check.py — 10/10 gates (C10 = SEBI disclaimer in week_summary.py). Compliance catches SEBI/XSS violations in page files that regression alone misses. UPDATED from SNAPSHOT-013 (was 446 checks).

## SNAPSHOT-015 | 2026-04-18 | session_030 | v5.39 | QSet-v1
*Compared to SNAPSHOT-014 (QSet-v1). Deviations: none. Updated: Q09 (v5.39 COMPLETE → session_030 start, v5.40 Phase 1 pending). New questions: none.*

**Q01. Regression baseline:** 451/451 PASS (run this session). Matches CLAUDE.md COMPLETE-mode baseline. Unchanged from SNAPSHOT-014.

**Q02. R27 enforcement scope:** Unchanged from SNAPSHOT-014 — regression.py not modified since session_029 baseline correction. R27 enforces GSI_SPRINT_MANIFEST.json completeness; content checks active only IN_PROGRESS; R27.complete (1 check) active at COMPLETE.

**Q03. yfinance import restriction:** Unchanged from SNAPSHOT-014 — only market_data.py may import yfinance; R3 (15 checks) enforces. No new modules added.

**Q04. DataManager bypass mode:** Unchanged from SNAPSHOT-014 — DataManager at M2 (CacheManager + DataContract). bypass_mode=True until M4. Pages use market_data.py directly. R24 + R24.M2 (10+6 checks) enforce.

**Q05. Signal arbitration hierarchy:** Unchanged from SNAPSHOT-014 — Weinstein Stage veto → Elder Triple Screen → momentum score. compute_unified_verdict() in indicators.py (line 520). Vetoes disclosed in UI.

**Q06. M3 routing guard:** Unchanged from SNAPSHOT-014 — grp_explicitly_selected session_state flag; R22 (20 checks) enforces lazy-loading contracts.

**Q07. DO NOT UNDO rule 12:** Unchanged from SNAPSHOT-014 — raw Momentum score absent from _render_header_static(); present in KPI panel only. ADR-008 final record.

**Q08. Permanent Tier A manifest checks:** Unchanged from SNAPSHOT-014 — 5 checks: sync_docs_passes, compliance_baseline_current, pr_template_baseline_current, decisions_has_sprint_adr, qa_standards_has_brief.

**Q09. Current sprint and pending pre-sprint work:** session_029 COMPLETE (baseline correction + WIP plan). GSI_WIP.md Status: IDLE. Next: v5.40 Phase 1 (8 items, ~37k tokens, all sequential — Block A Sonnet first). Carry-forward: PLAYWRIGHT-09 still deferred; test_data_manager_m2.py requires Python 3.9. UPDATED from SNAPSHOT-014.

**Q10. Pre-push gate:** Unchanged from SNAPSHOT-014 — python3 regression.py (451 checks) + python3 compliance_check.py (10/10). Compliance catches SEBI/XSS violations regression alone misses.

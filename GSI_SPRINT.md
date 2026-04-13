# GSI Dashboard — Sprint Board
# ════════════════════════════════════════════════════════════════════════
# This file is the single source of truth for sprint planning.
# Updated at the start and end of every session.
# The "In Progress" column acts as a WIP lock alongside GSI_WIP.md.
# ════════════════════════════════════════════════════════════════════════

## Current Sprint: v5.37 — Planning

**Status:** Planning — backlog candidates below (sprint not yet opened)
**Target date:** TBD
**Regression baseline entering sprint:** 434/434
**Goal:** TBD — pending Action 2 (financial analyst / SEBI compliance review) findings before sprint is locked.

### CEO Sign-offs recorded (2026-04-01)
- S-01: WorldMonitor → stopgap link button now, Leaflet+GDELT in v5.36
- S-02: Landing page → GitHub Pages one-pager
- S-03: Analytics → streamlit-analytics
- S-04: Launch sequence → private beta first → Reddit → Product Hunt
- S-05: Yahoo ToS → educational/non-commercial confirmed for MVP

---

### Backlog (candidate items for v5.36)

Sourced from GSI_session.json open_items and GSI_AUDIT_TRAIL.md open findings.
Prioritised by impact and implementation effort.

**Phase groupings:**
- Items marked `OPEN-018 (Claude API)` require AI narrative integration — future phase, do not start before OPEN-018.
- Items marked `OPEN-007` depend on DataManager M2 — complete M2 before starting those.
- All other items are standalone and can be picked for the next sprint.

| ID | Description | Effort | Source | Governance policy |
|---|---|---|---|---|
| OPEN-004 | Extract SCORING_WEIGHTS to config.py | Low | session | Policy 2 |
| OPEN-003 | Cross-session forecast persistence (Supabase) | High | session | Policy 2 |
| C-02 | Macro data (Gold, Crude) not accessible to stock-level AI narrative | Medium | audit | OPEN-018 (Claude API) |
| C-03 | RSI 36 described as "neutral momentum" in AI narrative — wrong | Medium | audit | OPEN-018 (Claude API) |
| C-08 | Sector breadth computed but never passed to AI narrative engine | Medium | audit | OPEN-018 (Claude API) |
| F-02 | India Impact formula static — not computed from live Crude price | Medium | audit | OPEN-018 (Claude API) |
| C-01 | Sector breadth not wired to narrative — partially fixed in v5.31 | Medium | audit | OPEN-018 (Claude API) |
| OPEN-006 | Portfolio Allocator stability score UI (shipped v5.23 — needs UI polish) | Medium | session | Policy 3 (UX) |
| OPEN-007 | DataManager M2: CacheManager + DataContract validator | High | session | Policy 2 (arch) |
| OPEN-018 | Claude API integration — live AI narrative (Opus 4.6 / Mythos-ready) | Medium | session | Policy 4,5 |
| C-05 | Momentum score decomposition / scale disclosure | Medium | audit | Policy 5 |
| PROXY-01 | Classifier alignment — sync keyword lists between sprint_planner.py and approval_hook.py (shared config or automated sync-check) | Low | proxy | Policy 2 (arch) |
| PROXY-02 | Fallback transparency — log notification when paid model falls back to Groq (post-call hook or LiteLLM success_handler) | Low | proxy | Policy 7 (freshness labeling) |
| PROXY-03 | Post-proxy diff review gate — commit tagging convention `[proxy:model]`; script to flag un-reviewed proxy commits before push | Medium | proxy | Policy 2 |
| PROXY-04 | Depends column in sprint_planner.py — detect cross-tier dependencies (subscription item needed before proxy item can start); warn in execution guide | Medium | proxy | Policy 2 |
| PROXY-05 | Sprint board staleness check — sprint_planner.py warns when GSI_SPRINT.md In Progress items are older than 2 sessions | Low | proxy | Policy 7 |
| PROXY-06 | Spend visibility — `--spend` flag in validate_models.py calls LiteLLM `/spend` endpoint; shows daily per-provider cost summary | Low | proxy | Policy 3 (UX) |
| PROXY-07 | Tool-use guard in approval_hook — detect `tools` key in request data; block routing to Groq (no tool-use support); escalate to `deep-reasoning` or reject with clear error | Low | proxy | Policy 2 (arch) |
| PROXY-08 | Proxy execution flow fix — env vars locked at process start; implement two-launch sequence in CLAUDE.md + sprint_planner.py; validate with live proxy test. **Batch: implement in same sequential block as HOOK-01 + OPEN-023 (all 3 touch non-UI, low-risk files — single regression run at end of block saves ~6k tokens).** | Low | proxy | Policy 2 (arch) |
| HOOK-01 | R28 regression check: add existence check for `.claude/hooks/post_quant_flag.sh` — baseline moves 434→435. Also add `.claude/quant_audit_pending.json` to R10b list. **Dependency: if ALERT-01 ships first, this check must target `gsi_alerts.json` instead of `quant_audit_pending.json` — do not implement HOOK-01 independently after ALERT-01 is merged.** | Low | session_020 | Policy 2 (arch) |
| **OPEN-022** | **P0-REGULATORY: SEBI disclaimer absent in two week_summary.py signal sections — Signal Summary tab (lines 649–679, BUY/WATCH/AVOID count cards) and Portfolio Allocator allocation table (lines 956–968, per-stock badges). Neither contains "SEBI" or "investment advisor". compliance_check.py only gates dashboard.py so this passes the pre-push gate silently. Fix: add co-located SEBI disclaimer in each section. Score: 100 (CTO review 2026-04-08).** | Low | cto_review_v5.36 | Policy 4 (regulatory) |
| **OPEN-023** | **P1: litellm-proxy hf-code model name malformed — config.yaml line 59 has `groq/openai/gpt-oss-20b`; README documents "Groq Qwen-QwQ-32B". Double-slash format is invalid LiteLLM Groq syntax; hf-code tier will error at runtime and break the hf-reasoning→hf-code fallback chain silently. Fix: `groq/qwen-qwq-32b` (verify exact Groq model slug). Score: 85 (CTO review 2026-04-08).** | Low | cto_review_v5.36 | Policy 2 (arch) |
| **OPEN-024** | **P2: mean_acc dead variable in _render_forecast_accuracy_report (week_summary.py line 1104) — extracted from report dict but never rendered. Docstring promises "Mean price accuracy (how close was P50 to actual?)". Fix: add 4th KPI card or calibration note for mean_acc. Score: 100 (CTO review 2026-04-08).** | Low | cto_review_v5.36 | Policy 5 (data coherence) |
| **OPEN-025** | **P2: UNSTABLE threshold boundary mismatch — portfolio.py lines 370–375 trigger UNSTABLE at `>= 15` (else branch), but portfolio.py comment (line 347) and week_summary.py UI text (line 898) both say `> 15`. Fix: align comment + UI to `>= 15` or change code to `> 15`. Score: 100 (CTO review 2026-04-08).** | Low | cto_review_v5.36 | Policy 5 (data coherence) |
| **OPEN-026** | **P3-DOC: CLAUDE.md Key Entry Points not updated for two v5.36 functions — `_render_forecast_accuracy_report` in regression.py R8 EP list but absent from CLAUDE.md week_summary EP table; `compute_stability_score` absent from both CLAUDE.md portfolio EP table and regression R8 list. Fix: add both to CLAUDE.md; add compute_stability_score to regression R8. Score: 100 (CTO review 2026-04-08). Batch: same worktree agent as OPEN-025 (both doc/regression only, no .py logic — one regression run covers both, saves ~3k tokens).** | Low | cto_review_v5.36 | Policy 2 (arch) |
| ALERT-01 | **⭐ HIGH PRIORITY — pick up next sprint.** Generalised alert system: replace `quant_audit_pending.json` with `gsi_alerts.json` — unified flag file for P0_LAUNCH_BLOCKER, CEO_DECISION, SKILL_STALE, SESSION_CLEANUP, SPRINT_CLOSE_PENDING alert types. Pre-populate with: README screenshots, ADR-025, beta list, cxo.md stale, ui-test.md stale, last_session drift. Add `post_sprint_close.sh` hook. new-session surfaces grouped summary. Foundation for top-notch governance visibility across all program state. | Medium | session_020 | Policy 2 (arch) |
| QUANT-01 | First `/quant-reviewer` full audit run (all 5 domains) — **COMPLETE** (session_024, 2026-04-13). 11 findings, 0 P0 blockers. See docs/signal-accuracy-audit-v5.36-2026-04-13.md. D3 pending CEO Screener.in cross-check. | Medium | session_020 | Policy 5 (data coherence) |
| **QA-D3-01** | **P1 (CONFIRMED 2026-04-13): `_calc_roe()` returns 0.37% for INFY.NS vs Screener.in actual 30.3% — 29.93pp gap. Root cause: `netIncomeToCommon` in USD, `bookValue × sharesOutstanding` in INR. The `returnOnEquity` field (32.68%) is within ±3pp of actual (30.3%). Fix: when `returnOnEquity` is available AND calculated value diverges >10pp, prefer `returnOnEquity`. HDFCBANK (13.18% vs 14.4% Screener) and RELIANCE (9.49% vs 8.40% Screener) both pass ±3pp. Only INFY.NS is affected (USD-reporting company on NSE).** | Low | quant_audit_session_024 | Policy 5 (data coherence) |
| **QA-D1-01** | **P1: RSI uses Cutler's SMA (`rolling(14).mean()`) not Wilder's RMA (`ewm(com=13)`). Diverges from TradingView/Zerodha by 3–8 RSI points on stocks with <100 bars of data. Converges (<0.5pt) at >100 bars. Fix: switch to `ewm(com=13, adjust=False)` with SMA seed for first 14 values. Document: regression passes after change only if all RSI references updated.** | Medium | quant_audit_session_024 | Policy 5 (data coherence) |
| **QA-D1-02** | **P1: ATR uses SMA(14) (`tr.rolling(14).mean()`) not Wilder's RMA. Diverges 5–15% on volatile stocks at short windows. Same fix pattern as QA-D1-01. Batch with RSI fix — same commit, same regression run.** | Medium | quant_audit_session_024 | Policy 5 (data coherence) |
| QA-D2-04 | P2: `compute_unified_verdict()` return dict missing `veto_applied: bool` key. Policy 6 requires veto visible disclosure in UI. Veto fires correctly (Stage 4 → AVOID) but the boolean flag for UI disclosure is absent. Fix: add `"veto_applied": stage == 4` or check `conflicts` list. One-line fix in `indicators.py`. | Low | quant_audit_session_024 | Policy 6 (signal arbitration) |
| QA-D2-03 | P2: Elder Screen 3 (entry trigger) not implemented — only 2 of 3 Elder screens active. UI labels it "Elder Triple Screen" — inaccurate. Fix A (quick): rename label to "Elder Two-Screen Filter" in UI. Fix B (full): implement Screen 3 (stochastic-based entry confirmation). | Medium | quant_audit_session_024 | Policy 5 (data coherence) |
| QA-D1-03 | P2: Bollinger Bands use `ddof=1` (pandas default) vs TradingView `ddof=0`. ~2.6% wider bands. Not wrong per se — document the difference in UI tooltip. Fix: add chart footnote "Bollinger σ: sample std (ddof=1)". | Low | quant_audit_session_024 | Policy 7 (data freshness labeling) |
| QA-D5-01 | P2: `EXP_DECAY=0.97` in portfolio.py vs expected ~0.94. Half-life ~23 days vs 11 days — weights older data more. Verify design intent with portfolio designer. If intentional: document in `GSI_DEPENDENCIES.md`. If unintentional: adjust to 0.94. | Low | quant_audit_session_024 | Policy 5 (data coherence) |
| QA-D5-02 | P2: Efficient frontier has no monotonicity guard. Solver instability could produce a backwards-bending section (higher CVaR but lower return) without detection. Fix: add assertion after `compute_efficient_frontier()` — at least 10/12 points must be non-dominated. | Low | quant_audit_session_024 | Policy 5 (data coherence) |
| **OPEN-027** | **P0-REGULATORY (Action 2): SEBI disclaimer absent from `_render_global_signals()` (home.py:343). BUY/WATCH/AVOID index signals refresh every 60s; existing caption is non-SEBI. Fix: st.caption with full SEBI text after line 343, before column loop. Playwright: verify disclaimer visible on Home page → Global Signals section.** | Low | action2_sebi | Policy 4 (regulatory) |
| **OPEN-028** | **P0-REGULATORY (Action 2): FS-01 + FS-06 in `_render_watchlist_badges()` (global_intelligence.py:60–90). Named stocks shown with price/% but no BUY/WATCH/AVOID verdict (FS-06) and no SEBI disclaimer (FS-01). Section title "Related Stocks to Watch" implies action. Fix: (a) add SEBI caption after section header line 61; (b) fetch and display cached verdict per ticker for FS-06 compliance. Playwright: verify disclaimer + verdict badge visible in GI watchlist section.** | Medium | action2_sebi | Policy 4 (regulatory) + Policy 5 |
| **OPEN-029** | **P0-REGULATORY (Action 2): SEBI disclaimer absent from `_render_header_static()` (dashboard.py:159–163). Verdict badge is tab-independent — visible on Charts/Forecast/Compare tabs; Insights tab disclaimer (line 1059) does NOT cover these tabs. Fix: add compact st.caption after header markdown block (after line 178). Playwright: navigate Dashboard → Charts tab → verify SEBI disclaimer present without switching to Insights.** | Low | action2_sebi | Policy 4 (regulatory) |

---

### In Progress

Nothing in progress. Next session picks from Backlog above.

---

### Done — v5.36 (2026-04-07)

| ID | Description | Verified |
|---|---|---|
| PROXY-01 | `classifier_keywords.py` — shared keyword config; `approval_hook.py` + `sprint_planner.py` import from it | Both files import cleanly ✓ |
| PROXY-02 | `approval_hook.py` — `async_success_callback` logs when actual model ≠ requested | Code review ✓ |
| PROXY-03 | `review_gate.py` — `[proxy:model]` tag convention; `--mark SHA` (git note); `--all` flag | `python3 litellm-proxy/review_gate.py` → exit 0 ✓ |
| PROXY-04 | `sprint_planner.py` — optional `Depends` column; warns inline when prerequisite not in Done | Code review ✓ |
| PROXY-05 | `sprint_planner.py` — git-log staleness check; warns when in-progress items >14 days old | Code review ✓ |
| PROXY-06 | `validate_models.py` — `--spend` flag → `/spend` endpoint → per-provider cost summary | `--help` shows flag ✓ |
| PROXY-07 | `approval_hook.py` — tool-use guard: forces `deep-reasoning` when `tools` key present | Code review ✓ |
| Bugfix | `sprint_planner.py` — `YELLOW` NameError on execution guide render; exit 1 → 0 | `python3 litellm-proxy/sprint_planner.py` → exit 0 ✓ |

---

### Done — v5.35.1 (2026-04-06)

| ID | Description | Verified |
|---|---|---|
| Bugfix | `safe_ticker_key` — allow `&`; `M&M.NS` was stripped to `MM.NS` (delisted phantom on group load) | Regression 433/433 ✓ |
| Bugfix | `tickers.json` — `AMBUJACEMENT.NS` → `AMBUJACEM.NS` (typo; correct NSE ticker) | No 404 on NIFTY Next 50 load ✓ |
| Bugfix | `tickers.json` — Zomato removed from IT & Technology (food delivery, not IT) | Remains in Nifty Next 50 ✓ |
| Bugfix | `tickers.json` — Paytm removed from IT & Technology (fintech, not IT) | Remains in Nifty Next 50 ✓ |
| Governance | CLAUDE.md Rule 8: parallel agent discipline — no git commands in worktree agents | Documented ✓ |
| Governance | Sprint close protocol step 0: dual version-field update in GSI_session.json before sync_docs | Documented ✓ |
| Planning | Tiered sprint capacity: 9-item flat cap → 3-lane budget (≤6 seq / ≤6 parallel / ≤4 risky) | GSI_SPRINT.md + CLAUDE.md ✓ |
| Planning | `token_budget` + `token_optimisations` manifest fields with per-type quality floor guardrails | CLAUDE.md Rule 2 ✓ |

---

### Done — v5.35 (2026-04-06)

| ID | Description | Verified |
|---|---|---|
| S-01 | ADR-022: WorldMonitor CSP stopgap formal decision record | ADR-022 in GSI_DECISIONS.md ✓ |
| S-02 | docs/index.html: GitHub Pages landing page (dark-theme, mobile-responsive, SEBI disclaimer) | File exists, SEBI disclaimer present ✓ |
| S-03 | streamlit-analytics2: requirements.txt + app.py integration (fail-safe) | R29 check passes 433/433 ✓ |
| S-04 | docs/social-media-guidelines.md: SEBI finfluencer rules + RISK-L04 → Mitigated | social_guidelines_exist ✓ |
| R29 | regression.py R29: analytics import check in app.py (+1 check, 432→433) | `python3 regression.py` → ALL 433 CHECKS PASS ✓ |

---

### Done — v5.34.2 (2026-04-05)

| ID | Description | Verified |
|---|---|---|
| R28 | regression.py R28 — 5 hook infrastructure existence checks (+5, baseline 427→432) | `python3 regression.py` → ALL 432 CHECKS PASS |
| Bugfix | CTO C-1: sync_docs.py exit code — exits 1 on issues (was 0, made post_edit error branch unreachable) | `python3 sync_docs.py --check` exits non-zero on issues |
| Bugfix | CTO C-2: observability.py path — dashboard.py→pages/dashboard.py (false compliance failures) | `python3 compliance_check.py` → 8/8 |
| Bugfix | CTO M-1: git rev-parse replaces CLAUDE_PROJECT_DIR in all 3 hooks (permanent fix) | Hooks fire without unbound variable errors |
| Bugfix | CTO M-2: compliance_check.py __main__ guard added (prevented R1 syntax check from running) | R1 syntax checks pass; module importable |
| Bugfix | CTO M-4: settings.json Write(*.sh) permission removed (was overbroad scope) | Settings reviewed |
| Bugfix | jq installed (brew install jq 1.8.1) — ralph-loop stop hook dependency | ralph-loop functional |
| Doc | .gitignore: RALPH_PROMPT.md + .claude/ralph-loop.local.md (ephemeral ralph state) | git status clean |
| Doc | GSI_LOOPHOLE_LOG.md Class 2: governance script hardcoded wrong path | Class 2 documented |

---

### Done — v5.34.1 (2026-04-05)

| ID | Description | Verified |
|---|---|---|
| Infra | compliance_check.py — 8-check pre-push gate (fixed path bug: dashboard.py→pages/dashboard.py) | `python3 compliance_check.py` passes 8/8 |
| Infra | .claude/hooks/pre_commit.sh — PreToolUse regression gate, exit 2, dedup via run_state.json | Regression R27.B pre_commit_hook ✓ |
| Infra | .claude/hooks/pre_push.sh — PreToolUse compliance gate, exit 2 | Regression R27.B pre_push_hook ✓ |
| Infra | .claude/hooks/post_edit.sh — PostToolUse doc audit on *.md, suppressOutput on pass | Regression R27.B post_edit_hook ✓ |
| Infra | settings.json — hooks block (3 hooks), sync_docs --check migrated from settings.local.json | Regression R27.B hooks_block_added ✓ |
| Bugfix | regression.py R27 schema — target_file field + must_contain list iteration | Regression R27.B r27_bug_fixed ✓ |

---

### Done — v5.34 (2026-04-01)

| ID | Description | Verified |
|---|---|---|
| R27 | GSI_SPRINT_MANIFEST.json living manifest system — per-file doc update enforcement | Regression R27 (sprint-active) |
| Doc debt | 6 v5.33 audit resolutions: H-02/D-07/D-09/G-02/G-05/EQA-38 | GSI_AUDIT_TRAIL.md |
| Doc debt | RISK-T09 Open→Mitigated, governance enforcement updated, v5.31 entry added | GSI_RISK_REGISTER.md |
| Phase 1 | market_data.py: get_health_stats() + get_rate_limit_state() + 3 counters | Regression R26 |
| Phase 1 | pages/observability.py: App Health + Program tabs, DEV_TOKEN gated | Regression R26 |
| D-05 | Loading spinner on Dashboard nav (data_stale gate) | Code review |
| G-03/F-10 | Impact chain overflow CSS fix (width:100% + box-sizing:border-box) | Code review |
| F-14 | West Asia quantitative claims sourced (Reuters/EIA/PPAC/Drewry) | Code review |

---

### Done — v5.33 (2026-03-31)

| ID | Description | Verified |
|---|---|---|
| RISK-003 | safe_ticker_key() before yf.download() | Regression R25.P2a |
| RISK-001 | sanitise()/safe_url() XSS in home.py + GI | Regression R25.P7b |
| D-07 | Elder labels → plain English | Code review |
| G-02 | GI topics 2→5 (Rate Cycle, China, Commodities) | Code review |
| G-05 | GI subtitle "Real-Time" removed | Regression R25.P4c |
| H-02 | Loading states: "Loading…"/"Computing…" | Code review |
| D-09 | Forecast correction factor disclosed | Code review |
| OPEN-017 | R25 governance checks (6 rules, 10 checks) | Regression 410/410 |
| P0-fix | SEBI disclaimer in _tab_insights() | Regression R25.P4a |
| P0-fix | Algo disclosure in _tab_insights() | Regression R25.P4b |
| P0-fix | "No major red flags" blanket fallback removed | Regression R25 |
| P0-fix | 48h Live Headlines gate in GI | Regression R25.P7a |

---

### Done — v5.32 (2026-03-29)

| ID | Description | Verified |
|---|---|---|
| OPEN-008 | calc_5d_change() shared utility | Regression R23b |
| OPEN-009 | P(gain) 45–55% neutral zone | Regression R23b |
| OPEN-010 | Forecast dedup — replace same-day entries | Regression R23b |
| OPEN-011 | Dynamic week summary section titles | Regression R23b |
| OPEN-012 | Weinstein override label names the stage | Regression R23b |
| OPEN-013 | MACD (Daily) label on chart + KPI panel | Regression R23b |
| OPEN-014 | GI watchlist market filter | Regression R23b |
| OPEN-015 | Market LIVE badge names specific market | Regression R23b |
| OPEN-016 | GI watchlist cache_buster=0 | Regression R23b |

---

### Done — v5.31 (2026-03-28)

| ID | Description | Verified |
|---|---|---|
| P0-1 | Option B: raw score removed from header | QA verified |
| P0-2 | ROE null guard: N/A not 0.0% | QA verified |
| P0-3 | SEBI disclaimer + algorithmic disclosure | QA verified |
| P0-4 | Watch Out For RSI/MACD-aware fallback | QA verified |
| H-03 | Market status short labels | QA verified |
| F-15/F-01 | GI topic cards expanded by default | QA verified |
| F-03 | Stale RSS replaced, 48h freshness gate | QA verified |
| F-06/EQA-33 | What You Should Do Next removed | QA verified |
| EQA-29 | SEBI disclaimer | QA verified |
| EQA-32 | Algorithmic disclosure | QA verified |

---

### Sprint Planning Rules

1. **Tiered capacity budget** — replace the flat 9-item cap with three independent budgets:

   | Lane | Definition | Limit |
   |---|---|---|
   | Sequential | Items that depend on each other or touch shared files | ≤ 6 |
   | Parallel agent | Fully independent file changes — dispatched as worktree agents per Rule 8 | ≤ 6 |
   | Risky / high-judgment | Page files, compliance, market_data.py, tickers.json, any P0 change | ≤ 4 (regardless of lane) |

   Effective ceiling: **~14 items per sprint** (6 seq + 6 parallel, with risky items counted against their own cap).
   A sprint with only sequential items is still capped at 6 — the old 9 ceiling applied when parallelism wasn't available.

2. **Token budget + optimisation log in manifest** — before implementation starts, fill both `token_budget` and `token_optimisations` blocks in `GSI_SPRINT_MANIFEST.json`.
   Each item gets: `mode` (sequential | parallel_agent), `files_touched` (count), `est_tokens` (range), `risk` (low | medium | high).
   Sprint-level totals: main-context tokens (sequential only) + agent tokens (parallel only) + overhead.
   Reference costs: sequential item ~8–12k, parallel agent item ~20–25k (isolated), regression run ~3k, sync_docs ~2k, large-file read (GSI_WIP.md) ~4k.
   **Quality floor — optimisations may never remove:** regression gate · compliance gate · QA brief · CTO Read-before-commit on agent output · Read-before-Edit rule.

3. **Group by file** — batch changes to the same file in the same sprint. Cross-file changes in separate sprints.
4. **Regression check before adding** — every new item must have a clear R-check definition before entering "In Progress".
5. **No item enters "In Progress" without a WIP entry** — update GSI_WIP.md simultaneously.
6. **Commit after every file** — do not batch multiple files into a single commit. If Claude hits a limit, only uncommitted files are at risk.

7. **Model + agent + token + permission declaration (mandatory for every item)** — every sprint item, backlog entry, and action item must declare the following fields before implementation begins. These are set at planning time and locked in `GSI_SPRINT_MANIFEST.json`:

   | Field | Values | Guidance |
   |---|---|---|
   | `model` | `haiku` \| `sonnet` \| `opus` | Haiku: grep/doc/pattern-match/trivial edits. Sonnet: code changes, judgment calls, agent tasks. Opus: architecture decisions, high-stakes compliance, novel design. |
   | `agents` | count + mode | e.g. `1 × sequential`, `3 × worktree-parallel`, `2 × haiku-scoring` |
   | `est_tokens` | range string | e.g. `"8k–12k"` for sequential Sonnet; `"2k–4k"` for Haiku doc edit |
   | `permissions_required` | list | Categories: `file-read`, `file-write`, `bash-python3`, `bash-git`, `bash-gh`, `worktree-agent`, `playwright-browser`, `mcp-tool` |

   **Pre-approval protocol:** At the start of every sprint, Claude posts a single permission manifest listing every `permissions_required` entry across all planned items. User approves once per sprint — not per tool call. If a mid-sprint item needs an unlisted permission, pause and request approval before proceeding. This eliminates per-call approval friction.

   **Model selection rationale must be documented.** "Haiku is sufficient because this is a grep + single-line edit with no judgment required." Not just the model name.

8. **Playwright test coverage (mandatory for every UI-touching item)** — every sprint item that modifies a page file, CSS, or user-visible output must include:

   - A **Playwright test case definition** in the QA brief (written before implementation, not after). Format:
     ```
     PLAYWRIGHT-[ID]:
       Navigate: [route or tab]
       Action: [what to trigger]
       Assert: [exact text / element / absence of element]
       Edge cases: [empty data, None values, extreme inputs, mobile viewport]
     ```
   - At minimum: 1 happy-path test + 2 edge-case tests per changed UI section.
   - **>95% hygiene target**: Claude runs the Playwright suite via the `ui-test` skill after implementation. All cases must pass before the item is marked Done. Failures are bugs, not known issues.
   - Items that touch only non-UI files (regression.py, config, doc-only `.md`) are exempt from Playwright requirement — mark `playwright: N/A` with reason.

---

### v5.37 Item Specifications (Draft — session_021, 2026-04-08)
*Pending sprint review before locking. Risky lane overflow: 5 P0 items → recommend split into v5.37a (SEBI compliance) + v5.37b (governance/proxy).*

#### v5.37a — SEBI Compliance Sprint (proposed)

| ID | Model | Agents | Est. tokens | Permissions | Playwright |
|---|---|---|---|---|---|
| OPEN-022 | sonnet — judgment needed for correct section placement | 1 × sequential | 10–14k | file-read, file-write, bash-python3, playwright-browser | PLAYWRIGHT-022a: Home → Week Summary → Signal Summary tab → assert "SEBI-registered investment advisor" above signal cards. Edge: market closed; zero resolved signals. PLAYWRIGHT-022b: Portfolio Allocator tab → assert SEBI text before allocation table. Edge: single-ticker group. |
| OPEN-027 | sonnet — fragment is a live @st.fragment; placement relative to column loop matters | 1 × sequential | 8–12k | file-read, file-write, bash-python3, playwright-browser | PLAYWRIGHT-027: Home page → Global Signals section → assert SEBI disclaimer visible. Edge: no markets open; all signals NEUTRAL. |
| OPEN-028 | sonnet — two sub-fixes: (a) SEBI caption (Haiku-capable), (b) verdict fetch from cache requires judgment | 1 × sequential (split: caption first, verdict second commit) | 12–18k | file-read, file-write, bash-python3, playwright-browser | PLAYWRIGHT-028a: GI page → Related Stocks to Watch → assert SEBI disclaimer. PLAYWRIGHT-028b: each watchlist badge shows BUY/WATCH/AVOID label. Edge: ticker cache cold; ticker data unavailable. |
| OPEN-029 | haiku — single st.caption line after a known line number; no judgment | 1 × sequential | 4–6k | file-read, file-write, bash-python3, playwright-browser | PLAYWRIGHT-029: Dashboard → Charts tab (do NOT switch to Insights) → assert SEBI disclaimer visible in header area. Edge: AVOID verdict; STRONG BUY verdict. |

#### v5.37b — Governance + Proxy Sprint (proposed)

| ID | Model | Agents | Est. tokens | Permissions | Playwright |
|---|---|---|---|---|---|
| ALERT-01 | sonnet — schema design + multi-file | 1 × sequential (main) + 1 × haiku (skill scaffold) | 25–35k | file-read, file-write, bash-python3, bash-git | N/A — CLI/session tooling |
| HOOK-01 *(after ALERT-01)* | haiku — targeted regex.py edit only | 1 × sequential | 3–5k | file-read, file-write, bash-python3 | N/A — regression infra |
| PROXY-08 + OPEN-023 *(batched)* | haiku — doc edit + 1-line config fix; one regression at end | 1 × sequential | 6–9k total | file-read, file-write | N/A — CLI/proxy |
| QUANT-01 | sonnet — Domains 1+2+5 via worktree; Domain 3 needs CEO input (pause point) | 3 × worktree-parallel | ~60–75k agent; ~5k main-ctx | file-read, worktree-agent, bash-python3 | N/A — audit generates report, not UI |
| OPEN-024 | sonnet — layout context needed for KPI card placement | 1 × sequential | 10–14k | file-read, file-write, bash-python3, playwright-browser | PLAYWRIGHT-024: Week Summary → Forecast Accuracy → assert 4th KPI "Mean Price Accuracy" present. Edge: 0 resolved forecasts → "—"; mean_accuracy key absent → "—"; value exactly 0.0% → "0.0%". |
| OPEN-025 + OPEN-026 *(batched)* | haiku — 2 string edits + 2 doc lines; one worktree | 1 × worktree-parallel | 5–8k total | file-read, file-write, bash-python3, playwright-browser | PLAYWRIGHT-025: Portfolio Allocator → Stability Score card → assert description contains ">= 15%". OPEN-026: N/A. |

#### Sprint-level permission pre-approval (post v5.37 review, request before kickoff)
`file-read · file-write · bash-python3 · bash-git · worktree-agent · playwright-browser`
*(No bash-gh, mcp-tool, or opus required in either sub-sprint)*

---

### Sprint Velocity

| Sprint | Version | Items | Sessions | Est. Tokens | Optimisations | Outcome |
|---|---|---|---|---|---|---|
| Global signals hotfix | v5.37.1 | 1 | 0.1 | ~3k (actual) | Single read+edit, no agents | Period-aware _ticker_cache; ADR-026; loophole class 3 updated; 444/444 |
| SEBI compliance + governance | v5.37 | 9 code + 2 gov | 2 | ~85k (actual) | df-03/df-08/H1/H2 batched sequential; no agents needed — all targeted single-file edits | 9 P0/P1/P2 items, sprint-monitor onboarded, compute_stability_score R8, 436/436 |
| Post-launch hardening | v5.36 | 10 | 1 | ~100k (est) | Proxy savings forfeited (env-var lifecycle bug); D-02/OPEN-006/EQA-41 run under subscription (PROXY-08 deferred) | 7 proxy items + 3 feature items, ADR-024, PROXY-08 parked, 434/434 |
| Post-sprint hotfix + governance | v5.35.1 | 8 | 0.5 | ~40k (actual) | All sequential; no agents needed for targeted fixes | 3 bugfixes, 2 governance rules, 2 planning upgrades, 433/433 |
| Launch readiness | v5.35 | 5+R29 | 1 | ~150k (actual) | 3 parallel agents saved ~45k main-ctx; sync_docs debug loop wasted ~10k (RECORD-008) | All 5 complete, R29 +1 check, 433/433 |
| Regression hardening + sprint close | v5.34.2 | 9 | 1 | ~80k (est) | — | All 9 complete, R28 +5 checks, baseline 432/432 |
| Hook infrastructure + CTO review | v5.34.1 | 8+fixes | 2 | ~120k (est) | — | All items complete + all CTO findings fixed |
| Manifest + observability + UX | v5.34 | 8 | 1 | ~90k (est) | — | All 8 complete, 5 R26 checks, R27 manifest system |
| Security, compliance & governance | v5.33 | 8 | 1 | ~90k (est) | — | All 8 complete + 4 P0 gaps fixed, 10 R25 checks |
| Data coherence | v5.32 | 9 | 1 | ~80k (est) | — | All 9 complete, 11 R23b checks |
| P0 regulatory | v5.31 | 8 | 1 | ~80k (est) | — | All 8 verified by QA |
| Lazy loading M0-M3 | v5.24–v5.25 | 6 | 2 | ~100k (est) | — | Complete |
| Portfolio allocator | v5.23 | 1 major | 1 | ~60k (est) | — | Complete |

# GSI Dashboard — Sprint Board
# ════════════════════════════════════════════════════════════════════════
# This file is the single source of truth for sprint planning.
# Updated at the start and end of every session.
# The "In Progress" column acts as a WIP lock alongside GSI_WIP.md.
# ════════════════════════════════════════════════════════════════════════

## Current Sprint: v5.36 — Post-Launch Hardening

**Status:** Planning — backlog candidates below
**Target date:** TBD
**Regression baseline entering sprint:** 433/433
**Goal:** Address post-beta feedback, DataManager M2, observability improvements, landing page screenshots.

### CEO Sign-offs recorded (2026-04-01)
- S-01: WorldMonitor → stopgap link button now, Leaflet+GDELT in v5.36
- S-02: Landing page → GitHub Pages one-pager
- S-03: Analytics → streamlit-analytics
- S-04: Launch sequence → private beta first → Reddit → Product Hunt
- S-05: Yahoo ToS → educational/non-commercial confirmed for MVP

---

### Backlog (candidate items for v5.35)

Sourced from GSI_session.json open_items and GSI_AUDIT_TRAIL.md open findings.
Prioritised by impact and implementation effort.

**Phase groupings:**
- Items marked `OPEN-018 (Claude API)` require AI narrative integration — future phase, do not start before OPEN-018.
- Items marked `OPEN-007` depend on DataManager M2 — complete M2 before starting those.
- All other items are standalone and can be picked for the next sprint.

| ID | Description | Effort | Source | Governance policy |
|---|---|---|---|---|
| D-02 bench | ROE benchmark: self-calculate from yfinance financials | Medium | audit | Policy 5 (data coherence) |
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
| EQA-41 | Forecast accuracy visual baseline | Medium | audit | Policy 7 |

---

### In Progress

Nothing in progress. Next session picks from Backlog above.

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

1. **Max 9 items per sprint** — v5.32 was the ceiling. Larger sprints fragment context and risk mid-session limits.
2. **Group by file** — batch changes to the same file in the same sprint. Cross-file changes in separate sprints.
3. **Regression check before adding** — every new item must have a clear R-check definition before entering "In Progress".
4. **No item enters "In Progress" without a WIP entry** — update GSI_WIP.md simultaneously.
5. **Commit after every file** — do not batch multiple files into a single commit. If Claude hits a limit, only uncommitted files are at risk.

---

### Sprint Velocity

| Sprint | Version | Items | Sessions | Outcome |
|---|---|---|---|---|
| Regression hardening + sprint close | v5.34.2 | 9 | 1 | All 9 complete, R28 +5 checks, baseline 432/432 |
| Hook infrastructure + CTO review | v5.34.1 | 8+fixes | 2 | All items complete + all CTO findings fixed |
| Manifest + observability + UX | v5.34 | 8 | 1 | All 8 complete, 5 R26 checks, R27 manifest system |
| Security, compliance & governance | v5.33 | 8 | 1 | All 8 complete + 4 P0 gaps fixed, 10 R25 checks |
| Data coherence | v5.32 | 9 | 1 | All 9 complete, 11 R23b checks |
| P0 regulatory | v5.31 | 8 | 1 | All 8 verified by QA |
| Lazy loading M0-M3 | v5.24–v5.25 | 6 | 2 | Complete |
| Portfolio allocator | v5.23 | 1 major | 1 | Complete |

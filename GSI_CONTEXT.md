# GSI Dashboard — Project Context (lean, always-on)
# Upload ONLY this file to Claude Project Files
# Do NOT upload CLAUDE.md (5k tokens) or GSI_session.json (35k tokens) to Project Files
# Regenerate: python3 generate_context.py  (auto-runs after regression.py passes)
# Generated: 2026-04-06 | v5.34.2 | ALL 432 CHECKS PASS
# Target: <1,600 tokens. Do not add verbose content here.

## Identity
Project: Global Stock Intelligence Dashboard
Repo: https://github.com/Tarun19k/stock-intelligence-test-1-vs
Session manifest (Gist): https://gist.github.com/Tarun19k/7c894c02dad4e76fe7c404bf963baeab
Stack: Python 3.14 · Streamlit 1.55 · yfinance 1.2 · pandas>=1.4.0
Deploy: Streamlit Cloud (community) · no API keys · no database
Current version: v5.34.2 | Regression: ALL 432 CHECKS PASS

## Architecture — one paragraph
14-file modular app. market_data.py is the ONLY yfinance importer.
indicators / forecast / portfolio have ZERO Streamlit calls.
Pages receive pre-computed data — never fetch directly.
4-state routing in app.py: stock → group → market → week.
DataManager M1 exists (data_manager.py) — BYPASS MODE until M4.
  Pages must NOT call DataManager.fetch() until M4 is implemented.
calc_5d_change() in utils.py is the ONLY 5-day calculation function.
GI watchlist uses cache_buster=0 — matches ticker bar cache key.
tickers.json is the single source of truth for all 559 tickers and 38 groups.

## DO NOT UNDO — hard rules (sourced live from CLAUDE.md)
 1. Do NOT revert `forecast.py` to filesystem persistence. — Cloud wipes filesystem on redeploy.
 2. Do NOT remove `cache_buster: int = 0` — from market_data functions.
 3. Do NOT add `scope='fragment'` to `st.rerun()`. — StreamlitAPIException in 1.43.
 4. Do NOT move VERSION_LOG back into config.py. — In version.py by design.
 5. Do NOT move GROUPS back into config.py. — In tickers.json by design.
 6. Do NOT use Streamlit MPA as primary nav. — MPA sidebar hidden via CSS.
 7. Do NOT use `TATAMOTORS.NS`. — Delisted. Use `TMCV.NS` + `TMPV.NS`.
 8. Do NOT put CSS in `inject_css()` docstring. — All CSS inside `CSS` constant.
 9. Do NOT re-add `_refresh_fragment` to app.py. — Removed v5.26. Was a no-op.
10. Do NOT pass `cache_buster=cb` to `get_news()`. — News is not stock-specific. Use 0.
11. Do NOT restore "No major red flags at this time."
12. Do NOT display raw Momentum score (X/100) in the dashboard header. — Option B is final — verdict badge + plain-English reason only. Score is in KPI panel.
13. Do NOT remove the SEBI disclaimer from `_tab_insights()`. — It is a P0 regulatory requirement. It must appear before the three insight columns.
14. Do NOT call `_render_next_steps_ai()` from `render_global_intelligence()`. — Removed v5.31 — liability risk. Function definition kept for future redesign.
15. QA brief protocol:

## Critical patterns (from GSI_SKILLS.md anti-patterns)
safe_float(None)=0.0 — for ROE/fundamentals: show N/A not 0.0% if val==0
GI topic cards: expanded=True by default — collapsed page looks empty to beginner
RSS 48h freshness gate: Live Headlines label only when newest article < 48h old
WorldMonitor: CSP blocks *.streamlit.app — use external link button, not iframe
DataManager.fetch(): banned in pages until M4 — bypass mode enforced
Algo disclosure: every AI narrative section must be labeled algorithmically generated
SEBI disclaimer: required on every BUY/WATCH/AVOID signal section in pages

## Dependency constraints (full detail in GSI_DEPENDENCIES.md)
C-001 pandas>=1.4.0 NOT >=3.0.0 — streamlit declares pandas<3 in metadata
C-002 streamlit==1.55: CSS selectors changed — see CONSTRAINT-002 before upgrading
C-003 yfinance MultiIndex: df['Close'].iloc[:,0] if isinstance(..., pd.DataFrame)
C-004 Ticker.info ROE returns None for Indian stocks — guard: val!=0 else 'N/A'
C-005 _is_rate_limited() must precede every yfinance call in market_data.py
C-006 FutureWarning: suppress yfinance/pandas warnings via warnings.filterwarnings
C-007 libopenblas-dev in packages.txt — required by cvxpy on Streamlit Cloud Linux
C-008 st.rerun(scope='fragment') raises StreamlitAPIException — use plain st.rerun()
C-009 WorldMonitor CSP blocks all *.streamlit.app embeds — replaced with link button

## Governance documents (all in repo root)
GSI_WIP.md               READ FIRST every session. Mutex + CHECKPOINT.
CLAUDE.md                Full architecture reference
GSI_GOVERNANCE.md        7 mandatory policies — read before any new feature
GSI_SKILLS.md            10 dev patterns + anti-patterns catalogue
GSI_DECISIONS.md         15 ADRs — check before re-litigating any design choice
GSI_SPRINT.md            Sprint board + backlog
GSI_AUDIT_TRAIL.md       48 audit findings. Append-only. Never edit records.
GSI_DEPENDENCIES.md      9 compatibility constraints. Check before upgrading.
GSI_QA_STANDARDS.md      Test briefs, personas, finding registry
GSI_COMPLIANCE_CHECKLIST.md  Pre-deploy gate. Tier 1-3 block deploy.
GSI_PRODUCT.md           MVP scope, personas, dependency map, monetisation path
GSI_MARKETING.md         Positioning, competitive analysis, launch strategy
GSI_RISK_REGISTER.md     24 risks: technical, legal, product, operational
GSI_LOOPHOLE_LOG.md      6 classes of automation-caught loopholes. Append as discovered.
GSI_SESSION_LEARNINGS.md Per-session stale-info/confusion/hallucination/deviation log. Append-only via /log-learnings.
GSI_SESSION_SNAPSHOT.md  Per-session Q&A snapshot of 10 key invariants. Compared at session start to detect semantic drift.
.claude/commands/        36 slash commands — skills, legal, product, marketing, management
.claude/rules/           Path-scoped rules — auto-load in Claude Code only (not claude.ai)

## Open items
  OPEN-003 [MEDIUM]: Cross-session forecast persistence
  OPEN-004 [LOW]: indicators.py scoring weight audit
  OPEN-006 [MEDIUM]: Portfolio Allocator — Mean-CVaR optimisation tab in group overview
  OPEN-007 [HIGH]: DataManager: SQLite + priority queue + circuit breaker + market-aware TTLs
  OPEN-018 [MEDIUM]: Claude API integration — live AI narrative with Opus 4.6 / Mythos-ready

## Sprint discipline
Max 9 items per sprint — verified ceiling for single-session completion
Commit after every file — never batch multiple files into one commit
Checkpoint protocol: write CHECKPOINT block to GSI_WIP.md if context runs low
  then immediately push GSI_WIP.md + any committed files to GitHub

## Session start ritual
1. Read GSI_WIP.md FIRST — ACTIVE = resume from CHECKPOINT, IDLE = proceed
2. This file is already loaded (Project Files)
3. Run: python3 regression.py — expect above baseline
4. Read GSI_GOVERNANCE.md before any new feature development
5. Check GSI_SPRINT.md for current sprint backlog

## Before every commit
regression.py passes → compliance Tier 1-3 (GSI_COMPLIANCE_CHECKLIST.md)
→ version.py entry added → GSI_WIP.md updated (Status: IDLE) → GSI_SPRINT.md updated
→ commit per file (never batch) → push → update Gist

## Phase 3 sprint close protocol (full sequence)
1. /log-learnings → GSI_SESSION_LEARNINGS.md (stale/confusion/learning records)
2. Trigger review: scan GSI_SNAPSHOT_QUESTIONS.md checklist — did this sprint add/change
   regression checks, modules, DO NOT UNDO rules, or major invariants? If yes, add/retire
   questions in GSI_SNAPSHOT_QUESTIONS.md and bump QSet version.
3. python3 sync_docs.py (auto-update CHANGELOG, README, AGENTS)
4. Update baseline count in GSI_COMPLIANCE_CHECKLIST.md + .github/PULL_REQUEST_TEMPLATE.md
5. Append ADR → GSI_DECISIONS.md; append QA brief → GSI_QA_STANDARDS.md
6. version.py entry; CLAUDE.md baseline + Current State; GSI_CONTEXT.md header
7. GSI_SPRINT.md Done; GSI_WIP.md Status IDLE
8. regression.py final pass — all checks must pass
9. Commit, push, update Gist
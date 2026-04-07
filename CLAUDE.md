# CLAUDE.md — Global Stock Intelligence Dashboard
# Read this FULLY before touching any file in this repo.
# Last updated: 2026-03-27 (Session 007 — v5.26 hotfix batch)
# Dynamic session state: GSI_Session.json (see Gist URL at bottom)

---

## Project Overview

Multi-market stock intelligence dashboard built with Streamlit.
Entry point: `app.py` (root). 9 markets, 559 tickers, 38 groups, 4-tab per-stock dashboard.
Two repos — ALL active work is in the modular repo:

- **ACTIVE:** https://github.com/Tarun19k/stock-intelligence-test-1-vs
- **REFERENCE ONLY (monolith, do not edit):** https://github.com/Tarun19k/global-gsi-intelligence

---

## Run Commands

```bash
streamlit run app.py        # run the app locally
python3 regression.py       # MUST pass (410/410) before any new work
```

Before every `git push`, also run the compliance script:
```bash
python3 compliance_check.py
```

Deploy: Streamlit Community Cloud (1GB RAM) + local dev.

---

## Environment

```
streamlit==1.55.0   yfinance==1.2.0     feedparser==6.0.11
plotly==5.24.1      pandas>=1.4.0       numpy>=2.0.0
pytz==2024.2        requests==2.32.3    cvxpy==1.8.2
```

Runtime: Python 3.14.x (Streamlit Cloud default). System deps: libopenblas-dev.

Streamlit 1.55 notes:
- `@st.fragment(run_every=N)` dims entire page during re-render — expected, not a bug
- `use_container_width=True` correct for `st.dataframe`; do NOT use `width='stretch'`
- `width='content'` is valid on `st.dataframe` in 1.52+ (content-width mode)
- `st.rerun(scope='fragment')` raises StreamlitAPIException — use plain `st.rerun()`
- `_refresh_fragment` REMOVED in v5.26 — do not re-add
- `st.plotly_chart` uses `config={'responsive': True}` — `**kwargs` deprecated in 1.50

---

## Current State (v5.35.1 — 2026-04-06)

**Regression baseline: 434/434 PASS** *(stable; R27 sprint-manifest checks add additional checks during active sprints)*

**v5.35 sprint: COMPLETE**

Versions since last CLAUDE.md update:
- **v5.33** — Security, compliance & governance sprint (see version.py for full notes)
- **v5.34** — Sprint manifest infrastructure + observability dashboard + UX fixes:
  - R27: GSI_SPRINT_MANIFEST.json living manifest system — every committed file logged with doc update requirements; regression enforces completeness each sprint
  - Doc debt backfill: 6 v5.33 audit resolutions, RISK-T09 mitigated, governance enforcement updated, missing v5.31 entry added
  - Phase 1: market_data.py observability instrumentation (`get_health_stats()`, `get_rate_limit_state()`, `_cache_stats`, `_fetch_errors`, `_fetch_latency_ms`); 5 R26 checks
  - Phase 1: `pages/observability.py` — founder-only App Health + Program dashboard, `DEV_TOKEN` gated
  - Phase 2: D-05 spinner on Dashboard nav (data_stale gate); G-03/F-10 impact chain overflow CSS fix; F-14 West Asia attribution
- **v5.34.1** — Claude Code hook infrastructure:
  - compliance_check.py: 8-check pre-push gate extracted from CLAUDE.md inline script
  - .claude/hooks/pre_commit.sh: PreToolUse regression gate (exit 2 blocks)
  - .claude/hooks/pre_push.sh: PreToolUse compliance gate (exit 2 blocks)
  - .claude/hooks/post_edit.sh: PostToolUse doc audit on *.md (suppressOutput on pass)
  - settings.json: hooks block wired (3 hooks), sync_docs --check migrated from local
- **v5.34.2** — Regression hardening + CTO review fixes:
  - R28: 5 hook infrastructure existence checks (baseline 427→432)
  - CTO fixes: sync_docs exit code, observability path, git rev-parse in hooks, __main__ guard, permission scope
- **v5.35** — Launch readiness sprint:
  - S-01: ADR-022 WorldMonitor CSP stopgap formal record (link button already implemented)
  - S-02: `docs/index.html` GitHub Pages landing page (dark-theme, mobile-responsive, SEBI disclaimer)
  - S-03: `streamlit-analytics2` integration in `app.py` + `requirements.txt`; R29 check (baseline 432→433)
  - S-04: `docs/social-media-guidelines.md` new file; RISK-L04 Open → Mitigated in risk register
- **v5.35.1** — Post-sprint hotfix + governance improvements:
  - Fix: `safe_ticker_key` allows `&` — `M&M.NS` was stripped to `MM.NS` (delisted phantom)
  - Fix: `tickers.json` — `AMBUJACEMENT.NS` → `AMBUJACEM.NS` typo; Zomato + Paytm removed from IT & Technology (misclassified)
  - Governance: CLAUDE.md Rule 8 (parallel agent git discipline); sprint close protocol step 0 (dual version-field requirement)
  - Planning: tiered sprint capacity (9-item flat → 3-lane: ≤6 seq / ≤6 parallel / ≤4 risky); `token_budget` + `token_optimisations` manifest fields with quality floor guardrails
  - Regression baseline: 433/433 PASS (v5.35.1 base)
- **v5.35.1 governance patch** — GSI_FILE_IMPACT.md new change-type → file map; sync_docs.py velocity + learnings checks; R10b extended (433→434)
---

## File Structure

### Code files — safe rebuild order
```
version.py              Changelog + CURRENT_VERSION. No logic.
tickers.json            Master ticker registry. Edit here, NEVER in config.py.
config.py               Constants hub. Re-exports GROUPS + VERSION_LOG.
utils.py                safe_run(), sanitise(), init_session_state().
styles.py               All CSS in CSS constant. inject_css() called once from app.py.
indicators.py           compute_indicators(df), signal_score(df, info), unified verdict.
market_data.py          All yfinance + RSS. Token bucket + _ticker_cache + warmth guard.
data_manager.py         DataManager M1 skeleton + CircuitBreaker. Bypass mode until M4.
forecast.py             Forecast lifecycle. session_state as primary store.
portfolio.py            Mean-CVaR engine. No Streamlit calls.
pages/week_summary.py   Weekly summary + group/market overview.
pages/global_intelligence.py  Geopolitical topics + WorldMonitor link + watchlists.
pages/home.py           Ticker bar + homepage. 3 deferred @st.fragment sections.
pages/dashboard.py      4-tab stock dashboard: Charts | Forecast | Compare | Insights.
pages/observability.py  Founder-only App Health + Program dashboard. DEV_TOKEN gated.
app.py                  Entry point. Routing. No _refresh_fragment.
regression.py           427-check regression suite. Must pass before every commit.
compliance_check.py     8-check pre-push gate. Extracted from CLAUDE.md inline script.
requirements.txt        Python dependencies. See Environment section for constraints.
```

### Governance & documentation files (repo root)
```
CLAUDE.md                    Architecture reference. Read before every session.
GSI_GOVERNANCE.md            7 policies — mandatory rules for all development.
GSI_QA_STANDARDS.md          Test brief template, issue classification, data reliability.
GSI_SKILLS.md                Development patterns, anti-patterns, lessons learned.
GSI_COMPLIANCE_CHECKLIST.md  Pre-deploy gate. Run alongside regression.py.
GSI_session.json             Session manifest. Dynamic state. Push to Gist after sessions.
```

---

## Rate Limiting Architecture

### Current (v5.26) — Token Bucket + Module Cache
| Component | Detail |
|---|---|
| `_global_throttle()` | Token bucket: max=5, rate=0.4s. threading.Lock serialises all threads. |
| `_yf_batch_download()` | CHUNK=3, inter-chunk=5s, rate-limit backoff=10s, cold-start delay=2s |
| `_ticker_cache` | Module-level dict. Survives @st.cache_data evictions. Stale fallback. |
| `is_ticker_cache_warm()` | 70% majority threshold. Gates fragments on cold start. |

### Planned (OPEN-007) — DataManager: SQLite + Priority Queue
Three new packages: `requests-cache` + `requests-ratelimiter` + `pyrate-limiter`.
Combined as `CachedLimiterSession` passed to `yf.Ticker(session=)`.
Benefits: cache survives restarts, market-aware TTLs, stale-while-revalidate.
**NOT YET INTEGRATED** — see Open Items.

---

## Key Entry Points

```
app.py              _is_market_open(country), _on_market_change()
pages/home.py       render_ticker_bar(cb), render_homepage(cb, market_open)
                    _render_global_signals()          # @st.fragment(run_every=60)
                    _render_top_movers(cb)            # @st.fragment(run_every=60)
                    _render_news_feed(cb)             # @st.fragment(run_every=300)
pages/dashboard.py  render_dashboard(ticker, name, country, cur_sym, info, df, cb, ...)
                    _make_live_price_fragment(...)    # @st.fragment(run_every=5s market only)
pages/week_summary.py render_week_summary, render_market_overview, render_group_overview
pages/global_intelligence.py render_global_intelligence(cur_sym, cb, market_open)
pages/observability.py render_observability() — DEV_TOKEN gated, MPA direct URL only
market_data.py      get_ticker_bar_data_fresh(tickers) [TTL=10s]
                    get_batch_data(tickers, period, interval, cache_buster) [TTL=300s]
                    get_price_data(ticker, period, interval, cache_buster) [TTL=300s]
                    get_ticker_info(ticker, cache_buster) [TTL=600s]
                    get_live_price(ticker) [TTL=5s]
                    get_intraday_chart_data(ticker) [TTL=60s]
                    get_top_movers(symbols, max_symbols, cache_buster) [TTL=300s]
                    get_news(feeds, max_n, cache_buster) [TTL=600s]
                    is_ticker_cache_warm(tickers) → bool
                    get_health_stats() → dict  [no TTL — reads module counters]
                    get_rate_limit_state() → dict  [no TTL — reads module counters]
indicators.py       compute_indicators(df), signal_score(df, info)
                    compute_weinstein_stage(df), compute_elder_screens(df)
                    compute_unified_verdict(sig, stage, elder, asset_class)
forecast.py         store_forecast, resolve_forecasts, render_forecast_accuracy
portfolio.py        check_data_quality, compute_log_returns, winsorize_returns
                    bootstrap_scenarios, optimise_mean_cvar, compute_efficient_frontier
                    detect_stress_regime, check_regime_conflicts
utils.py            safe_run(fn, context, default), sanitise(text, max_len)
                    sanitise_bold(text, max_len), init_session_state()
```

---

## DO NOT UNDO — Hard Rules

1. **Do NOT revert `forecast.py` to filesystem persistence.** Cloud wipes filesystem on redeploy.
2. **Do NOT remove `cache_buster: int = 0`** from market_data functions.
3. **Do NOT add `scope='fragment'` to `st.rerun()`.** StreamlitAPIException in 1.43.
4. **Do NOT move VERSION_LOG back into config.py.** In version.py by design.
5. **Do NOT move GROUPS back into config.py.** In tickers.json by design.
6. **Do NOT use Streamlit MPA as primary nav.** MPA sidebar hidden via CSS.
7. **Do NOT use `TATAMOTORS.NS`.** Delisted. Use `TMCV.NS` + `TMPV.NS`.
8. **Do NOT put CSS in `inject_css()` docstring.** All CSS inside `CSS` constant.
9. **Do NOT re-add `_refresh_fragment` to app.py.** Removed v5.26. Was a no-op.
10. **Do NOT pass `cache_buster=cb` to `get_news()`.** News is not stock-specific. Use 0.
11. **Do NOT restore "No major red flags at this time."** as the Watch Out For fallback. It is a false safety statement. The RSI/MACD-aware default is the correct replacement.
12. **Do NOT display raw Momentum score (X/100) in the dashboard header.** Option B is final — verdict badge + plain-English reason only. Score is in KPI panel.
13. **Do NOT remove the SEBI disclaimer from `_tab_insights()`.** It is a P0 regulatory requirement. It must appear before the three insight columns.
14. **Do NOT call `_render_next_steps_ai()` from `render_global_intelligence()`.** Removed v5.31 — liability risk. Function definition kept for future redesign.
15. **QA brief protocol:** Always include before/after screenshots and explicit expected text. Never rely on numbered fix lists alone — tester must know exactly what they are looking at on screen. Learned from v5.31 Fix1/Fix2 numbering confusion.

---

## Regression Suite

`python3 regression.py` — run from repo root. All checks must pass before any commit.

22 rule categories across syntax, imports, design contracts, lazy-loading contracts (R22).
R8 EP list: verify `_refresh_fragment` absent from app.py EP, `_make_live_price_fragment` present in dashboard EP.

---

## Open Items

### Infrastructure
| ID | Priority | Task |
|---|---|---|
| OPEN-001 | HIGH | git rm config_OLD.py + git rm --cached forecast_history.json |
| OPEN-002 | MED | README update |
| OPEN-003 | MED | Cross-session forecast persistence (Supabase) |
| OPEN-004 | LOW | Extract SCORING_WEIGHTS to config |
| OPEN-005 | HIGH | git rm config_OLD.py from repo root |
| OPEN-006 | MED | Portfolio Allocator stability score UI + backtest |
| **OPEN-007** | **HIGH** | **DataManager M2: CacheManager + DataContract validator (M1 complete)** |
| RISK-001 | MED | XSS: sanitise() all {ticker}/{name} in unsafe_allow_html f-strings |
| RISK-003 | LOW | safe_ticker_key() in _yf_download() before yf.download() |

### QA Audit Backlog — v5.32 Sprint (P1 High)
| ID | Audit Ref | Task |
|---|---|---|
| OPEN-008 | H-01 | 5-day calculation unification — shared `_calc_5d_change(df)` across Home/Dashboard/GI |
| OPEN-009 | D-03 | Forecast neutral threshold — P(gain) 45–55% shows "Insufficient directional signal" |
| OPEN-010 | D-04 | Forecast deduplication — update existing entry when forecast unchanged same day |
| OPEN-011 | D-06/D-08 | Temporal labels — explicit "This week" / "Today" on all time-relative figures |
| OPEN-012 | C-04 | Weinstein override disclosure — label when Stage vetoes Elder signal |
| OPEN-013 | C-06 | MACD timeframe label — "Daily" on chart, "Intraday (live)" on KPI panel |
| OPEN-014 | F-05 | GI watchlist responds to market selector — pass `country` param |
| OPEN-015 | C-09 | Market LIVE badge gated on `market_open` bool, not Streamlit runtime |
| OPEN-016 | G-04 | GI ticker data coherence — use ticker_cache when warm |

### QA Audit Backlog — v5.33+ (P2 / Roadmap)
| ID | Audit Ref | Task |
|---|---|---|
| OPEN-017 | Governance | 7-policy governance framework + R25 regression checks |
| OPEN-018 | C-01 | Feed sector breadth into AI narrative engine (full C-01 fix) |
| OPEN-019 | C-05 | Momentum Score decomposition bar chart |
| OPEN-020 | G-01 | WorldMonitor self-hosted (Leaflet.js + ACLED/GDELT API) |
| OPEN-021 | Policy 5 | observability.py `_inline_compliance_check()` — refactor to call `compliance_check.py` instead of duplicating check logic (Policy 5: same metric = same function) |

## Governance Policy Framework (v5.31)

Seven policies agreed during QA audit session. All future features must comply.

| # | Policy | Core Rule |
|---|---|---|
| 1 | Data & Logic Integrity | No hard-coded dynamic values; refresh invalidates all cache layers |
| 2 | Architectural Policies | Strict module separation; CSP compliance on all embeds; scalable impact chains |
| 3 | UX & Performance Standards | Persona-ready density; 2MB bundle cap; 4:5 + 16:9 responsive |
| **4** | **Regulatory & Compliance** | **SEBI disclaimer on every signal section; algorithmic outputs labeled; no unnamed investment recommendations** |
| **5** | **Data Coherence** | **Same metric = same calculation function across all pages; AI narrative must consume same data as indicator panel** |
| **6** | **Signal Arbitration** | **Documented hierarchy: Weinstein > Elder in conflict; veto must be visibly disclosed in UI** |
| **7** | **Data Freshness Labeling** | **Recency claims ("Live", "Real-Time") gated on timestamp verification; stale data shows source date** |

Policies 4–7 are new additions from audit session 009. Policies 1–3 were pre-existing.

---

## Living Documentation

Governance documents produced from audit sessions 001–010 onwards.
Read before implementing any new feature. Update after every sprint.

| Document | Purpose |
|---|---|
| `GSI_GOVERNANCE.md` | 7 policies — mandatory rules for all future development |
| `GSI_QA_STANDARDS.md` | Test brief template, issue classification, data reliability matrix |
| `GSI_SKILLS.md` | Development patterns, anti-patterns, and lessons learned |
| `GSI_COMPLIANCE_CHECKLIST.md` | Pre-deploy gate — all items must pass before git push |
| `GSI_AUDIT_TRAIL.md` | Immutable audit trail — 48 findings, all resolutions. **Append only. Never edit existing records.** |
| `GSI_DECISIONS.md` | Architecture Decision Record log. 15 ADRs. Append only. Read before re-litigating any design choice. |
| `GSI_SPRINT.md` | Sprint board — backlog, in-progress, done. Updated every session. |
| `GSI_WIP.md` | Session continuity mutex. Read FIRST in every session. Write checkpoint when limit approaches. |
| `GSI_DEPENDENCIES.md` | Compatibility constraints. 9 active constraints. Check before upgrading any package. |
| `GSI_PRODUCT.md` | MVP scope, user personas, dependency map, free tier constraints, monetisation path. |
| `GSI_MARKETING.md` | Positioning, competitive analysis, channel strategy, Reddit/Product Hunt launch templates. |
| `GSI_RISK_REGISTER.md` | 24 risks across technical, legal (SEBI/SEC/MiFID II/FCA/CSRC), product, operational. |
| `GSI_LOOPHOLE_LOG.md` | 6 classes of loophole caught by automation. Append when new failure classes found. |
| `GSI_SESSION_LEARNINGS.md` | Per-session log of stale context, confusions, hallucinations, deviations, and new learnings. Append-only. Updated via /log-learnings (Phase 3 close step). |
| `GSI_SESSION_SNAPSHOT.md` | Per-session Q&A snapshot of 10 key system invariants. Written at session START after reading context. Compared to previous session's snapshot to detect semantic drift before any code is written. |
| `docs/social-media-guidelines.md` | SEBI Finfluencer rules for social media posts about the tool. Prohibited content, approved framing, platform-specific rules. RISK-L04 mitigation. |
| `docs/index.html` | GitHub Pages landing page. Static one-pager with hero, features, market coverage, SEBI disclaimer. Screenshot slots ready for real images. |
| `GSI_FILE_IMPACT.md` | Pre-change file impact map. Look up change type → every file that must be updated. Single source of truth for documentation accountability. |

Store all in repo root alongside CLAUDE.md.

---

## Scoped Rules (always active — path-specific behaviour)

These rules are enforced regardless of interface. In Claude Code they also
load automatically via `.claude/rules/` when the matching file is edited.

### When editing any page file (pages/*.py, dashboard.py)
- Every signal section showing BUY/WATCH/AVOID **must** include the SEBI disclaimer
- Algorithmic narrative sections **must** be labeled as algorithmically generated
- The Watch Out For fallback **must** check RSI and MACD — never use the blanket "no red flags" text
- Raw Momentum score (X/100) **must not** appear in `_render_header_static()`
- ROE display: `roe_str = f'{val:.1f}%' if val != 0 else "N/A"` — 0.0 is a data gap, not a value
- Any named stock must show its current BUY/WATCH/AVOID verdict alongside the name

### When editing market_data.py
- Every new public function calling yfinance **must** call `_is_rate_limited()` first
- Every new RSS feed domain **must** be added to `_ALLOWED_RSS_DOMAINS`
- `get_news()` always uses `cache_buster=0` — never pass `cb`
- Pages must NOT call `DataManager.fetch()` until M4 — bypass mode active
- TTLs: live price=5s, OHLCV=300s, ticker info=600s, financials=86400s, news=600s
---

## Usage Limit & Session Continuity Protocol

Claude.ai has usage limits. Any session can be interrupted mid-implementation.
These rules ensure zero work is lost and no conflict occurs between sessions.

### Rule 1 — Read GSI_WIP.md first, always
Before reading CLAUDE.md or session.json, read `GSI_WIP.md`.
- If `Status: IDLE` — proceed normally.
- If `Status: ACTIVE` — read the CHECKPOINT block and resume from it exactly.
  Do NOT start fresh. Do NOT regenerate files already marked complete.

### Rule 2 — Write to GSI_WIP.md and GSI_SPRINT_MANIFEST.json before starting any implementation
When starting a new sprint or implementation task:
1. Set `Status: ACTIVE` in GSI_WIP.md
2. List all planned tasks as unchecked boxes
3. Write `GSI_SPRINT_MANIFEST.json` with:
   - Tier A checks (always-required): version.py entry, CLAUDE.md version, GSI_CONTEXT.md header, GSI_SPRINT.md Done section
   - Tier B checks (sprint-specific): one check per audit finding fixed, risk mitigated, governance change, or new ADR
   - `file_change_log` entries for all files you know will change
   - `token_budget` block (see template below) — fill before any implementation
4. Begin implementation — regression R27 now enforces the manifest automatically

**Token budget template — add to every sprint manifest:**
```json
"token_budget": {
  "items": [
    {
      "id": "item-id",
      "mode": "sequential | parallel_agent",
      "files_touched": 1,
      "risk": "low | medium | high",
      "est_tokens": "8k–12k"
    }
  ],
  "overhead": {
    "session_start_context": "~15k",
    "regression_runs": "N × 3k",
    "sync_docs": "~2k",
    "sprint_close_sequence": "~10k"
  },
  "totals": {
    "main_context_est": "sequential items + overhead (parallel agents are isolated)",
    "agent_est": "sum of parallel_agent items",
    "grand_total_est": "main_context + agent (rough ceiling for cost awareness)"
  },
  "notes": "Flag any item > 20k as a split candidate"
}
```
Reference costs: sequential item ~8–12k · parallel agent item ~20–25k · regression run ~3k · sync_docs ~2k · large file read (GSI_WIP.md 520 lines) ~4k · context compaction overhead ~12k.

**Token optimisation log — add to every sprint manifest alongside token_budget:**
```json
"token_optimisations": [
  {
    "decision": "short label",
    "type": "parallelise | batch | split | read_avoidance | scope_narrow | defer",
    "items_affected": ["item-id"],
    "saving_est": "~Xk tokens",
    "detail": "what was done and what alternative was rejected"
  }
]
```
Optimisation types and quality floors:

| Type | Saves | Quality floor — non-negotiable |
|---|---|---|
| **parallelise** | ~20k main-context per item | CTO must Read agent output before committing — not just run regression |
| **batch** | ~5k per extra agent avoided | Only for doc-only changes (*.md, *.json config). Never batch code files. |
| **split** | ~15k per avoided oversized task | Sub-items must be committed independently; sub-item B cannot start until sub-item A's regression passes |
| **read_avoidance** | ~3–4k per skipped Read | **BANNED for files being edited.** Grep/Glob only for files being searched but not modified. Always Read before Edit — no exceptions. |
| **scope_narrow** | ~5–8k per agent | Agent prompt must include: file path, target function, and the relevant CLAUDE.md scoped rules for that file type |
| **defer** | full item cost | Deferred items must be added to GSI_SPRINT.md backlog in the same session — not silently dropped |

**Quality is never a budget variable.** Token savings are only valid if:
1. `python3 regression.py` still passes (433 checks — enforced by pre_commit.sh)
2. `python3 compliance_check.py` passes (8 P0 checks — enforced by pre_push.sh)
3. The QA brief covers every user-visible change in the sprint
4. No scoped rule from CLAUDE.md was skipped because of a narrow agent prompt

Fill this block BEFORE implementation. After sprint close, update `saving_est` with actuals where known. This log feeds the velocity table — track cumulative savings across sprints.

**Permanent Tier A checks — add to EVERY sprint manifest, no exceptions:**
```json
{ "id": "sync_docs_passes",             "tier": "A", "must_contain": ["see sync_docs.py exit 0"], "target_file": "sync_docs.py output" },
{ "id": "compliance_baseline_current",  "tier": "A", "must_contain": ["ALL {N} CHECKS PASS"], "target_file": "GSI_COMPLIANCE_CHECKLIST.md" },
{ "id": "pr_template_baseline_current", "tier": "A", "must_contain": ["ALL {N} CHECKS PASS"], "target_file": ".github/PULL_REQUEST_TEMPLATE.md" },
{ "id": "decisions_has_sprint_adr",     "tier": "A", "must_contain": ["v{sprint_version}"],   "target_file": "GSI_DECISIONS.md" },
{ "id": "qa_standards_has_brief",       "tier": "A", "must_contain": ["v{sprint_version}"],   "target_file": "GSI_QA_STANDARDS.md" }
```
Replace `{N}` with the post-sprint regression count; `{sprint_version}` with e.g. `v5.35`.

### Sprint close protocol — run before declaring any sprint COMPLETE
After the final implementation commit and before updating manifest status or GSI_WIP.md:
0. Update `GSI_session.json` version fields — **both** must be updated together before running sync_docs:
   - `current_version` (top-level) → new version
   - `meta.current_app_version` (nested) → same new version
   - `meta.next_version` → version + 1 minor
   sync_docs.py reads `meta.current_app_version` exclusively; stale top-level fields cause false "expected vX.XX" errors.
1. Run `python3 sync_docs.py` — auto-rebuilds CHANGELOG.md, README.md, AGENTS.md and checks all governance docs. Respond to any SEMI-auto prompts.
2. Run `python3 regression.py` — confirm baseline still passes after sync.
3. Update `GSI_SPRINT_MANIFEST.json` status → COMPLETE and archive to `docs/sprint_archive/`.
4. Set `GSI_WIP.md` Status → IDLE.

### Rule 3 — Commit after every file (git-first discipline)
Never batch multiple files into a single commit during active development.
Commit sequence: implement file → run regression → commit → then next file.
If Claude hits a limit, only the current uncommitted file is at risk.

### Rule 4 — Write a CHECKPOINT when context is running low
If Claude suspects it is approaching a context or usage limit:
1. Stop mid-task if necessary — a clean break is better than a half-done file
2. Write a CHECKPOINT block to GSI_WIP.md immediately:

```
## CHECKPOINT — [YYYY-MM-DD] [session-id]
Status: ACTIVE (interrupted)
Currently working on: [file + function + what change]
Completed (safe from outputs/):
  - [filename] ✓ committed / not committed
Not yet started:
  - [task]
Decisions made (add to GSI_DECISIONS.md):
  - [decision + reason]
Regression baseline at checkpoint: [N]/[N]
Resume instruction: [one precise sentence]
```

3. Push GSI_WIP.md to GitHub immediately after writing the checkpoint
4. Push any committed files

### Rule 5 — Max 9 items per sprint
Larger sprints increase the probability of hitting a limit mid-sprint.
9 items is the verified maximum for a clean single-session completion.
See GSI_SPRINT.md for sprint planning rules.

### Rule 6 — Decisions go to GSI_DECISIONS.md before session ends
Any decision that took more than 30 seconds to make gets an ADR record.
If the session ends before this is done, note the pending decisions in
the CHECKPOINT block of GSI_WIP.md.

### Rule 8 — Parallel agent discipline (worktree agents)
When dispatching parallel agents via `isolation: worktree`:
- Agent prompt **must** include: "Write the file and run `python3 regression.py` only. Do NOT attempt `git add`, `git commit`, or any git command."
- Agents cannot execute git commands (permission denied in worktree context) — asking wastes tokens.
- After worktrees close, all file writes persist in the main working tree. CTO (main conversation) inspects content, runs one final regression, then commits per Rule 3.
- One regression run by CTO after all agents complete is sufficient — agents do not need to run regression individually.

### Rule 7 — Amend the manifest for every mid-sprint file change
Before committing any file during a sprint — whether planned or not:
1. Check if the file is already in `file_change_log` in `GSI_SPRINT_MANIFEST.json`
2. If NOT listed: add an entry immediately with `doc_updates_required` or `no_doc_update_reason`
3. If a new file is created: look up its type in the template below and add standard checks
4. Add any new `checks[]` entries that the change requires
R27 fails if any committed file is missing from the log. No silent omissions.

**New file type → standard doc update checks:**
| File type | Required checks to add |
|---|---|
| `pages/*.py` | CLAUDE.md file structure, R8 EP list if new entry points |
| New `GSI_*.md` governance doc | R10b list in regression.py, CLAUDE.md Living Documentation table |
| New `*.py` utility/module | CLAUDE.md file structure, R8 EP list for public functions |
| `docs/sprint_archive/*.json` | None — archival artifact |


---

## Session Manifest (Dynamic State)

**GSI_Session.json Gist:** https://gist.github.com/Tarun19k/7c894c02dad4e76fe7c404bf963baeab

To resume with Claude:
> "I am working on the Global Stock Intelligence Dashboard.
>  Here is CLAUDE.md and GSI_Session.json — read both fully before we proceed."

**Minimum upload bundle for every session:**
- `GSI_WIP.md` — READ THIS FIRST. Contains session status and checkpoint if interrupted.
- `CLAUDE.md` — architecture reference and DO NOT UNDO rules
- `GSI_session.json` — session manifest with open items and baseline

**Also upload when starting a sprint or new feature:**
- `GSI_GOVERNANCE.md` — 7 policies Claude reads before writing any code
- `GSI_SKILLS.md` — development patterns and anti-patterns
- `GSI_SPRINT.md` — current sprint board and backlog
- `GSI_DECISIONS.md` — ADR log to prevent re-litigating resolved decisions

Note: `.claude/settings.json` (permission rules) and `.claude/rules/` (path-scoped rules)
only activate automatically in **Claude Code**. In Claude.ai, the Scoped Rules section
above covers the same content, and command files are used as reference documents.

**Using Claude Code?** Follow this sequence every session:

```bash
# 1. Outside Claude Code — check sprint board (zero tokens, pure Python)
python3 litellm-proxy/sprint_planner.py

# 2a. Proxy items on board today → set env vars, then launch
source litellm-proxy/.env
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY
claude

# 2b. Subscription items only → launch directly (no env vars)
claude
```

Inside Claude Code: `/new-session` to load context · `/compliance-check` before push · `/qa-brief` for QA briefs.

Proxy runs via launchd (auto-starts on login, no second terminal needed).
Active tiers: `hf-reasoning` (Groq 70B) · `hf-code` (Groq 20B) · `hf-fast` (Groq 8B).
Paid tiers (Anthropic API, OpenAI, Gemini, Perplexity) need billing activation — see `litellm-proxy/README.md`.

**Using Claude.ai?** The `.claude/commands/` files work as reference documents:
- Ask Claude to "follow the new-session command" → reads `.claude/commands/new-session.md`
- Ask Claude to "generate a qa-brief" → reads `.claude/commands/qa-brief.md`
- Ask Claude to "run compliance-check" → reads `.claude/commands/compliance-check.md`
- Ask Claude to "run sprint-review" → reads `.claude/commands/sprint-review.md`
Upload the relevant command file alongside CLAUDE.md when you need it.

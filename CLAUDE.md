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
python3 regression.py       # MUST pass (399/399) before any new work
```

Before every `git push`, also run the compliance script in `GSI_COMPLIANCE_CHECKLIST.md`:
```bash
# Quick inline version (copy from GSI_COMPLIANCE_CHECKLIST.md §Quick compliance script)
python3 -c "
import re
files = {'db':open('dashboard.py').read(),'gi':open('pages/global_intelligence.py').read(),'md':open('market_data.py').read(),'ind':open('indicators.py').read()}
checks=[('SEBI disclaimer','SEBI-registered investment advisor' in files['db']),('Algo disclosure','algorithmically generated' in files['db'].lower()),('No raw score','Momentum: {score}/100' not in files['db']),('No red flags fallback','"No major red flags at this time."' not in files['db']),('ROE guard','roe_str' in files['db']),('Next steps removed',len(re.findall(r'(?<!def )_render_next_steps_ai\(\)',files['gi']))==0),('RATES CONTEXT','RATES CONTEXT' in files['ind']),('Rate limit gate','_is_rate_limited()' in files['md'])]
fails=[n for n,ok in checks if not ok]
print(f'{len(checks)-len(fails)}/{len(checks)} compliance checks passed')
[print(f'  FAIL: {n}') for n in fails] if fails else print('Safe to push')
"
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

## Current State (v5.31 — 2026-03-28)

**Regression baseline: 399/399 PASS**

**v5.31 QA status: ALL 8 FIXES VERIFIED (2026-03-28)**

Versions since last CLAUDE.md update:
- **v5.29** — `get_ticker_info` missing `_is_rate_limited()` gate added
- **v5.30** — `styles.py` sidebar collapse CSS for Streamlit 1.55 (stSidebarCollapsedControl)
- **v5.31** — QA audit P0 fixes (see Open Items for full audit backlog):
  - Option B: raw Momentum score removed from header; verdict + plain-English reason only
  - ROE 0.0% null guard → N/A (yfinance returns null for Indian tickers via safe_float→0)
  - Watch Out For false positive fixed: RSI/MACD-aware default, never blanket "no red flags"
  - SEBI disclaimer + algorithmic disclosure added to Insights tab (P0 regulatory fix)
  - Market status card labels: IND/USA/EUR/CHN/COMM/ETF (prevents mid-word wrapping)
  - TechCrunch stale RSS feeds removed from AI & Jobs config
  - GI topic cards: expanded=True by default
  - Live Headlines label: date-gated, only "Live" when article <48h old
  - "What You Should Do Next" removed from GI page (liability, no market relevance)
  - R17 regression updated: "Momentum Signal Panel" accepted as valid score label
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
app.py                  Entry point. Routing. No _refresh_fragment.
regression.py           399-check regression suite. Must pass before every commit.
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
market_data.py      get_ticker_bar_data_fresh(tickers) [TTL=10s]
                    get_batch_data(tickers, period, interval, cache_buster) [TTL=300s]
                    get_price_data(ticker, period, interval, cache_buster) [TTL=300s]
                    get_ticker_info(ticker, cache_buster) [TTL=600s]
                    get_live_price(ticker) [TTL=5s]
                    get_intraday_chart_data(ticker) [TTL=60s]
                    get_top_movers(symbols, max_symbols, cache_buster) [TTL=300s]
                    get_news(feeds, max_n, cache_buster) [TTL=600s]
                    is_ticker_cache_warm(tickers) → bool
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

Five governance documents produced from audit sessions 001–010.
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

### Rule 2 — Write to GSI_WIP.md before starting any implementation
When starting a new sprint or implementation task:
1. Set `Status: ACTIVE` in GSI_WIP.md
2. List all planned tasks as unchecked boxes
3. Begin implementation

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

**Using Claude Code?** Run `/new-session` to auto-load all context.
Run `/compliance-check` before pushing. Run `/qa-brief` to generate QA briefs.

**Using Claude.ai?** The `.claude/commands/` files work as reference documents:
- Ask Claude to "follow the new-session command" → reads `.claude/commands/new-session.md`
- Ask Claude to "generate a qa-brief" → reads `.claude/commands/qa-brief.md`
- Ask Claude to "run compliance-check" → reads `.claude/commands/compliance-check.md`
- Ask Claude to "run sprint-review" → reads `.claude/commands/sprint-review.md`
Upload the relevant command file alongside CLAUDE.md when you need it.

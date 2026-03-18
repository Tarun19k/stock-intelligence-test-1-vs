# GSI Known Issues Log
# Maintained from: v1.0 (2026-02-28)
# Last updated:    v5.17   (2026-03-18)
#
# Format:
#   [ID]  Severity · Version discovered · Version fixed
#   Root cause · Fix · Regression check added
# ──────────────────────────────────────────────────────────────────────────────

KI-001
  severity   : HIGH
  discovered : v5.5  (2026-03-17)
  fixed      : v5.5  (2026-03-17)
  file       : all files
  symptom    : Streamlit deprecation warning / potential future crash
  root_cause : st.plotly_chart(use_container_width=True) deprecated after
               Streamlit 1.40 — parameter removed from API
  fix        : Replaced with width='stretch' (or explicit pixel width) across
               all 10 files
  regression : R2 — scan all files for 'use_container_width' in live code
               (VERSION_LOG string occurrence is a false positive — excluded)

KI-002
  severity   : HIGH (silent, pre-existing since v5.6)
  discovered : v5.9  (2026-03-18) — first seen at runtime
  fixed      : v5.9  (2026-03-18)
  file       : pages/dashboard.py
  symptom    : NameError: name 'sanitise_bold' is not defined
               (raised in _tab_insights when rendering insight cards)
  root_cause : sanitise_bold() was added to utils.py in v5.6 and used in
               dashboard.py, but the import line was never updated:
               'from utils import safe_float, sanitise, ...' — missing
               sanitise_bold. Dormant until a stock with insights was loaded.
  fix        : Added sanitise_bold to the utils import in dashboard.py
  regression : R8 — verify every entry point used in a file is imported
               R9 — cross-file import resolution check

KI-003
  severity   : HIGH
  discovered : v5.9  (2026-03-18)
  fixed      : v5.10 (2026-03-18)
  file       : pages/home.py → render_ticker_bar()
  symptom    : Ticker bar invisible on cold cache / slow network
  root_cause : CSS injecting Streamlit header suppression was inside the
               'if not items: return' guard. On cold cache, no ticker data
               loads → guard fires → CSS never injected → Streamlit header
               reappears and covers the ticker.
  fix        : CSS injected unconditionally BEFORE the data fetch block.
               Same CSS also baked into styles.py inject_css() as fallback.
  regression : R13 — verify CSS injection precedes data fetch in ticker fn

KI-004
  severity   : CRITICAL (app crash on startup)
  discovered : v5.9  (2026-03-18)
  fixed      : v5.9  (2026-03-18)
  file       : pages/home.py
  symptom    : NameError: name 'NEWS_FEEDS' is not defined (on every cold start)
  root_cause : Self-referencing list definition:
               NEWS_FEEDS = [NEWS_FEEDS.get("World", []), ...]
               Python evaluates the right side before the name is bound →
               NameError on first execution.
  fix        : Replaced with 6 explicit, validated RSS URL strings
  regression : R10 — validate all RSS URLs are explicit strings, no self-refs

KI-005
  severity   : HIGH
  discovered : v5.9  (2026-03-18)
  fixed      : v5.9  (2026-03-18)
  file       : market_data.py, global_intelligence.py,
               week_summary.py, dashboard.py  (5 locations)
  symptom    : TypeError or silent NaN: raw df["Close"].iloc[-1] returns a
               DataFrame row (Series) instead of float when yfinance returns
               a MultiIndex DataFrame (happens with multi-ticker downloads)
  root_cause : yfinance changed output format — "Close" column in multi-ticker
               downloads is a DataFrame, not a Series
  fix        : _safe_close() helper added to market_data.py; applied at all
               5 raw df["Close"] access points
  regression : R4 — scan for raw df["Close"] not guarded by _safe_close /
               isinstance / _cl = pattern

KI-006
  severity   : MEDIUM (cosmetic)
  discovered : v5.10 (2026-03-18) — spotted in screenshot
  fixed      : v5.10 (2026-03-18)
  file       : pages/home.py → render_homepage()
  symptom    : Version display shows "vv5.9" (double v prefix)
  root_cause : CURRENT_VERSION is already "v5.9" (stored with 'v' prefix in
               VERSION_LOG). Template had f'v{CURRENT_VERSION}' → "vv5.9"
  fix        : Changed to f'{CURRENT_VERSION}' (removed redundant literal 'v')
  regression : R11 — verify CURRENT_VERSION display string does not double-prefix

KI-007
  severity   : HIGH
  discovered : v5.10 (2026-03-18) — spotted in screenshot
  fixed      : v5.10 (2026-03-18)
  file       : pages/home.py → render_ticker_bar()
  symptom    : Ticker bar renders as multi-line wrapped block, not a fixed
               32px strip at the top of the page
  root_cause : position:fixed inside st.markdown() is trapped by Streamlit's
               stVerticalBlock stacking context (ancestor has overflow/transform
               constraints). overflow:hidden on .ticker-wrap has no effect
               inside the component tree.
  fix        : Rewrote render_ticker_bar() to use st.components.v1.html()
               with a <script> block: window.parent.document.body.prepend(div)
               This escapes Streamlit's DOM entirely.
  regression : R13 — verify 'window.parent' pattern present in home.py

KI-008
  severity   : MEDIUM (cosmetic)
  discovered : v5.10 (2026-03-18) — spotted in screenshot
  fixed      : v5.10 (2026-03-18)
  file       : styles.py → inject_css()
  symptom    : Streamlit MPA auto-generates a sidebar nav listing raw filenames:
               app / dashboard / global_intelligence / home / week_summary
  root_cause : When a pages/ directory exists, Streamlit renders
               [data-testid="stSidebarNav"] automatically
  fix        : Added CSS to hide stSidebarNav and stDeployButton in styles.py
  regression : R13 — verify stSidebarNav suppression in styles.py

KI-009
  severity   : HIGH (app error log)
  discovered : v5.11 (2026-03-18)
  fixed      : v5.11 (2026-03-18)
  file       : market_data.py (_ALLOWED_RSS_DOMAINS), pages/home.py, config.py
  symptom    : get_news:blocked_url · ValueError: Not in allowlist: feeds.bbci.co.uk
  root_cause : BBC RSS URLs added to NEWS_FEEDS in v5.9 but domain
               feeds.bbci.co.uk was never added to _ALLOWED_RSS_DOMAINS.
               Also: BBC and Reuters URLs used http:// (not https://)
               which safe_url() rejects as insecure.
  fix        : Added bbci.co.uk, bbc.co.uk, bbc.com to allowlist.
               Upgraded all http:// feed/news URLs to https://
  regression : R10 — verify all RSS URLs pass allowlist check
               R10 — verify no http:// feed URLs in codebase

KI-010
  severity   : HIGH (app crash on Global Intelligence page)
  discovered : v5.12 (2026-03-18)
  fixed      : v5.12 (2026-03-18)
  file       : pages/global_intelligence.py
  symptom    : NameError: name 'pd' is not defined
               (in _render_watchlist_badges at isinstance(df["Close"], pd.DataFrame))
  root_cause : _safe_close pattern (isinstance check) was applied to
               global_intelligence.py in v5.9, but 'import pandas as pd'
               was never added to that file's imports. The file previously
               had no pandas dependency.
  fix        : Added 'import pandas as pd' to global_intelligence.py
  regression : R5 — scan all files: if pd.X is used, 'pd' must be imported
               Pattern: check short-form module aliases (pd, np) across all files

KI-011
  severity   : HIGH (HTTP 404 on every TATAMOTORS.NS fetch)
  discovered : v5.13 (2026-03-18)
  fixed      : v5.13 (2026-03-18)
  file       : config.py (3 groups), pages/week_summary.py
  symptom    : HTTP Error 404: Quote not found for symbol: TATAMOTORS.NS
               "possibly delisted; no price data found"
  root_cause : Tata Motors completed a court-approved demerger effective
               October 1, 2025. TATAMOTORS.NS ceased to exist as a listed
               entity. It was split into:
               TMCV.NS (commercial vehicles) + TMPV.NS (passenger vehicles/EV)
  fix        : Replaced TATAMOTORS.NS → TMCV.NS in all 4 locations.
               Added TMPV.NS as a new entry in the 🚗 Auto & EV group.
  note       : Other India tickers verified: ZEEL.NS ✅  M&M.NS ✅
  regression : Periodic ticker audit recommended before each major release.
               No automated check possible (requires live Yahoo Finance query)

KI-012
  severity   : CRITICAL (blocks entire server, not just user session)
  discovered : v5.14 (2026-03-18) — design review
  fixed      : v5.14 (2026-03-18)
  file       : app.py → auto-refresh block
  symptom    : App freezes for 3 seconds every 3 seconds when auto-refresh ON.
               All users sharing the Streamlit process are blocked.
  root_cause : Auto-refresh was implemented as:
                 time.sleep(3) + st.rerun()  # polling loop
               time.sleep() in a Streamlit script blocks the ENTIRE server
               thread — not just the current user's session.
  fix        : Replaced with @st.fragment(run_every=1).
               Fragment ticks every 1 s — non-blocking, isolated from app tree.
               Full app rerun (st.rerun(scope="app")) only fires at 60 s boundary.
  regression : R7 — scan for time.sleep(N) where N >= 1 in non-test code

KI-013
  severity   : HIGH (StreamlitAPIException crash)
  discovered : v5.15 (2026-03-18)
  fixed      : v5.15 (2026-03-18)
  file       : app.py → _refresh_fragment()
  symptom    : StreamlitAPIException: Calling st.sidebar in a function
               wrapped with st.fragment is not supported.
  root_cause : Fragment used st.sidebar.markdown() (imperative form).
               Streamlit rule: inside a fragment, you cannot use the
               imperative st.sidebar.X form — must use context-inherited
               st.markdown() from within a 'with st.sidebar:' call site.
  fix        : Fragment definition unchanged. Call site moved INSIDE
               'with st.sidebar:' block. Inside fragment: st.markdown()
               replaces st.sidebar.markdown() — context is inherited.
  regression : R6 — scan for st.sidebar.X calls inside @st.fragment bodies

KI-014
  severity   : HIGH (TypeError crash when stock selected)
  discovered : v5.15.1 (2026-03-18)
  fixed      : v5.15.1 (2026-03-18)
  file       : pages/dashboard.py → render_dashboard()
  symptom    : TypeError: render_dashboard() got an unexpected keyword
               argument 'market_open'
  root_cause : PROCESS FAILURE — the fix (adding market_open param to
               render_dashboard signature) was applied to the in-memory FM
               dict during the regression validation run, but GSI_v5_15.zip
               was packaged BEFORE that fix was written back to FM.
               The shipped zip contained the old 3-param signature.
  fix        : Added market_open: bool = False to render_dashboard signature.
               Also backfilled _live_kpi_panel @st.fragment definition which
               suffered the same write-before-package gap.
  process_fix: Post-package zip-read verification step added: after writing
               the zip, re-open it and verify critical fields from actual
               bytes on disk (not from in-memory FM dict).
  regression : R-ZIP — after every package: re-read zip, re-run R12 against
               zip contents to confirm in-memory fixes were written.
               Never trust FM dict state after packaging.

KI-015
  severity   : CRITICAL (RecursionError / server crash)
  discovered : v5.15.2 (2026-03-18) — caught during regression suite authoring
  fixed      : v5.15.2 (2026-03-18)
  file       : pages/dashboard.py → _live_kpi_panel()
  note       : [entry reconstructed from R8b regression check + version log;
                no direct pre-fix source preserved — fixed before v5.15.2 log was cut]
  symptom    : RecursionError: maximum recursion depth exceeded
               (Streamlit server crash — all sessions affected)
               Triggered immediately on loading any stock while market is open.
  root_cause : _live_kpi_panel() was introduced in v5.15 as a @st.fragment for
               "partial UI refresh (dynamic sections only)". The initial
               implementation called _live_kpi_panel() inside its own body
               to "chain" the next KPI update — replicating a pattern from the
               pre-fragment version where the render function called the panel
               directly. With @st.fragment, run_every= already handles
               re-invocation automatically. The explicit self-call caused the
               fragment to recurse immediately every run, crashing the server.
  fix        : Removed the self-call from _live_kpi_panel() body.
               run_every parameter on @st.fragment decorator handles
               all periodic re-invocation — no self-call needed or valid.
  regression : R8b — scan all @st.fragment-decorated function bodies;
               raise failure if any body contains a call to itself
               (st.rerun() excluded — valid fragment call, not self-recursion)
               Covers: _refresh_fragment@app.py, _live_kpi_panel@dashboard.py,
                       _render_live_section@home.py

KI-016
  severity   : HIGH (stale state, wrong market context, blocked UI)
  discovered : v5.16 (2026-03-18)  — observed in prod screenshot
  fixed      : v5.16 (2026-03-18)
  file       : app.py → Market selectbox
  symptom    : Switching market (e.g. USA→India) shows "No results — try a
               different name or symbol." immediately, even with empty search.
               No stock can be selected until user manually clears the search box.
               Additionally: prev_ticker still points to old market's stock,
               nav_page stays "Dashboard", currency symbol is wrong for new market.
  root_cause : No on_change handler on the Market selectbox. When country changes,
               Streamlit reruns top-to-bottom but these keys are NEVER cleared:
                 stock_search  → retains previous market's query → "No results"
                 prev_ticker   → still points to old ticker → nav stays Dashboard
                 nav_page      → stays "Dashboard" → renders wrong market's stock
                 grp_sel       → old market group name → KeyError or silent wrong group
                 stk_sel       → old market stock name → wrong stock auto-selected
                 cb            → cache not busted → stale price data may serve
  fix        : Added _on_market_change() callback to Market selectbox via on_change=.
               Atomically clears: stock_search, prev_ticker, grp_sel, stk_sel,
               data_stale. Resets nav_page → "Home". Increments cb (cache bust).
               Market selectbox given key="market_sel" to support on_change.
  impact     : ALL market switches were affected. Severity HIGH because user has
               no clear affordance to recover — they must manually clear search.
  regression : R14 — verify on_change=_on_market_change on Market selectbox;
               verify all 6 stale keys are cleared in the handler body.


KI-017
  severity   : HIGH (TypeError crash on every Indian stock load)
  discovered : v5.17 (2026-03-18) — reported at runtime
  fixed      : v5.17 (2026-03-18)
  file       : pages/dashboard.py → _render_kpi_panel()
  symptom    : TypeError: _render_kpi_panel.<locals>._color() got an
               unexpected keyword argument 'tip'
               (raised on loading any stock with RSI / MACD / ADX KPIs)
  root_cause : Tooltip injection patch used regex _kpi\([^)]+label[^)]+\)
               to locate _kpi() calls. [^)]+ stops at the FIRST ')' it
               encounters — which is the closing paren of the nested _color()
               argument, not _kpi() itself. Result: tip= was injected into
               _color()'s argument list, not _kpi()'s.
  fix        : Replaced regex with a parenthesis-balanced matcher that counts
               ( and ) depth, only stopping when depth returns to 0 at the
               genuine outer ) of _kpi(). tip= now correctly appended as the
               last argument of _kpi(), after _color() is closed.
  regression : KI-017 check: verify no _color(..., tip=) pattern exists;
               all 9 _kpi() calls have tip= outside _color()

KI-018
  severity   : HIGH (KeyError crash on market switch)
  discovered : v5.17 (2026-03-18) — reported at runtime
  fixed      : v5.17 (2026-03-18)
  file       : app.py → sidebar group selectbox
  symptom    : KeyError: None
               app.py line 107: stock_map = mkt_grps[selected_grp]
  root_cause : _on_market_change() set st.session_state["grp_sel"] = None
               to clear the group selection. On the very next render,
               st.selectbox(key="grp_sel") reads None back from session_state
               and returns None before Streamlit can default to index 0.
               The existing code then executed mkt_grps[None] → KeyError.
  fix        : (1) _on_market_change() now uses st.session_state.pop("grp_sel")
               instead of = None — removes the key entirely so Streamlit
               resets the widget to index 0 automatically.
               (2) Defensive guard added: if selected_grp not in mkt_grps:
               selected_grp = grp_names[0]
  regression : R14.KI-016 — grp_sel cleared in handler; sidebar guard present

KI-019
  severity   : HIGH (KeyError crash after market switch then stock select)
  discovered : v5.17 (2026-03-18) — reported at runtime
  fixed      : v5.17 (2026-03-18)
  file       : app.py → sidebar stock selectbox
  symptom    : KeyError: None
               app.py line 118: selected_ticker = stock_map[chosen]
  root_cause : Same root cause as KI-018. _on_market_change() called
               st.session_state.pop("stk_sel") but the guard on the
               resulting selectbox value only checked:
                 if chosen != "— Select a stock —"
               When chosen is None (first render after pop), None != string
               evaluates True → stock_map[None] → KeyError.
               Additionally, search-path guard filtered[selected_label]
               had the same None-access vulnerability.
  fix        : All three selectbox-dependent access points hardened:
               (1) if chosen and chosen != "..." and chosen in stock_map
               (2) if selected_label and selected_label in filtered
               Both use explicit None check + membership check.
  regression : E-NONE — persona test P3 Market Switcher validates all
               paths through the sidebar after pop()

KI-020
  severity   : CRITICAL (StreamlitAPIException crash)
  discovered : v5.17 (2026-03-18) — reported at runtime
  fixed      : v5.17 (2026-03-18)
  file       : app.py → _refresh_fragment()
  symptom    : streamlit.errors.StreamlitAPIException:
               scope="fragment" can only be specified from
               @st.fragment-decorated functions during fragment reruns.
               (triggered by: enabling auto-refresh, then selecting a stock)
  root_cause : st.rerun(scope="fragment") is only valid when Streamlit's own
               fragment scheduler is re-running the fragment (i.e. a periodic
               fragment rerun triggered by run_every=). Selecting a new stock
               triggers a full-page rerun via auto-nav. During that full-page
               load, the fragment body executes as part of the main script —
               not as a scheduled fragment rerun — making scope="fragment"
               illegal at that point.
  fix        : Changed st.rerun(scope="fragment") → st.rerun() (no scope).
               st.rerun() from inside a fragment triggers a full-app rerun,
               which is the correct behaviour (refreshes chart data) and is
               valid in all execution contexts — both fragment reruns and
               full-page loads.
  note       : scope="fragment" would have only re-run the fragment itself
               (no data refresh). Plain st.rerun() is strictly better.
  regression : R13.KI-012 scoped_rerun check updated — now accepts
               st.rerun( in any form (with or without scope=)

# ──────────────────────────────────────────────────────────────────────────────
# KNOWN OPEN ISSUES (not yet fixed)
# ──────────────────────────────────────────────────────────────────────────────

KI-021
  severity   : HIGH (crash on brand-new IPO listings)
  discovered : v5.17 (2026-03-18) — persona test P5 edge case simulation
  fixed      : OPEN
  file       : forecast.py
  symptom    : numpy.linalg.LinAlgError: SVD did not converge
               (when a stock has < 2 rows of price history)
  root_cause : np.polyfit() requires at minimum 2 data points. A same-day
               IPO listing returns a single-row DataFrame. No length guard
               exists before the polyfit call.
  fix        : Add: if len(df) < lookback or len(df) < 2:
                        st.info("Insufficient price history for forecast")
                        return
               before every polyfit / regression call in forecast.py
  regression : Add R15 — verify polyfit calls are guarded by len(df) check
# ──────────────────────────────────────────────────────────────────────────────
# EXTERNAL / ENVIRONMENT ISSUES (not code bugs — documented for awareness)
# ──────────────────────────────────────────────────────────────────────────────

EXT-001
  type       : Yahoo Finance API
  symptom    : HTTP 401 Invalid Crumb
  cause      : yfinance session token (crumb) expires after inactivity
  behaviour  : safe_run() catches it, returns empty DataFrame — no crash
  resolution : Auto-resolves on next cache TTL (5 min). No code change needed.

EXT-002
  type       : Yahoo Finance API
  symptom    : HTTP 401 Unauthorized — User unable to access this feature
  cause      : Yahoo Finance restricts certain API endpoints (fundamentals,
               some ETFs) for non-premium accounts
  behaviour  : safe_run() catches it — no crash
  resolution : Expected behaviour. No code change needed.

EXT-003
  type       : Yahoo Finance data
  symptom    : HTTP 404 + "possibly delisted" for a valid ticker
  cause      : Ticker temporarily unavailable, or symbol changed due to
               corporate action (see KI-011 for permanent case)
  behaviour  : safe_run() catches it, returns empty DataFrame — no crash
  distinction: Transient → wait and retry. Permanent → update config.py.
               Check NSE/BSE announcements to distinguish.

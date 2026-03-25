#!/usr/bin/env python3
"""
regression.py — GSI Regression & Validation Suite
Run from project root: python3 regression.py
Each check references its KI-code from KNOWN_ISSUES_LOG.md.
"""
import re, ast, os, sys, zipfile
from urllib.parse import urlparse

PROJECT_FILES = [
    "config.py","version.py","app.py","utils.py","forecast.py","market_data.py","styles.py",
    "indicators.py","portfolio.py",
    "pages/home.py","pages/dashboard.py","pages/global_intelligence.py","pages/week_summary.py",
]

def load_files():
    FM = {}
    for fn in PROJECT_FILES:
        if os.path.exists(fn): FM[fn] = open(fn).read()
        else: print(f"WARNING: {fn} not found")
    return FM

_results = []
def chk(ref, label, passed, detail=""):
    _results.append((ref, label, passed, detail))

def run(FM):
    FM = {k: v for k, v in FM.items() if k in PROJECT_FILES}

    # R1 · Syntax ──────────────────────────────────────────────────────────────
    for fn, src in FM.items():
        try: ast.parse(src); chk("R1", "syntax:"+fn, True)
        except SyntaxError as e: chk("R1", "syntax:"+fn, False, f"L{e.lineno}: {e.msg}")

    # R2 · KI-001 deprecated Streamlit width/container args ────────────────────
    # Streamlit 1.43 rules (corrected):
    #   st.dataframe: use_container_width=True  ✅ VALID in 1.43
    #   st.dataframe: width='stretch'            ❌ INVALID in 1.43 (TypeError)
    #   st.plotly_chart: width='stretch'         ❌ INVALID — use config={'responsive':True}
    #   st.button(width=...)                     ❌ INVALID — no width param on button
    for fn, src in FM.items():
        lines = src.splitlines()
        hits = []
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith('#') or s.startswith('"') or s.startswith("'"):
                continue
            if 'notes' in l.lower() or ('version' in l.lower() and '{' in l):
                continue
            # Flag width='stretch' on dataframe (invalid in 1.43 — use use_container_width=True)
            if 'dataframe' in l and "width=" in l and ('stretch' in l or 'content' in l):
                hits.append(i+1)
            # Flag width='stretch' on plotly_chart
            if 'plotly_chart' in l and "width=" in l and 'stretch' in l:
                hits.append(i+1)
            # Flag width= on st.button (no width param in any version)
            if re.search(r'st\.button\(.*width\s*=', l):
                hits.append(i+1)
        chk("R2.KI-001", "ucw:"+fn, not hits, str(hits) if hits else "")

    # R3 · Bare except ─────────────────────────────────────────────────────────
    for fn, src in FM.items():
        bare = [i+1 for i,l in enumerate(src.splitlines()) if l.strip() == "except:"]
        chk("R3", "bare_except:"+fn, not bare, str(bare) if bare else "")

    # R4 · KI-005 unsafe raw df["Close"] ──────────────────────────────────────
    SAFE = ["_safe_close","isinstance","#","_cl = df[","cl = df[","val = df[",
            "c = df[","close = df["]
    for fn, src in FM.items():
        bad = [i+1 for i,l in enumerate(src.splitlines())
               if re.search(r'\b(df|d)\["Close"\]', l) and not any(g in l for g in SAFE)]
        chk("R4.KI-005", "raw_close:"+fn, not bad, str(bad) if bad else "")

    # R5 · KI-010 pd/np used but not imported ──────────────────────────────────
    for fn, src in FM.items():
        try: tree = ast.parse(src)
        except: continue
        imp = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names: imp.add(a.asname or a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for a in node.names: imp.add(a.asname or a.name)
        for short in ["pd", "np"]:
            if re.search(r"\b" + short + r"\.", src):
                chk("R5.KI-010", f"{short}_import:{fn}", short in imp,
                    "MISSING import!" if short not in imp else "")

    # R6 · KI-013 st.sidebar.X inside @st.fragment ─────────────────────────────
    for fn, src in FM.items():
        in_frag = False; hits = []
        for i, l in enumerate(src.splitlines(), 1):
            if "@st.fragment" in l: in_frag = True
            if in_frag and re.match(r"^[^\s]", l) and "@st.fragment" not in l and i > 1:
                in_frag = False
            if in_frag and "st.sidebar." in l: hits.append(i)
        chk("R6.KI-013", "sidebar_in_frag:"+fn, not hits, str(hits) if hits else "")

    # R7 · KI-012 blocking time.sleep ─────────────────────────────────────────
    for fn, src in FM.items():
        bad = [i+1 for i,l in enumerate(src.splitlines())
               if re.search(r"time\.sleep\(\s*[1-9]", l) and not l.strip().startswith("#")]
        chk("R7.KI-012", "blocking_sleep:"+fn, not bad, str(bad) if bad else "")

    # R8 · KI-002 entry points defined ────────────────────────────────────────
    EP = {
        "app.py": ["_is_market_open","_refresh_fragment","_on_market_change"],
        "pages/home.py": ["render_homepage","render_ticker_bar"],
        "pages/dashboard.py": ["render_dashboard","_live_price_tile","_render_kpi_panel",
                               "_render_header_static","_make_live_price_fragment",
                               "_make_live_kpi_fragment","_render_price_tile",
                               "_tab_forecast","_tab_insights","_detect_asset_class"],
        "pages/global_intelligence.py": ["render_global_intelligence"],
        "pages/week_summary.py": ["render_week_summary","_render_forecast_accuracy_report","render_market_overview","render_group_overview","_multi_asset_weekly_chart"],
        "styles.py": ["inject_css"],
        "utils.py": ["init_session_state","render_error_log","safe_run","log_error",
                     "safe_float","sanitise","sanitise_bold","responsive_cols","info_tip","section_title_with_tip"],
        "market_data.py": ["get_price_data","get_ticker_info","get_top_movers",
                           "get_news","_safe_close","get_live_price","get_intraday_chart_data"],
        "forecast.py": ["store_forecast","resolve_forecasts","render_forecast_accuracy",
                        "get_weekly_accuracy_report","get_pending_forecast_summary"],
            "portfolio.py": ["check_data_quality","compute_log_returns","winsorize_returns",
                        "bootstrap_scenarios","optimise_mean_cvar","compute_efficient_frontier",
                        "detect_stress_regime","check_regime_conflicts"],
        "indicators.py": ["compute_indicators","signal_score","compute_weinstein_stage",
                          "compute_elder_screens","compute_forecast","compute_unified_verdict"],
    }
    for fn, fns in EP.items():
        src = FM.get(fn, "")
        for f in fns:
            ok = bool(re.search(r"def\s+" + f + r"\b", src))
            chk("R8.KI-002", f"ep:{f}@{fn}", ok, "NOT DEFINED" if not ok else "")

    # R8b · KI-015 no @st.fragment body calls itself ───────────────────────────
    for fn, src in FM.items():
        lines = src.splitlines()
        i = 0
        while i < len(lines):
            if "@st.fragment" in lines[i]:
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("@"): j += 1
                if j < len(lines) and lines[j].strip().startswith("def "):
                    m = re.match(r"(\s*)def\s+(\w+)\s*\(", lines[j])
                    if m:
                        fn_indent = len(m.group(1))  # indentation of def line
                        fname     = m.group(2)
                        body_lines = []
                        k = j + 1
                        while k < len(lines):
                            stripped = lines[k].strip()
                            if stripped == "":          # blank line — keep scanning
                                body_lines.append(lines[k]); k += 1; continue
                            line_indent = len(lines[k]) - len(lines[k].lstrip())
                            if line_indent <= fn_indent: # back at/above def level
                                break
                            body_lines.append(lines[k]); k += 1
                        body = "\n".join(body_lines)
                        clean_body = re.sub(r"st\.rerun[^\n]*", "", body)
                        self_call  = bool(re.search(r"\b" + fname + r"\s*\(", clean_body))
                        chk("R8b.KI-015", f"no_self_recurse:{fname}@{fn}",
                            not self_call,
                            f"{fname}() calls itself!" if self_call else "")
            i += 1

    # R9 · KI-002 cross-file imports resolve ────────────────────────────────
    exports = {}
    for fn, src in FM.items():
        mod = fn.replace("/", ".").replace(".py", "")
        try: tree = ast.parse(src)
        except: continue
        exports[mod] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                exports[mod].add(node.name)
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name): exports[mod].add(t.id)
            elif isinstance(node, ast.AnnAssign):
                # Handles type-annotated assignments: MARKET_SESSIONS: dict = {...}
                if isinstance(node.target, ast.Name): exports[mod].add(node.target.id)
            elif isinstance(node, ast.ImportFrom):
                # Include re-exported names (e.g. config.py re-exports from version.py)
                for alias in node.names:
                    exports[mod].add(alias.asname or alias.name)
    for fn, src in FM.items():
        try: tree = ast.parse(src)
        except: continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and \
               any(node.module.startswith(m) for m in
                   ["config","utils","market_data","forecast","pages","styles"]):
                mf = node.module.replace(".", "/") + ".py"
                if mf not in FM: continue
                for alias in node.names:
                    ok = alias.name in exports.get(node.module, set())
                    chk("R9.KI-002", f"{alias.name}<-{node.module}", ok,
                        f"not in {mf}" if not ok else "")

    # R10 · KI-009 RSS allowlist + no http:// feeds ───────────────────────────
    md = FM.get("market_data.py", "")
    allow_raw = md.split("_ALLOWED_RSS_DOMAINS")[1].split("}")[0] if "_ALLOWED_RSS_DOMAINS" in md else ""
    allowlist = set(re.findall(r'"([\w\-.]+\.\w+)"', allow_raw))
    all_src = " ".join(FM.values())
    rss_urls = re.findall(r'"(https?://[^"]+(?:rss|feed)[^"]*)"', all_src)
    blocked = [u for u in set(rss_urls) if not any(
        (h := urlparse(u).netloc.lower().lstrip("www.")) == d or h.endswith("." + d)
        for d in allowlist)]
    chk("R10.KI-009", "rss_allowlist", not blocked, str(blocked) if blocked else "")
    http_bad = [u for u in re.findall(r'"http://[^"]+"', all_src)
                if any(k in u for k in ["feed","rss","news"])]
    chk("R10.KI-009", "no_http_feeds", not http_bad, str(http_bad) if http_bad else "")

    # R11 · KI-006/KI-011 version log + delisted tickers ─────────────────────
    # v5.16: VERSION_LOG moved to version.py; config.py re-exports it.
    cfg     = FM.get("config.py", "")
    ver_src = FM.get("version.py", cfg)  # fallback to config for pre-v5.16 repos
    entries = re.findall(r'{"version":\s*"([^"]+)"[^}]+}', ver_src)
    chk("R11", "version_log_min_20", len(entries) >= 20, str(len(entries)))
    # v5.16+: version.py defines CURRENT_VERSION = VERSION_LOG[-1]["version"]
    # pre-v5.16: config.py defined it inline
    chk("R11", "current_ver_dynamic",
        'VERSION_LOG[-1]["version"]' in ver_src or
        "CURRENT_VERSION = VERSION_LOG[-1][" in cfg)
    chk("R11.KI-011", "no_TATAMOTORS_live",
        not any("TATAMOTORS" in l
                for fn, src in FM.items() if fn.endswith(".py")
                for l in src.splitlines()
                if not l.strip().startswith("#")
                and not l.strip().startswith("{")
                and not l.strip().startswith("'")),
        "TATAMOTORS.NS found — delisted Oct 2025, use TMCV.NS/TMPV.NS")

    # R12 · KI-014 market_open param propagated ───────────────────────────────
    for fn, param in [("app.py","_is_market_open"),
                      ("pages/home.py","market_open"),
                      ("pages/dashboard.py","market_open"),
                      ("pages/global_intelligence.py","market_open")]:
        chk("R12.KI-014", f"{param}@{fn}", param in FM.get(fn,""),
            "MISSING" if param not in FM.get(fn,"") else "")

    # R13 · Design contracts ───────────────────────────────────────────────────
    app = FM.get("app.py", "")
    chk("R13.KI-013", "fragment_in_sidebar_ctx",  "_refresh_fragment()" in app)
    chk("R13.KI-003", "css_before_data_fetch",    "window.parent" in FM.get("pages/home.py",""))
    chk("R13.KI-008", "stSidebarNav_hidden",       "stSidebarNav" in FM.get("styles.py",""))
    chk("R13.KI-006", "no_double_v_prefix",        "f'v{CURRENT_VERSION}" not in FM.get("pages/home.py",""))
    chk("R13.KI-012", "scoped_rerun",
        # KI-020 (v5.17): scope="fragment" removed — plain st.rerun() is correct.
        # Check: st.rerun() is present AND scope="fragment" is absent.
        "st.rerun()" in app and 'scope="fragment"' not in app)
    chk("R13",        "data_stale_guard",           "data_stale" in app)
    chk("R13",        "manual_refresh_btn",         ("Refresh data" in app or "🔄" in app))


    # R14 · KI-016 market-switch state isolation ─────────────────────────────
    app = FM.get("app.py", "")
    chk("R14.KI-016", "on_change_market_selectbox", "on_change=_on_market_change" in app)
    stale_keys = ["stock_search", "prev_ticker", "grp_sel", "stk_sel", "data_stale"]
    handler_idx = app.find("def _on_market_change")
    handler_body = app[handler_idx:handler_idx+600] if handler_idx >= 0 else ""
    for k in stale_keys:
        chk("R14.KI-016", f"clears_{k}", k in handler_body,
            f"'{k}' not cleared in _on_market_change" if k not in handler_body else "")
    chk("R14.KI-016", "resets_nav_to_home", "nav_page" in handler_body and "Home" in handler_body)
    chk("R14.KI-016", "busts_cache_on_change", "cb" in handler_body and ("+ 1" in handler_body or "+= 1" in handler_body))

    # R15 · v5.18 live auto-refresh contracts ────────────────────────────────
    app = FM.get("app.py", "")
    db  = FM.get("pages/dashboard.py", "")
    md  = FM.get("market_data.py", "")
    # Fragment must be at module level — defined before 'with st.sidebar:'
    frag_idx    = app.find("@st.fragment")
    sidebar_idx = app.find("with st.sidebar:")
    chk("R15.v518", "fragment_before_sidebar",
        0 <= frag_idx < sidebar_idx,
        "fragment defined inside sidebar — timer will reset on every interaction")
    # market_open must be stored in session_state for fragment to read
    chk("R15.v518", "market_open_in_ss",
        "st.session_state.market_open = market_open" in app,
        "market_open not stored in session_state")
    # Manual auto_refresh toggle must be gone
    chk("R15.v518", "no_manual_toggle",
        "auto_refresh" not in app,
        "manual auto_refresh toggle still present — remove it")
    # Live price tile must NOT call st.rerun()
    tile_start = db.find("def _live_price_tile")
    tile_end   = db.find("return _live_price_tile", tile_start) if tile_start >= 0 else -1
    tile_body  = db[tile_start:tile_end] if tile_start >= 0 and tile_end >= 0 else ""
    chk("R15.v518", "no_rerun_in_price_tile",
        "st.rerun()" not in tile_body,
        "st.rerun() inside _live_price_tile — defeats fragment isolation")
    # get_live_price must have TTL=5
    chk("R15.v518", "live_price_ttl_5",
        "ttl=5" in md and "get_live_price" in md,
        "get_live_price TTL must be 5s")
    # get_intraday_chart_data must have TTL=60
    chk("R15.v518", "intraday_ttl_60",
        "ttl=60" in md and "get_intraday_chart_data" in md,
        "get_intraday_chart_data TTL must be 60s")
    # Intraday chart only renders when market open
    chk("R15.v518", "intraday_gated_by_market_open",
        "if market_open and ticker" in db,
        "intraday chart not gated by market_open")



    # R16 · v5.19 forecast engine + unified verdict contracts ─────────────────
    db  = FM.get("pages/dashboard.py", "")
    ind = FM.get("indicators.py", "")
    fc  = FM.get("forecast.py", "")
    ws  = FM.get("pages/week_summary.py", "")
    # polyfit must be gone from _tab_forecast
    chk("R16.v519", "no_polyfit_in_forecast",
        "np.polyfit" not in db[db.find("def _tab_forecast"):db.find("def _tab_compare")]
        if "def _tab_forecast" in db and "def _tab_compare" in db else True,
        "polyfit still in _tab_forecast — must be replaced by Historical Simulation")
    # new engine functions present
    chk("R16.v519", "compute_forecast_defined",        "def compute_forecast" in ind)
    chk("R16.v519", "compute_weinstein_defined",       "def compute_weinstein_stage" in ind)
    chk("R16.v519", "compute_elder_defined",           "def compute_elder_screens" in ind)
    chk("R16.v519", "compute_unified_verdict_defined", "def compute_unified_verdict" in ind)
    chk("R16.v519", "get_weekly_accuracy_report",      "def get_weekly_accuracy_report" in fc)
    chk("R16.v519", "weekly_report_in_week_summary",   "_render_forecast_accuracy_report" in ws)
    chk("R16.v519", "store_forecast_takes_simulation", "simulation: dict" in fc or "simulation=None" in fc)
    chk("R16.v519", "resolve_calibration_fields",      "in_p25_p75" in fc and "direction_correct" in fc)
    chk("R16.v519", "no_6m_12m_horizon",
        '"6M"' not in db[db.find("def _tab_forecast"):db.find("def _tab_compare")]
        if "def _tab_forecast" in db and "def _tab_compare" in db else True,
        "6M/12M horizon options still present — removed as statistically unreliable")

    # R17 · v5.20 header verdict + asset class contracts ─────────────────────
    db  = FM.get("pages/dashboard.py", "")
    cfg = FM.get("config.py", "")
    # Header must show verdict, not raw signal
    chk("R17.v520", "header_takes_verdict_param",
        "verdict=None" in db,
        "header still uses raw sig — verdict param missing")
    # Momentum score labelled pre-regime
    chk("R17.v520", "score_labelled_momentum",
        "Momentum: {score}/100" in db or "Momentum:" in db,
        "score not labelled as Momentum only")
    # Asset class detection defined
    chk("R17.v520", "detect_asset_class_defined",
        "def _detect_asset_class" in db)
    # P/E suppressed for non-equity
    chk("R17.v520", "pe_suppressed_non_equity",
        "show_fundamentals" in db and "P/E, P/B, ROE" in db,
        "P/E not suppressed for non-equity asset classes")
    # Verdict computed before header in render_dashboard
    rd_body = db[db.find("def render_dashboard"):]
    verdict_idx = rd_body.find("compute_unified_verdict")
    header_idx  = rd_body.find("_render_header_static(")
    chk("R17.v520", "verdict_before_header",
        0 < verdict_idx < header_idx,
        "verdict not computed before header renders")
    # _tab_insights receives pre-computed objects
    chk("R17.v520", "insights_accepts_precomputed",
        "stage: dict = None" in db and "verdict: dict = None" in db,
        "_tab_insights does not accept pre-computed stage/verdict")
    # New HELP_TEXT keys present
    for key in ["weinstein_stage", "elder_screen", "p_gain",
                "hist_sim", "conflict", "unified_verdict"]:
        chk("R17.v520", f"helptext_{key}", f'"{key}"' in cfg,
            f"HELP_TEXT missing key: {key}")

    # R18 · CLAUDE.md baseline sync ──────────────────────────────────────────
    # Compares CLAUDE.md count against GSI_Session.json manifest — NOT the
    # mid-run check count (which is incomplete when R18 executes).
    import re as _re, json as _json
    claude_md_path = "CLAUDE.md"
    session_path   = "GSI_Session.json"
    if os.path.exists(claude_md_path):
        claude_md_src = open(claude_md_path).read()
        # Get expected count from manifest
        expected_n = None
        if os.path.exists(session_path):
            try:
                _m   = _json.load(open(session_path))
                _exp = _m.get("regression", {}).get("expected_output", "")
                _hit = _re.findall(r"(\d+)", _exp)
                if _hit: expected_n = _hit[0]
            except Exception:
                pass
        matches = _re.findall(r"(\d+)/(\d+)\s+PASS", claude_md_src)
        if matches and expected_n:
            claude_n = matches[0][0]
            chk("R18", "claude_md_baseline_current",
                claude_n == expected_n,
                f"CLAUDE.md shows {claude_n} but manifest expects {expected_n} — update CLAUDE.md")
        elif matches:
            chk("R18", "claude_md_baseline_current",
                int(matches[0][0]) > 0,
                "CLAUDE.md regression count is zero or missing")
        else:
            chk("R18", "claude_md_baseline_current", False,
                "CLAUDE.md has no 'NNN/NNN PASS' line — add regression count")
    else:
        chk("R18", "claude_md_baseline_current", False,
            "CLAUDE.md not found in repo root")

    # R19 · v5.21 Phase 2 contracts ──────────────────────────────────────────
    db  = FM.get("pages/dashboard.py", "")
    ind = FM.get("indicators.py", "")
    # Debt suppression in unified_verdict
    chk("R19.v521", "debt_suppression_in_verdict",
        'asset_class == "debt"' in ind or "asset_class==" in ind,
        "compute_unified_verdict has no debt asset_class branch")
    chk("R19.v521", "rates_context_signal",
        "RATES CONTEXT" in ind,
        "RATES CONTEXT signal not defined for debt instruments")
    # Plain English header labels
    chk("R19.v521", "plain_english_aligned",
        "Trend and momentum agree" in db,
        "Header still shows 'All layers aligned' jargon")
    chk("R19.v521", "plain_english_conflict",
        "Momentum signal adjusted" in db,
        "Header still shows 'Score overridden by regime' jargon")
    # Debt KPI panel
    chk("R19.v521", "debt_kpi_branch_in_panel",
        'asset_class == "debt"' in db[db.find("def _render_kpi_panel"):
                                       db.find("def _make_live_kpi_fragment")],
        "_render_kpi_panel has no debt branch")
    # Dynamic chart subplots
    chk("R19.v521", "dynamic_chart_subplots",
        "_has_macd" in db and "_row_macd" in db,
        "_tab_charts still uses hardcoded 4-row subplot layout")
    # All 6 HELP_TEXT keys wired
    for key in ["weinstein_stage", "elder_screen", "hist_sim", "conflict"]:
        chk("R19.v521", f"helptext_{key}_wired",
            f"HELP_TEXT['{key}']" in db or f'HELP_TEXT["{key}"]' in db,
            f"HELP_TEXT['{key}'] not wired in dashboard.py")
    # asset_class passed to compute_unified_verdict
    chk("R19.v521", "asset_class_to_verdict",
        "asset_class=asset_class" in db,
        "asset_class not passed to compute_unified_verdict in render_dashboard")

    # R20 · v5.22 routing + new page functions ───────────────────────────────
    ap  = FM.get("app.py", "")
    ws  = FM.get("pages/week_summary.py", "")
    # 4-state routing in app.py
    chk("R20.v522", "view_mode_logic",
        "_view_mode" in ap,
        "app.py missing _view_mode routing logic")
    chk("R20.v522", "group_routing",
        "render_group_overview" in ap,
        "app.py not routing to render_group_overview")
    chk("R20.v522", "market_routing",
        "render_market_overview" in ap,
        "app.py not routing to render_market_overview")
    chk("R20.v522", "week_routing",
        "render_week_summary" in ap,
        "app.py not routing to render_week_summary")
    # New page functions in week_summary.py
    chk("R20.v522", "render_market_overview_defined",
        "def render_market_overview" in ws,
        "render_market_overview not defined in week_summary.py")
    chk("R20.v522", "render_group_overview_defined",
        "def render_group_overview" in ws,
        "render_group_overview not defined in week_summary.py")
    chk("R20.v522", "multi_asset_chart_defined",
        "def _multi_asset_weekly_chart" in ws,
        "_multi_asset_weekly_chart not defined in week_summary.py")
    chk("R20.v522", "imports_in_app",
        "render_market_overview" in ap and "render_group_overview" in ap,
        "new page functions not imported in app.py")

    # R21 · v5.23 portfolio allocator contracts ───────────────────────────────
    ws  = FM.get("pages/week_summary.py", "")
    pf  = FM.get("portfolio.py", "")
    chk("R21.v523", "portfolio_module_exists",
        bool(pf), "portfolio.py not in loaded files — add to PROJECT_FILES")
    chk("R21.v523", "cvxpy_guard",
        "CVXPY_AVAILABLE" in pf,
        "portfolio.py missing CVXPY_AVAILABLE guard — cvxpy may not be installed")
    chk("R21.v523", "winsorize_defined",
        "def winsorize_returns" in pf,
        "winsorize_returns not defined — HIGH/D3 fix missing")
    chk("R21.v523", "stress_regime_defined",
        "def detect_stress_regime" in pf,
        "detect_stress_regime not defined — CRITICAL/P1+M1 fix missing")
    chk("R21.v523", "conflict_check_defined",
        "def check_regime_conflicts" in pf,
        "check_regime_conflicts not defined — Layer 4 missing")
    chk("R21.v523", "data_quality_defined",
        "def check_data_quality" in pf,
        "check_data_quality not defined — HIGH/D1 fix missing")
    chk("R21.v523", "allocator_tab_in_week_summary",
        "_render_portfolio_allocator" in ws and "tab_alloc" in ws,
        "Portfolio Allocator tab not wired in render_group_overview")
    chk("R21.v523", "stress_check_before_allocation",
        "detect_stress_regime" in ws,
        "Stress regime check not called in week_summary — CRITICAL fix missing")
    chk("R21.v523", "conflict_check_in_week_summary",
        "check_regime_conflicts" in ws,
        "Layer 4 conflict check not called in week_summary")
    chk("R21.v523", "leverage_disclaimer",
        "leverage" in ws.lower() or "borrowed" in ws.lower(),
        "Leverage disclaimer missing from allocator UI — HIGH/P4 fix missing")

def verify_zip(zip_path: str):
    """R-ZIP · KI-014: Re-read packaged zip from disk and run full suite.
    Catches fixes applied to in-memory FM but not written to the zip."""
    print(f"\n── R-ZIP: verifying {zip_path} ──")
    if not os.path.exists(zip_path): print("  zip not found"); return
    with zipfile.ZipFile(zip_path) as zf:
        FM_zip = {n: zf.read(n).decode() for n in zf.namelist() if n.endswith(".py")}
    _results.clear()
    run(FM_zip)
    report()


def report():
    cats = {}
    for ref, lbl, p, d in _results:
        cats.setdefault(ref, [0, 0])
        cats[ref][0 if p else 1] += 1
    tp = sum(p for p, _ in cats.values())
    tf = sum(f for _, f in cats.values())
    print(f"\n  {'REF':<24} PASS FAIL")
    print("  " + "-" * 36)
    for ref, (p, f) in sorted(cats.items()):
        icon = "OK" if f == 0 else "!!"
        print(f"  [{icon}] {ref:<22} {p:>4} {f:>4}")
    print("  " + "-" * 36)
    print(f"  TOTAL: {tp} pass  {tf} fail  ({tp+tf} checks)")
    if tf:
        print("\nFAILURES:")
        for ref, lbl, p, d in _results:
            if not p: print(f"  FAIL [{ref}] {lbl}  ->  {d}")
    else:
        print(f"\n  ALL {tp+tf} CHECKS PASS")
    return tf


if __name__ == "__main__":
    FM = load_files()
    print(f"Loaded {len(FM)} files")
    run(FM)
    exit_code = report()
    for zname in ["GSI_v5_15_2.zip","GSI_v5_15_1.zip"]:
        if os.path.exists(zname):
            verify_zip(zname)
            break
    sys.exit(exit_code)
"""
regression.py — GSI Regression & Validation Suite
Run from project root: python regression.py
Each check references its KI-code from KNOWN_ISSUES_LOG.md.
"""
import re, ast, os, sys, zipfile
from urllib.parse import urlparse

PROJECT_FILES = [
    "config.py","app.py","utils.py","forecast.py","market_data.py","styles.py",
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

    # R2 · KI-001 use_container_width deprecated ───────────────────────────────
    for fn, src in FM.items():
        hits = [i+1 for i,l in enumerate(src.splitlines())
                if "use_container_width" in l
                and "=False" not in l          # =False is valid, only True deprecated
                and not l.strip().startswith("#")
                and not l.strip().startswith('"')
                and not l.strip().startswith("{")
                and not l.strip().startswith("'")]
        chk("R2.KI-001", "ucw:"+fn, not hits, str(hits) if hits else "")

    # R3 · Bare except ─────────────────────────────────────────────────────────
    for fn, src in FM.items():
        bare = [i+1 for i,l in enumerate(src.splitlines()) if l.strip() == "except:"]
        chk("R3", "bare_except:"+fn, not bare, str(bare) if bare else "")

    # R4 · KI-005 unsafe raw df["Close"] ──────────────────────────────────────
    SAFE = ["_safe_close","isinstance","#","_cl = df[","cl = df[","val = df["]
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
        "app.py": ["_is_market_open","_refresh_fragment"],
        "pages/home.py": ["render_homepage","render_ticker_bar","_render_live_section"],
        "pages/dashboard.py": ["render_dashboard","_live_kpi_panel","_render_kpi_panel"],
        "pages/global_intelligence.py": ["render_global_intelligence"],
        "pages/week_summary.py": ["render_week_summary"],
        "styles.py": ["inject_css"],
        "utils.py": ["init_session_state","render_error_log","safe_run","log_error",
                     "safe_float","sanitise","sanitise_bold","responsive_cols","info_tip","section_title_with_tip"],
        "market_data.py": ["get_price_data","get_ticker_info","get_top_movers",
                           "get_news","_safe_close"],
        "forecast.py": ["store_forecast","resolve_forecasts","render_forecast_accuracy"],
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
                    m = re.match(r"\s*def\s+(\w+)\s*\(", lines[j])
                    if m:
                        fname = m.group(1)
                        body_lines = []
                        k = j + 1
                        while k < len(lines) and (lines[k].startswith(" ") or
                                                    lines[k].startswith("\t") or
                                                    lines[k].strip() == ""):
                            body_lines.append(lines[k])
                            k += 1
                        body = "\n".join(body_lines)
                        body_no_rerun = re.sub(r"st\.rerun[^\n]*", "", body)
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
    cfg = FM.get("config.py", "")
    entries = re.findall(r'{"version":\s*"([^"]+)"[^}]+}', cfg)
    chk("R11", "version_log_min_20", len(entries) >= 20, str(len(entries)))
    chk("R11", "current_ver_dynamic", "CURRENT_VERSION = VERSION_LOG[-1][" in cfg)
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
    chk("R13.KI-012", "scoped_rerun",              ("st.rerun(scope=" in app))
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
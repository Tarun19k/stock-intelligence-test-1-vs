# ============================================================
#  Global Stock Intelligence Dashboard — v3.3 (Phase 1+2+3)
#  pip3 install streamlit yfinance feedparser plotly pandas numpy pytz requests
#  Run: python3 -m streamlit run app_v3_phase2_fix.py
# ============================================================

import time
import pytz
import json
import os
import warnings
import traceback
from collections import deque

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import feedparser

from plotly.subplots import make_subplots
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Stock Intelligence v3.5",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Version & Error Log (injected at top of app after imports) ───────────────
VERSION_LOG = [
    {"version": "v1.0", "date": "2026-02-28", "notes": "Initial build — India stocks, 5 KPIs"},
    {"version": "v2.0", "date": "2026-03-06", "notes": "USP layer: NLP sentiment, narrative detector, Monte Carlo ROI"},
    {"version": "v3.0", "date": "2026-03-10", "notes": "643 validated tickers across India/USA/Europe/China"},
    {"version": "v3.1", "date": "2026-03-10", "notes": "Phase 2: scrolling tickers, news feed, morning brief"},
    {"version": "v3.2", "date": "2026-03-10", "notes": "Live auto-refresh via st.fragment — no full page reload"},
    {"version": "v3.3", "date": "2026-03-10", "notes": "Phase 3: forecast accuracy tracking + auto-correction logic"},
    {"version": "v3.5", "date": "2026-03-11", "notes": "Phase 4-5: nav realign, global tickers, top movers, dashboard reorder"},
    {"version": "v4.1", "date": "2026-03-11", "notes": "Fully responsive UI — mobile/tablet/desktop CSS breakpoints + Plotly responsive config"},
]
CURRENT_VERSION = VERSION_LOG[-1]["version"]

if "app_error_log" not in st.session_state:
    st.session_state.app_error_log = deque(maxlen=50)
if "chatter_open"  not in st.session_state: st.session_state.chatter_open  = True
if "chatter_topic" not in st.session_state: st.session_state.chatter_topic = "Global Markets"
if "chatter_feeds" not in st.session_state: st.session_state.chatter_feeds = []



def _safe_close(df):
    """Return a clean 1-D float Series for Close prices, guarding MultiIndex."""
    if df is None or df.empty:
        return pd.Series(dtype=float)
    try:
        cl = df["Close"]
        if isinstance(cl, pd.DataFrame):
            cl = cl.iloc[:, 0]
        return cl.dropna().astype(float)
    except Exception:
        return pd.Series(dtype=float)

def responsive_cols(desktop: int, tablet: int = None, mobile: int = 1):
    """Return st.columns() appropriate for any screen — CSS handles stacking."""
    # We always render desktop columns; CSS media queries handle visual stacking
    return st.columns(desktop)


def log_error(context: str, exc: Exception):
    entry = {
        "time":    datetime.now().strftime("%H:%M:%S"),
        "context": context,
        "error":   type(exc).__name__,
        "detail":  str(exc)[:120],
        "trace":   traceback.format_exc()[-300:],
    }
    st.session_state.app_error_log.appendleft(entry)

def safe_run(fn, context="", default=None):
    try:
        return fn()
    except Exception as e:
        log_error(context, e)
        return default

# ─────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
body,.main{background:#0e1117;}
.kpi-card{background:linear-gradient(135deg,#1e2130,#252840);border-radius:12px;
  padding:14px 18px;margin:5px 0;border-left:4px solid #4f8ef7;}
.kpi-card.green{border-left-color:#00c853;}
.kpi-card.red{border-left-color:#ff1744;}
.kpi-card.yellow{border-left-color:#ffd600;}
.kpi-value{font-size:1.6rem;font-weight:800;color:#fff;}
.kpi-label{font-size:0.72rem;color:#9aa0b4;text-transform:uppercase;letter-spacing:1px;}
.kpi-delta{font-size:0.82rem;margin-top:3px;}
.kpi-help{font-size:0.72rem;color:#5c6380;margin-top:4px;font-style:italic;}
.section-title{font-size:1.15rem;font-weight:700;color:#c8cee8;margin:28px 0 10px;
  padding-bottom:6px;border-bottom:1px solid #1f2540;}
.insight-box{background:linear-gradient(135deg,#0d2137,#102040);
  border:1px solid #1e4060;border-radius:10px;padding:13px 17px;margin:7px 0;}
.action-box{background:linear-gradient(135deg,#0d2614,#0f2d17);
  border:1px solid #1a4d24;border-radius:10px;padding:13px 17px;margin:7px 0;}
.warn-box{background:linear-gradient(135deg,#2a1a00,#331f00);
  border:1px solid #5c3800;border-radius:10px;padding:13px 17px;margin:7px 0;}
.news-card{background:#1a1d2e;border-radius:8px;padding:11px 14px;margin:5px 0;
  border-left:3px solid #4f8ef7;}
.news-title{font-size:0.86rem;font-weight:600;color:#dde2f5;}
.news-meta{font-size:0.70rem;color:#6b7280;margin-top:3px;}
.news-sum{font-size:0.78rem;color:#8a91a8;margin-top:4px;}
.group-badge{background:#1a2035;border:1px solid #2d3a5e;border-radius:8px;
  padding:10px 14px;margin:4px 0;font-size:0.82rem;color:#9aa0b4;}
.graph-help{background:#12151f;border-left:3px solid #2d3a5e;border-radius:6px;
  padding:10px 14px;margin:8px 0;font-size:0.80rem;color:#7a82a0;}
.valid-badge{background:#0d2614;border:1px solid #1a4d24;border-radius:6px;
  padding:4px 10px;font-size:0.72rem;color:#4caf50;display:inline-block;margin-top:4px;}

/* ═══════════════════════════════════════════
   RESPONSIVE / DEVICE-FRIENDLY OVERRIDES
   Mobile  : ≤ 768px
   Tablet  : ≤ 1024px
   Desktop : > 1024px
═══════════════════════════════════════════ */

/* Force viewport scale on mobile */
@media screen and (max-width: 768px) {

    /* Stack Streamlit columns vertically */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* KPI tiles: smaller, full-width */
    .kpi-card {
        padding: 10px 12px !important;
        margin: 3px 0 !important;
    }
    .kpi-value  { font-size: 1.25rem !important; }
    .kpi-label  { font-size: 0.65rem !important; }
    .kpi-delta  { font-size: 0.72rem !important; }

    /* Section titles smaller */
    .section-title { font-size: 0.95rem !important; }

    /* News cards readable on small screens */
    .news-card    { padding: 9px 11px !important; }
    .news-title   { font-size: 0.82rem !important; }
    .news-meta    { font-size: 0.65rem !important; }
    .news-sum     { font-size: 0.72rem !important; }

    /* Insight / action boxes */
    .insight-box, .action-box, .warn-box {
        padding: 10px 12px !important;
        font-size: 0.80rem !important;
    }

    /* Group badge */
    .group-badge {
        padding: 8px 10px !important;
        font-size: 0.78rem !important;
    }

    /* Price ticker: slower scroll, smaller font */
    .ticker-scroll { animation-duration: 80s !important; }

    /* Plotly charts: reduce height on mobile */
    [data-testid="stPlotlyChart"] > div {
        height: 280px !important;
        min-height: 220px !important;
    }

    /* Sidebar narrower */
    [data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 80vw !important;
    }

    /* Buttons full width */
    [data-testid="stButton"] > button {
        width: 100% !important;
        font-size: 0.82rem !important;
        padding: 8px 12px !important;
    }

    /* Selectbox full width */
    [data-testid="stSelectbox"] {
        width: 100% !important;
    }

    /* Radio buttons wrap on mobile */
    [data-testid="stRadio"] > div {
        flex-wrap: wrap !important;
        gap: 6px !important;
    }

    /* Reduce main padding */
    .main .block-container {
        padding: 1rem 0.75rem !important;
        max-width: 100% !important;
    }

    /* Hero header font scaling */
    div[style*="font-size:2rem"]   { font-size: 1.4rem !important; }
    div[style*="font-size:1.85rem"]{ font-size: 1.3rem !important; }
    div[style*="font-size:1.6rem"] { font-size: 1.2rem !important; }
    div[style*="font-size:1.15rem"]{ font-size: 1.0rem !important; }
}

/* ── Tablet (769px – 1024px) ─────────────────────────────── */
@media screen and (min-width: 769px) and (max-width: 1024px) {

    [data-testid="column"] {
        min-width: 45% !important;
    }

    .kpi-value  { font-size: 1.4rem !important; }

    [data-testid="stPlotlyChart"] > div {
        height: 340px !important;
    }

    .main .block-container {
        padding: 1.2rem 1rem !important;
    }
}

/* ── Touch targets: universally bigger hit areas ─────────── */
@media (hover: none) and (pointer: coarse) {
    [data-testid="stButton"] > button {
        min-height: 44px !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSelectbox"] select,
    [data-testid="stMultiSelect"] {
        min-height: 44px !important;
    }
    [data-testid="stCheckbox"] label {
        min-height: 40px !important;
        display: flex !important;
        align-items: center !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  MARKET HOURS
# ─────────────────────────────────────────────────────────────
MARKET_SESSIONS = {
    "India":  {"tz": "Asia/Kolkata",    "open": (9, 15), "close": (15, 30)},
    "USA":    {"tz": "America/New_York","open": (9, 30), "close": (16,  0)},
    "Europe": {"tz": "Europe/London",   "open": (8,  0), "close": (16, 30)},
    "China":  {"tz": "Asia/Hong_Kong",  "open": (9, 30), "close": (16,  0)},
    "ETFs - India":   {"tz": "Asia/Kolkata",    "open": (9, 15), "close": (15, 30)},
    "ETFs - Global":  {"tz": "America/New_York", "open": (9, 30), "close": (16,  0)},
    "Commodities":    {"tz": "America/New_York", "open": (8,  0), "close": (17, 30)},
    "Debt & Rates":   {"tz": "America/New_York", "open": (8,  0), "close": (17,  0)},
    "Global Indices": {"tz": "Asia/Kolkata",     "open": (9, 15), "close": (15, 30)}
}

def is_market_open(country):
    sess = MARKET_SESSIONS.get(country)
    if not sess:
        return False
    tz  = pytz.timezone(sess["tz"])
    now = datetime.now(tz)
    if now.weekday() >= 5:
        return False
    t = (now.hour, now.minute)
    return sess["open"] <= t < sess["close"]

def market_status_label(country):
    sess    = MARKET_SESSIONS.get(country, {})
    tz      = pytz.timezone(sess.get("tz", "UTC"))
    now     = datetime.now(tz)
    is_open = is_market_open(country)
    local_t = now.strftime("%H:%M")
    day     = now.strftime("%a")
    return (f"🟢 OPEN  {local_t} {day}", "#00c853") if is_open else (f"🔴 CLOSED  {local_t} {day}", "#ff1744")

def next_open_label(country):
    sess  = MARKET_SESSIONS.get(country, {})
    tz    = pytz.timezone(sess.get("tz", "UTC"))
    now   = datetime.now(tz)
    oh, om = sess.get("open", (9, 0))
    for d in range(1, 8):
        nxt = now + timedelta(days=d)
        if nxt.weekday() < 5:
            return nxt.strftime(f"%a %d %b — {oh:02d}:{om:02d}")
    return "—"

# ── Phase 3: Forecast Accuracy Tracker ───────────────────────────────────────
FORECAST_STORE_FILE = "forecast_history.json"

def load_forecast_history():
    if os.path.exists(FORECAST_STORE_FILE):
        try:
            with open(FORECAST_STORE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_forecast_history(data: dict):
    try:
        with open(FORECAST_STORE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_error("save_forecast_history", e)

def store_forecast(ticker: str, horizon_days: int, forecast_price: float, current_price: float):
    """Save a forecast entry on the day it is made."""
    history = load_forecast_history()
    key = f"{ticker}_{horizon_days}d"
    if key not in history:
        history[key] = []
    entry = {
        "made_on":        datetime.now().strftime("%Y-%m-%d"),
        "due_on":         (datetime.now() + timedelta(days=horizon_days)).strftime("%Y-%m-%d"),
        "horizon_days":   horizon_days,
        "forecast_price": round(forecast_price, 2),
        "base_price":     round(current_price, 2),
        "actual_price":   None,
        "accuracy_pct":   None,
        "resolved":       False,
    }
    # Avoid duplicate for same day
    today = datetime.now().strftime("%Y-%m-%d")
    if not any(e["made_on"] == today for e in history[key]):
        history[key].append(entry)
        save_forecast_history(history)
    return history

def resolve_forecasts(ticker: str, current_price: float):
    """Check all pending forecasts whose due date has passed and compute accuracy."""
    history = load_forecast_history()
    today   = datetime.now().strftime("%Y-%m-%d")
    changed = False
    for key, entries in history.items():
        if not key.startswith(ticker + "_"):
            continue
        for e in entries:
            if not e["resolved"] and e["due_on"] <= today:
                actual        = current_price
                e["actual_price"] = round(actual, 2)
                pct_err       = abs(actual - e["forecast_price"]) / e["forecast_price"] * 100
                e["accuracy_pct"] = round(max(0, 100 - pct_err), 2)
                e["resolved"] = True
                changed = True
    if changed:
        save_forecast_history(history)
    return history

def compute_correction_factor(ticker: str, min_entries: int = 3) -> float:
    """
    Auto-correction logic:
    If mean accuracy < 95%, compute a scaling factor from resolved forecasts
    and apply it to new forecasts. Returns multiplier (1.0 = no correction).
    """
    history = load_forecast_history()
    resolved = []
    for key, entries in history.items():
        if not key.startswith(ticker + "_"):
            continue
        for e in entries:
            if e["resolved"] and e["actual_price"] and e["forecast_price"]:
                ratio = e["actual_price"] / e["forecast_price"]
                resolved.append(ratio)
    if len(resolved) < min_entries:
        return 1.0  # not enough data, no correction
    mean_accuracy = sum(
        max(0, 100 - abs(r - 1) * 100) for r in resolved
    ) / len(resolved)
    if mean_accuracy >= 95.0:
        return 1.0  # already accurate, no correction needed
    # Correction = mean of actual/forecast ratios
    correction = sum(resolved) / len(resolved)
    return round(correction, 4)

def get_accuracy_summary(ticker: str) -> dict:
    """Return accuracy stats for display."""
    history = load_forecast_history()
    all_resolved = []
    for key, entries in history.items():
        if not key.startswith(ticker + "_"):
            continue
        all_resolved += [e for e in entries if e["resolved"]]
    if not all_resolved:
        return {"count": 0, "mean_accuracy": None, "correction_factor": 1.0, "entries": []}
    accs   = [e["accuracy_pct"] for e in all_resolved if e["accuracy_pct"] is not None]
    mean_a = round(sum(accs) / len(accs), 2) if accs else None
    cf     = compute_correction_factor(ticker)
    return {"count": len(all_resolved), "mean_accuracy": mean_a,
            "correction_factor": cf, "entries": all_resolved[-10:]}

def render_forecast_accuracy(ticker: str, cur_sym: str):
    """Render the accuracy tracking panel inside the Forecast tab."""
    acc = get_accuracy_summary(ticker)
    st.markdown("### 📏 Forecast Accuracy Tracker")
    if acc["count"] == 0:
        st.info("No resolved forecasts yet for this stock. "
                "Accuracy data builds up over time as forecast due-dates pass.")
        return

    mean_a = acc["mean_accuracy"] or 0
    cf     = acc["correction_factor"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Resolved Forecasts", acc["count"])
    col2.metric("Mean Accuracy",      f"{mean_a:.1f}%",
                delta=f"{'✅ No correction needed' if mean_a >= 95 else '⚠️ Auto-correction ON'}")
    col3.metric("Correction Factor",  f"{cf:.4f}",
                delta="1.0000 = perfect" if cf == 1.0 else f"{'▲' if cf > 1 else '▼'} applied to forecasts")

    if mean_a < 95:
        st.warning(
            f"⚙️ **Auto-correction active** — past forecasts averaged **{mean_a:.1f}% accuracy** "
            f"(target: 95%). A correction factor of **{cf:.4f}×** is being applied to today's forecast."
        )
    else:
        st.success(f"✅ Forecast accuracy is **{mean_a:.1f}%** — above 95% threshold. No correction applied.")

    # History table
    rows = []
    for e in reversed(acc["entries"]):
        rows.append({
            "Made On":    e["made_on"],
            "Due On":     e["due_on"],
            "Forecast":   f"{cur_sym}{e['forecast_price']:,.2f}",
            "Actual":     f"{cur_sym}{e['actual_price']:,.2f}" if e["actual_price"] else "—",
            "Accuracy":   f"{e['accuracy_pct']:.1f}%" if e["accuracy_pct"] is not None else "—",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)


# ═══════════════════════════════════════════════════════════════════
#  GLOBAL INTELLIGENCE  —  Trends, Geopolitics & AI Impact Engine
# ═══════════════════════════════════════════════════════════════════
import streamlit.components.v1 as stc

GLOBAL_TOPICS = {
    "🔴 West Asia Conflict": {
        "color":    "#ff4444",
        "subtitle": "Geopolitical Crisis · Supply Chain · Consumer Impact",
        "overview": (
            "The ongoing conflict across West Asia is reshaping global trade routes, "
            "energy supply chains, and inflationary pressures — with second and third-order "
            "effects felt from crude oil desks in Mumbai to grocery shelves worldwide."
        ),
        "chain": [
            ("Active Conflict Zones",     "#7f0000", "Direct military engagement in Gaza, Lebanon, Red Sea"),
            ("Regional Destabilisation",  "#b71c1c", "Iran–Israel tensions, Houthi Red Sea attacks"),
            ("Oil & Energy Supply Risk",  "#c62828", "Strait of Hormuz risk premium, Brent spike"),
            ("Shipping Route Disruption", "#d32f2f", "Suez Canal diversions → +14 days transit → +30% freight"),
            ("Global Energy Inflation",   "#e53935", "Fuel, fertiliser, plastics cost surge"),
            ("Supply Chain Repricing",    "#ef5350", "Electronics, autos, agriculture inputs"),
            ("Consumer Goods Costs",      "#ff7043", "Edible oils, fuel, transport — basic needs impacted"),
        ],
        "market_sectors":   ["Energy", "Defense & Aerospace", "Shipping & Logistics", "FMCG", "Agri"],
        "rss": [
            "https://www.aljazeera.com/xml/rss/all.xml",
            "http://feeds.reuters.com/reuters/worldNews",
            "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        ],
        "india_impact": (
            "India imports ~87% of its crude oil. Every $10/bbl rise in Brent adds ~₹1.2L cr "
            "to the import bill, weakens INR ~50–80 paise, and pushes petrol/diesel up ₹2–4/litre. "
            "FMCG and logistics companies see direct margin compression."
        ),
        "watchlist": ["BPCL.NS","IOC.NS","ONGC.NS","HAL.NS","BEL.NS","MAZDOCK.NS"],
    },
    "🤖 AI & Job Markets": {
        "color":    "#4f8ef7",
        "subtitle": "Technology Disruption · Workforce Evolution · New Opportunities",
        "overview": (
            "Generative AI is compressing the automation curve from decades to years. "
            "White-collar roles in software, legal, finance, and media are being repriced. "
            "Simultaneously, new roles in AI oversight, prompt engineering, and human-AI "
            "collaboration are emerging faster than universities can respond."
        ),
        "chain": [
            ("Foundation Model Capabilities",  "#0d47a1", "GPT-5, Gemini 2, Claude 4 — reasoning at expert level"),
            ("Enterprise Adoption Wave",        "#1565c0", "70% of Fortune 500 deploying AI co-pilots by 2026"),
            ("Task-Level Automation",           "#1976d2", "Code gen, legal review, customer ops, data analysis"),
            ("Job Role Displacement",           "#1e88e5", "Entry-level IT, BPO, content, paralegal at risk"),
            ("Reskilling & New Roles",          "#2196f3", "AI trainers, ethics auditors, integration architects"),
            ("Productivity & GDP Gains",        "#42a5f5", "McKinsey: $4.4T annual value from GenAI"),
            ("Market Repricing",                "#64b5f6", "IT multiples shift — services vs platforms diverge"),
        ],
        "market_sectors":   ["IT Services", "Cloud & SaaS", "EdTech", "Robotics", "Semiconductors"],
        "rss": [
            "https://feeds.feedburner.com/TechCrunch",
            "https://www.artificialintelligence-news.com/feed/",
            "https://techcrunch.com/feed/",
        ],
        "india_impact": (
            "India's $250B IT services sector — employing 5.4M people — faces structural repricing. "
            "TCS, Infosys, Wipro are pivoting from headcount-led to AI-led delivery. "
            "Near-term: margin expansion. Medium-term: 20–30% headcount reduction risk in "
            "legacy service lines. New hires skewed toward AI/ML by 3:1 ratio."
        ),
        "watchlist": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","PERSISTENT.NS","LTIM.NS"],
    },
}

NEXT_STEPS_AI = [
    ("📚 Upskill Immediately",
     "Python + LLM APIs (OpenAI, Gemini). 3 months of consistent learning creates a "
     "defensible skill moat. Free resources: fast.ai, Deeplearning.ai, Hugging Face.",
     "#00c853"),
    ("💼 Audit Your Role",
     "Identify which 40% of your daily tasks could be AI-assisted. Build that tool yourself — "
     "it makes you the expert instead of the disrupted.",
     "#4f8ef7"),
    ("📈 Invest in the Infrastructure",
     "AI demand runs on semiconductors (NVDA, TSM), cloud (MSFT Azure, AWS, GCP), and "
     "data pipelines. Platform winners compound faster than service providers.",
     "#ff9800"),
    ("🌐 Follow the Hiring Signal",
     "Track job postings weekly for AI roles in your sector. A 3x spike in a domain is a "
     "leading indicator of where value is migrating — both as a career and investment signal.",
     "#e040fb"),
    ("🛡️ Diversify Income Streams",
     "AI makes knowledge productisable. Build one passive asset: a course, a tool, a niche "
     "newsletter. These compound while your primary income remains intact.",
     "#00bcd4"),
]

def fetch_topic_news(feeds: list, max_n: int = 8) -> list:
    """Pull live headlines from RSS feeds for a given topic."""
    articles = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:max_n]:
                articles.append({
                    "title":   e.get("title","")[:120],
                    "link":    e.get("link","#"),
                    "source":  feed.feed.get("title","")[:30],
                    "summary": (e.get("summary","") or "")[:180],
                    "date":    e.get("published","")[:16],
                })
            if len(articles) >= max_n * 2: break
        except Exception as ex:
            log_error(f"fetch_topic_news:{url[:40]}", ex)
    return articles[:max_n]

def render_impact_chain(chain: list, color_title: str):
    """Renders a horizontal cascade of impact nodes."""
    nodes_html = ""
    for i, (label, color, tooltip) in enumerate(chain):
        arrow = (
            f"<div style='color:#4b6080;font-size:1.1rem;align-self:center;"
            f"padding:0 2px;'>→</div>"
        ) if i < len(chain) - 1 else ""
        nodes_html += (
            f"<div title='{tooltip}' style='background:{color}22;border:1px solid {color};"
            f"border-radius:10px;padding:8px 12px;min-width:110px;max-width:140px;"
            f"text-align:center;cursor:help;flex-shrink:0;'>"
            f"<div style='font-size:0.70rem;color:{color};font-weight:700;'>{label}</div>"
            f"<div style='font-size:0.62rem;color:#6b7a90;margin-top:3px;'>{tooltip[:40]}…</div>"
            f"</div>{arrow}"
        )
    st.markdown(
        f"<div style='overflow-x:auto;'>"
        f"<div style='display:flex;align-items:stretch;gap:6px;padding:12px 4px;"
        f"min-width:max-content;'>{nodes_html}</div></div>",
        unsafe_allow_html=True
    )

def render_next_steps_ai():
    """Render personalised AI next-step cards."""
    st.markdown("### 🎯 What You Should Do Next")
    cols = st.columns(len(NEXT_STEPS_AI))
    for col, (title, body, color) in zip(cols, NEXT_STEPS_AI):
        col.markdown(
            f"<div style='background:{color}12;border:1px solid {color}44;"
            f"border-radius:12px;padding:14px;height:220px;'>"
            f"<div style='font-weight:900;color:{color};font-size:0.88rem;"
            f"margin-bottom:8px;'>{title}</div>"
            f"<div style='font-size:0.76rem;color:#9aa0b4;line-height:1.5;'>{body}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

def render_watchlist_badges(tickers: list, cur_sym: str, cb: int):
    """Show live mini price badges for a topic watchlist."""
    st.markdown("##### 📌 Related Stocks to Watch")
    cols = st.columns(min(len(tickers), 6))
    for col, sym in zip(cols, tickers):
        try:
            d = safe_run(lambda: yf.download(sym, period="2d", interval="1d",
                         auto_adjust=True, progress=False), f"watchlist:{sym}", pd.DataFrame())
            if d is not None and not d.empty and len(d) >= 2:
                d.columns = [c[0] if isinstance(c,tuple) else c for c in d.columns]
                lp=float(_safe_close(d).iloc[-1]) if not _safe_close(d).empty else 0
                pp = float(d["Close"].iloc[-2])
                chg = (lp - pp) / pp * 100 if pp else 0
                clr = "#00c853" if chg >= 0 else "#ff4444"
                arr = "▲" if chg >= 0 else "▼"
                name = sym.replace(".NS","").replace(".BO","")
                col.markdown(
                    f"<div style='background:#0d1117;border:1px solid {clr}44;"
                    f"border-radius:8px;padding:8px;text-align:center;'>"
                    f"<div style='font-size:0.72rem;color:#6b7a90;'>{name}</div>"
                    f"<div style='font-size:0.90rem;font-weight:800;color:#fff;'>{cur_sym}{lp:,.0f}</div>"
                    f"<div style='font-size:0.74rem;color:{clr};'>{arr}{abs(chg):.1f}%</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        except Exception as ex:
            log_error(f"watchlist_badge:{sym}", ex)

def render_global_intelligence(cur_sym: str, cb: int):
    """Full Global Intelligence page renderer."""
    st.markdown(
        "<div style='font-size:1.6rem;font-weight:900;color:#c8d6f0;"
        "margin-bottom:4px;'>🌍 Global Intelligence Centre</div>"
        "<div style='font-size:0.84rem;color:#4b6080;margin-bottom:20px;'>"
        "Real-time geopolitical & technology trends · Impact chains · Market linkages · "
        "Worldmonitor live feed</div>",
        unsafe_allow_html=True
    )

    # ── WorldMonitor embedded iframe ──────────────────────────────────────────
    with st.expander("🗺️ WorldMonitor Live — Interactive Global Events Map", expanded=True):
        st.caption("Live global event data · Use controls to explore conflicts, economic zones & risk regions.")
        stc.html("""
<div id="wm-wrap" style="width:100%;height:570px;position:relative;">
  <iframe id="wm-frame" src="https://worldmonitor.app"
    style="width:100%;height:570px;border:none;border-radius:10px;"
    allow="fullscreen" referrerpolicy="no-referrer">
  </iframe>
  <div id="wm-fallback" style="display:none;position:absolute;inset:0;
    background:#0d1117;border:1px solid #1f2d40;border-radius:10px;
    display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;">
    <div style="font-size:1.1rem;font-weight:700;color:#c8d6f0;">🗺️ WorldMonitor</div>
    <div style="font-size:0.82rem;color:#6b7a90;text-align:center;max-width:320px;">
      The site has restricted embedded loading (X-Frame-Options policy).<br>
      Open it directly in a new tab for the full interactive experience.
    </div>
    <a href="https://worldmonitor.app" target="_blank"
      style="background:#4f8ef7;color:#fff;padding:10px 28px;border-radius:8px;
      font-weight:700;font-size:0.88rem;text-decoration:none;border:none;cursor:pointer;">
      🌐 Open WorldMonitor in New Tab
    </a>
  </div>
</div>
<script>
  (function() {
    var iframe = document.getElementById("wm-frame");
    var fallback = document.getElementById("wm-fallback");
    var timer = setTimeout(function() {
      // If iframe hasn't loaded content after 4s, assume blocked
      try {
        var doc = iframe.contentDocument || iframe.contentWindow.document;
        if (!doc || doc.body === null || doc.body.innerHTML === "") {
          iframe.style.display = "none";
          fallback.style.display = "flex";
        }
      } catch(e) {
        // Cross-origin error = iframe loaded a real page (good) OR was blocked
        // Check readyState via postMessage is not possible cross-origin
        // So we show fallback on any cross-origin exception
        iframe.style.display = "none";
        fallback.style.display = "flex";
      }
    }, 4000);
    iframe.onload = function() { clearTimeout(timer); };
  })();
</script>
""", height=580)

    st.markdown("---")

    # ── Topic selector tabs ───────────────────────────────────────────────────
    topic_names = list(GLOBAL_TOPICS.keys())
    gt1, gt2 = st.tabs(topic_names)

    for gtab, topic_key in zip([gt1, gt2], topic_names):
        topic = GLOBAL_TOPICS[topic_key]
        with gtab:
            # Header
            st.markdown(
                f"<div style='background:{topic['color']}0f;border-left:4px solid {topic['color']};"
                f"border-radius:0 12px 12px 0;padding:14px 20px;margin-bottom:16px;'>"
                f"<div style='font-size:1.1rem;font-weight:900;color:{topic['color']};'>"
                f"{topic_key}</div>"
                f"<div style='font-size:0.80rem;color:#9aa0b4;margin-top:4px;'>"
                f"{topic['subtitle']}</div>"
                f"<div style='font-size:0.82rem;color:#c8d6f0;margin-top:8px;line-height:1.6;'>"
                f"{topic['overview']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

            # Impact chain
            st.markdown("##### 🔗 Impact Cascade Chain")
            st.caption("Hover each node for detail · Scroll horizontally to see full chain")
            render_impact_chain(topic["chain"], topic["color"])
            st.markdown("")

            # India-specific impact
            col_india, col_sectors = st.columns([3, 2])
            with col_india:
                st.markdown("##### 🇮🇳 India Market Impact")
                st.markdown(
                    f"<div class='insight-box' style='border-left-color:{topic['color']};'>"
                    f"{topic['india_impact']}</div>",
                    unsafe_allow_html=True
                )
            with col_sectors:
                st.markdown("##### 📊 Affected Sectors")
                for s in topic["market_sectors"]:
                    st.markdown(
                        f"<span style='background:{topic['color']}18;border:1px solid "
                        f"{topic['color']}44;border-radius:20px;padding:3px 12px;"
                        f"font-size:0.78rem;color:{topic['color']};margin:3px;display:inline-block;'>"
                        f"{s}</span>",
                        unsafe_allow_html=True
                    )

            # Watchlist badges
            st.markdown("")
            render_watchlist_badges(topic["watchlist"], cur_sym, cb)
            st.markdown("")

            # Live news feed for this topic
            st.markdown(f"##### 📰 Latest Headlines")
            with st.spinner("Fetching live news…"):
                articles = safe_run(
                    lambda: fetch_topic_news(topic["rss"], max_n=8),
                    f"topic_news:{topic_key}", []
                ) or []

            if articles:
                nc = st.columns(2)
                for i, a in enumerate(articles):
                    with nc[i % 2]:
                        st.markdown(
                            f"<div class='news-card'>"
                            f"<div class='news-title'>"
                            f"<a href='{a['link']}' target='_blank' "
                            f"style='color:#7eb3ff;text-decoration:none;'>{a['title']}</a>"
                            f"</div>"
                            f"<div class='news-meta'>🗞️ {a['source']} &nbsp;|&nbsp; 🕐 {a['date']}</div>"
                            f"<div class='news-sum'>{a['summary']}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
            else:
                st.info("Live news feed loading… Check your connection or try again shortly.")

            # AI-specific: next steps panel
            if topic_key == "🤖 AI & Job Markets":
                st.markdown("---")
                render_next_steps_ai()

            # ── Live chatter pane for this topic ──────────────────────────
            st.session_state.chatter_topic = topic_key
            st.session_state.chatter_feeds = topic.get("rss", [])
            gi_chatter_open = st.session_state.get("chatter_open", True)

            _gcol1, _gcol2 = st.columns([8, 1])
            with _gcol2:
                btn_lbl = "✕ Feed" if gi_chatter_open else "💬 Feed"
                if st.button(btn_lbl, key=f"gi_toggle_{topic_key}",
                             help="Toggle live chatter feed for this topic",
                             width='stretch'):
                    st.session_state.chatter_open = not gi_chatter_open
                    st.rerun()

            if gi_chatter_open:
                st.markdown("---")
                st.markdown("#### 📡 Live Topic Chatter")
                render_chatter_pane(
                    topic_key,
                    topic.get("rss", []),
                    cb,
                    height=520
                )




# ─────────────────────────────────────────────────────────────
#  LIVE CHATTER PANE
# ─────────────────────────────────────────────────────────────
def render_chatter_pane(topic_key: str, rss_feeds: list, cb: int, height: int = 560):
    """Expandable/collapsable live-streaming update pane for a topic."""
    articles = safe_run(
        lambda: fetch_topic_news(rss_feeds, max_n=14),
        f"chatter:{topic_key}", []
    ) or []
    accent = ["#4f8ef7","#00c853","#ff9800","#e040fb","#26c6da","#ffca28","#ef5350","#66bb6a"]
    cards  = ""
    for idx, a in enumerate(articles[:12]):
        acol = accent[idx % len(accent)]
        delay = idx * 0.18
        t = str(a.get("title",""))[:90].replace("<","&lt;").replace(">","&gt;")
        s = str(a.get("summary",""))[:110].replace("<","&lt;").replace(">","&gt;")
        src_ = str(a.get("source","")).replace("<","&lt;")
        dt   = str(a.get("date","")).replace("<","&lt;")
        lnk  = str(a.get("link","#"))
        cards += (
            f"<div style='background:#080f1e;border-left:3px solid {acol};"
            f"border-radius:0 8px 8px 0;padding:10px 12px;margin-bottom:8px;"
            f"opacity:0;animation:slideIn 0.45s ease {delay:.2f}s forwards;'>"
            f"<div style='font-size:0.63rem;color:#3d5272;margin-bottom:4px;'>"
            f"🕐 {dt} · 🗞️ {src_}</div>"
            f"<a href='{lnk}' target='_blank' style='font-size:0.76rem;font-weight:700;"
            f"color:{acol};text-decoration:none;line-height:1.45;display:block;"
            f"margin-bottom:4px;'>{t}</a>"
            f"<div style='font-size:0.68rem;color:#4a5a70;line-height:1.55;'>{s}…</div>"
            f"</div>"
        )
    if not cards:
        cards = ("<div style='text-align:center;padding:40px 20px;color:#3d5272;'>"
                 "<div style='font-size:2rem;margin-bottom:8px;'>📡</div>"
                 "<div style='font-size:0.78rem;'>Fetching live updates…</div></div>")
    stc.html(f"""
<style>
  @keyframes slideIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
  ::-webkit-scrollbar{{width:4px}}
  ::-webkit-scrollbar-track{{background:#060f1e}}
  ::-webkit-scrollbar-thumb{{background:#1a2d45;border-radius:4px}}
</style>
<div style='background:linear-gradient(180deg,#060f1e,#04090f);border:1px solid #0d2a50;
  border-radius:12px;height:{height}px;display:flex;flex-direction:column;font-family:system-ui;'>
  <div style='padding:10px 14px;border-bottom:1px solid #0d2a50;
    display:flex;align-items:center;justify-content:space-between;flex-shrink:0;'>
    <div style='display:flex;align-items:center;gap:8px;'>
      <span style='width:7px;height:7px;background:#00c853;border-radius:50%;
        display:inline-block;animation:pulse 1.6s infinite;'></span>
      <span style='font-size:0.68rem;font-weight:700;color:#4b6080;
        text-transform:uppercase;letter-spacing:1.3px;'>Live Feed</span>
    </div>
    <div style='font-size:0.70rem;color:#2a3d55;'>{len(articles)} updates</div>
  </div>
  <div style='padding:8px 14px;flex-shrink:0;'>
    <div style='background:#4f8ef718;border:1px solid #4f8ef744;border-radius:20px;
      padding:4px 12px;display:inline-block;
      font-size:0.70rem;font-weight:700;color:#4f8ef7;'>📡 {topic_key}</div>
  </div>
  <div style='flex:1;overflow-y:auto;padding:4px 10px 12px 10px;'>{cards}</div>
</div>
""", height=height + 12)


# ─────────────────────────────────────────────────────────────
#  STOCK PICKS — SCORING ENGINE + RENDERER
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def _compute_stock_scores(tickers_tuple: tuple, cb: int) -> list:
    """Batch-score tickers on 5 technical axes. Returns list of scored dicts."""
    results = []
    for ticker, name in tickers_tuple[:35]:
        try:
            df = get_price_data(ticker, "1y", cache_buster=cb)
            if df is None or df.empty or len(df) < 60:
                continue
            df = compute_indicators(df)
            if df.empty:
                continue
            latest = df.iloc[-1]
            price  = safe_float(latest.get("Close", 0))
            if price <= 0:
                continue
            rsi    = safe_float(latest.get("RSI",      50))
            macd   = safe_float(latest.get("MACD",      0))
            macd_s = safe_float(latest.get("MACD_S",    0))
            sma50  = safe_float(latest.get("SMA50",  price))
            sma200 = safe_float(latest.get("SMA200", price))
            bb_u   = safe_float(latest.get("BB_upper", price * 1.05))
            bb_l   = safe_float(latest.get("BB_lower", price * 0.95))
            adx    = safe_float(latest.get("ADX",       20))
            vol    = safe_float(latest.get("Volume",     0))
            vol_ma = safe_float(latest.get("Volume_MA", vol))
            vol_ratio = vol / vol_ma if vol_ma > 0 else 1.0
            bb_pct    = (price - bb_l) / (bb_u - bb_l) if (bb_u - bb_l) > 0 else 0.5

            chg1d=(price/safe_float(_safe_close(df).iloc[-2])-1)*100 if len(_safe_close(df))>=2 else 0
            chg1m=(price/safe_float(_safe_close(df).iloc[-22])-1)*100 if len(_safe_close(df))>=22 else 0

            score   = 0
            signals = []

            # ── RSI (0-25 pts) ────────────────────────────────────────────────
            if rsi < 30:
                score += 25; signals.append(("🟢", "Oversold — Reversal Signal"))
            elif rsi < 45:
                score += 20; signals.append(("🟢", "RSI Recovery Zone"))
            elif rsi < 60:
                score += 12; signals.append(("🟡", "RSI Neutral-Bullish"))
            elif rsi < 70:
                score += 8;  signals.append(("🟡", "RSI Approaching Overbought"))

            # ── MACD (0-20 pts) ───────────────────────────────────────────────
            if macd > macd_s and macd > 0:
                score += 20; signals.append(("🟢", "MACD Bullish Crossover"))
            elif macd > macd_s:
                score += 14; signals.append(("🟢", "MACD Recovering"))
            else:
                score += 2

            # ── Trend / SMA (0-20 pts) ────────────────────────────────────────
            if price > sma50 > sma200:
                score += 20; signals.append(("🟢", "Above SMA50 & SMA200 — Uptrend"))
            elif price > sma50:
                score += 12; signals.append(("🟡", "Above SMA50"))
            elif price > sma200:
                score += 6;  signals.append(("🟡", "Above SMA200"))
            elif sma50 > sma200:
                score += 10; signals.append(("🟡", "Pullback in Uptrend — Value Entry"))

            # ── Bollinger Bands (0-15 pts) ────────────────────────────────────
            if bb_pct < 0.15:
                score += 15; signals.append(("🟢", "Price Near Lower BB — Buy Zone"))
            elif bb_pct < 0.35:
                score += 8;  signals.append(("🟡", "Lower BB Quarter"))

            # ── Volume (0-10 pts) ─────────────────────────────────────────────
            if vol_ratio > 1.5:
                score += 10; signals.append(("🟢", "Volume Surge — Accumulation"))
            elif vol_ratio > 1.2:
                score += 5;  signals.append(("🟡", "Above-Average Volume"))

            # ── ADX Trend Strength (0-10 pts) ─────────────────────────────────
            if adx > 30:
                score += 10; signals.append(("🟢", "Strong Trend (ADX > 30)"))
            elif adx > 20:
                score += 4;  signals.append(("🟡", "Moderate Trend"))

            if score < 35:
                continue

            # ── Horizon categorisation ────────────────────────────────────────
            macd_bull   = macd > macd_s
            above_sma50 = price > sma50
            if score >= 65 and macd_bull and above_sma50 and 35 <= rsi <= 68:
                horizon        = "3M"
                horizon_reason = "Strong near-term momentum with confirmed trend"
            elif score >= 50 and (macd_bull or above_sma50) and rsi > 30:
                horizon        = "6M"
                horizon_reason = "Trend building — medium-term accumulation"
            else:
                horizon        = "12M+"
                horizon_reason = "Value / recovery thesis — long-term conviction play"

            confidence = ("STRONG BUY" if score >= 72 else
                          "BUY"        if score >= 58 else "WATCH")
            conf_color = ("#00c853" if score >= 72 else
                          "#4f8ef7" if score >= 58 else "#ff9800")

            results.append({
                "ticker": ticker, "name": name, "price": price,
                "chg1d": chg1d, "chg1m": chg1m,
                "score": score, "horizon": horizon,
                "horizon_reason": horizon_reason,
                "signals": signals[:4],
                "confidence": confidence, "conf_color": conf_color,
            })
        except Exception:
            continue
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def render_stock_picks(country_tickers: dict, cur_sym: str, cb: int):
    """Flash section: AI-scored buy picks by horizon (3M / 6M / 12M+)."""
    st.markdown("---")

    # ── Section header with live pulse ───────────────────────────────────────
    stc.html("""
<style>
  @keyframes livePulse{0%,100%{opacity:1;box-shadow:0 0 0 rgba(0,200,83,0)}
    50%{opacity:.85;box-shadow:0 0 16px rgba(0,200,83,.35)}}
  @keyframes cardSlide{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  @keyframes scoreGlow{0%,100%{color:#00c853}50%{color:#66ffaa}}
</style>
<div style="background:linear-gradient(135deg,#060f1e,#071525);
  border:1px solid #0d3050;border-radius:14px;padding:14px 22px;
  display:flex;align-items:center;gap:14px;">
  <div style="width:10px;height:10px;background:#00c853;border-radius:50%;
    animation:livePulse 1.8s infinite;flex-shrink:0;"></div>
  <div>
    <div style="font-size:0.65rem;color:#3d5272;text-transform:uppercase;
      letter-spacing:1.6px;margin-bottom:3px;">AI-Scored · Live Tracked · Technical Analysis</div>
    <div style="font-size:1.1rem;font-weight:900;color:#c8d6f0;">
      ⚡ Stocks to Buy — Intelligence Picks</div>
  </div>
  <div style="margin-left:auto;background:#00c85318;border:1px solid #00c85344;
    border-radius:8px;padding:5px 14px;font-size:0.70rem;color:#00c853;font-weight:700;
    animation:livePulse 1.8s infinite;">LIVE SIGNALS</div>
</div>
""", height=82)

    # ── Score tickers ─────────────────────────────────────────────────────────
    sample = tuple(list(country_tickers.items())[:35])
    with st.spinner("Scanning market for buy signals…"):
        picks = safe_run(lambda: _compute_stock_scores(sample, cb), "stock_picks", []) or []

    picks_3m  = [p for p in picks if p["horizon"] == "3M"][:6]
    picks_6m  = [p for p in picks if p["horizon"] == "6M"][:6]
    picks_12m = [p for p in picks if p["horizon"] == "12M+"][:6]

    # ── Horizon tabs ──────────────────────────────────────────────────────────
    tab3, tab6, tab12 = st.tabs([
        f"⚡ 3 Months  ({len(picks_3m)})",
        f"📈 6 Months  ({len(picks_6m)})",
        f"🚀 12 Months+  ({len(picks_12m)})",
    ])

    for tab, plist, label, accent, delay_base in [
        (tab3,  picks_3m,  "3-Month Momentum Plays",  "#00c853", 0.00),
        (tab6,  picks_6m,  "6-Month Trend Builders",  "#4f8ef7", 0.06),
        (tab12, picks_12m, "Long-Term Value Recovery", "#ff9800", 0.12),
    ]:
        with tab:
            if not plist:
                st.info(f"No strong {label} signals at the moment. Market data refreshes every 15 min.")
                continue

            st.caption(
                f"📊 {label} · {len(plist)} pick{'s' if len(plist)!=1 else ''} · "
                f"Scored: RSI · MACD · Trend (SMA) · Bollinger Bands · Volume · ADX"
            )

            cols = st.columns(min(len(plist), 3))
            for idx, p in enumerate(plist):
                with cols[idx % 3]:
                    chg_col = "#00c853" if p["chg1d"] >= 0 else "#ef5350"
                    arrow   = "▲" if p["chg1d"] >= 0 else "▼"
                    s_col   = ("#00c853" if p["score"] >= 72 else
                               "#4f8ef7" if p["score"] >= 58 else "#ff9800")
                    sigs_html = "".join(
                        f"<div style='font-size:0.67rem;color:#6a7a90;"
                        f"margin:2px 0;line-height:1.4;'>{s[0]} {s[1]}</div>"
                        for s in p["signals"]
                    )
                    anim_delay = f"{delay_base + idx * 0.10:.2f}s"
                    name_safe  = str(p["name"])[:24]

                    st.markdown(
                        f"<div style='background:#080f1e;border:1px solid #0d2a50;"
                        f"border-top:3px solid {accent};border-radius:10px;"
                        f"padding:14px 15px;margin-bottom:12px;"
                        f"opacity:0;animation:cardSlide 0.4s ease {anim_delay} forwards;'>"

                        # ── Name + score ──────────────────────────────────────
                        f"<div style='display:flex;justify-content:space-between;"
                        f"align-items:flex-start;margin-bottom:10px;'>"
                        f"<div>"
                        f"<div style='font-size:0.80rem;font-weight:900;color:#c8d6f0;"
                        f"line-height:1.3;'>{name_safe}</div>"
                        f"<div style='font-size:0.63rem;color:#3d5272;margin-top:2px;'>"
                        f"{p['ticker']}</div>"
                        f"</div>"
                        f"<div style='text-align:right;'>"
                        f"<div style='font-size:0.70rem;font-weight:900;color:{s_col};"
                        f"animation:scoreGlow 2s infinite;'>Score {p['score']}/100</div>"
                        f"<div style='font-size:0.63rem;color:{p['conf_color']};"
                        f"font-weight:700;margin-top:2px;background:{p['conf_color']}15;"
                        f"border-radius:4px;padding:1px 6px;display:inline-block;'>"
                        f"{p['confidence']}</div>"
                        f"</div></div>"

                        # ── Price ─────────────────────────────────────────────
                        f"<div style='background:#040c18;border-radius:6px;"
                        f"padding:8px 10px;margin-bottom:10px;'>"
                        f"<div style='font-size:1.0rem;font-weight:900;color:#e8f0fe;'>"
                        f"{cur_sym}{p['price']:,.1f}</div>"
                        f"<div style='font-size:0.66rem;color:{chg_col};margin-top:2px;'>"
                        f"{arrow} {abs(p['chg1d']):.2f}% today"
                        f"&nbsp;&nbsp;|&nbsp;&nbsp;1M: {p['chg1m']:+.1f}%</div>"
                        f"</div>"

                        # ── Signal tags ───────────────────────────────────────
                        f"<div style='margin-bottom:10px;'>{sigs_html}</div>"

                        # ── Horizon reason ────────────────────────────────────
                        f"<div style='background:{accent}10;border-left:3px solid {accent};"
                        f"border-radius:0 6px 6px 0;padding:6px 10px;"
                        f"font-size:0.66rem;color:{accent};line-height:1.45;'>"
                        f"⏱ {p['horizon_reason']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

# ─────────────────────────────────────────────────────────────
#  TOP MOVERS — dedicated real-time Gainers / Losers panel
# ─────────────────────────────────────────────────────────────
def render_top_movers(
    country_tickers: dict,
    cur_sym: str,
    cb: int,
    market_open: bool = False,
):
    """Real-time Top Gainers / Losers with live/close-of-day badge."""
    sample  = tuple(list(country_tickers.items())[:40])
    movers  = safe_run(
        lambda: get_ticker_prices(sample, max_n=40, cache_buster=cb),
        "top_movers", []
    ) or []
    gainers = sorted([m for m in movers if m["chg"] > 0], key=lambda x: -x["chg"])[:5]
    losers  = sorted([m for m in movers if m["chg"] < 0], key=lambda x:  x["chg"])[:5]

    badge = (
        "<span style='background:#00c85318;border:1px solid #00c853;border-radius:12px;"
        "padding:2px 10px;font-size:0.68rem;color:#00c853;font-weight:700;'>🟢 LIVE</span>"
        if market_open else
        "<span style='background:#6b728018;border:1px solid #6b7280;border-radius:12px;"
        "padding:2px 10px;font-size:0.68rem;color:#6b7280;'>📌 Close of Day</span>"
    )
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:12px;margin:16px 0 12px;'>"
        f"<span style='font-size:1.05rem;font-weight:900;color:#c8d6f0;'>📊 Market Movers</span>"
        f"{badge}</div>",
        unsafe_allow_html=True,
    )
    col_g, col_l = st.columns(2)

    def _card(item, accent, arrow):
        return (
            f"<div style='background:#060f1e;border:1px solid #0d2a50;"
            f"border-left:3px solid {accent};border-radius:8px;"
            f"padding:8px 12px;margin-bottom:6px;'>"
            f"<div style='font-size:0.76rem;font-weight:700;color:#c8d6f0;'>"
            f"{item['name']}"
            f"<span style='color:#3d5272;font-size:0.64rem;margin-left:6px;'>"
            f"{item['sym']}</span></div>"
            f"<div style='display:flex;justify-content:space-between;margin-top:3px;'>"
            f"<span style='color:#e8f0fe;font-weight:800;'>{cur_sym}{item['price']:,.2f}</span>"
            f"<span style='color:{accent};font-weight:700;'>"
            f"{arrow} {abs(item['chg']):.2f}%</span></div></div>"
        )

    with col_g:
        st.markdown(
            "<div style='font-size:0.80rem;font-weight:700;color:#00c853;margin-bottom:8px;'>"
            "🟢 Top Gainers</div>", unsafe_allow_html=True
        )
        for g in gainers:
            st.markdown(_card(g, "#00c853", "▲"), unsafe_allow_html=True)
        if not gainers:
            st.caption("No gainers data yet.")

    with col_l:
        st.markdown(
            "<div style='font-size:0.80rem;font-weight:700;color:#ef5350;margin-bottom:8px;'>"
            "🔴 Top Losers</div>", unsafe_allow_html=True
        )
        for l in losers:
            st.markdown(_card(l, "#ef5350", "▼"), unsafe_allow_html=True)
        if not losers:
            st.caption("No losers data yet.")


# ─────────────────────────────────────────────────────────────
#  HOMEPAGE
# ─────────────────────────────────────────────────────────────
def render_homepage(cb: int):
    """Dashboard homepage — global snapshot, index overview, quick-access cards."""
    now_ist = datetime.now(pytz.timezone("Asia/Kolkata"))

    # ── Chatter toggle button (top-right) ─────────────────────────────────
    chatter_open = st.session_state.get("chatter_open", True)
    _htop1, _htop2 = st.columns([8, 1])
    with _htop2:
        lbl = "✕ Feed" if chatter_open else "💬 Feed"
        if st.button(lbl, key="hp_chatter_toggle",
                     help="Toggle live global updates feed",
                     width='stretch'):
            st.session_state.chatter_open = not chatter_open
            st.rerun()

    # ── Two-column layout: main content | chatter pane ──────────────────────
    if chatter_open:
        _hmain, _hchat = st.columns([3.2, 1.2])
    else:
        _hmain = st.container()
        _hchat = None

    with _hmain:

     st.markdown(
         f"<div style='background:linear-gradient(135deg,#060f1e,#0a1628);"
         f"border-radius:16px;padding:28px 32px;margin-bottom:22px;"
         f"border:1px solid #0d2a50;'>"
         f"<div style='font-size:0.72rem;color:#4b6080;letter-spacing:1.5px;"
         f"text-transform:uppercase;'>Market Intelligence Platform</div>"
         f"<div style='font-size:2rem;font-weight:900;color:#c8d6f0;margin-top:6px;'>"
         f"Good {'Morning' if now_ist.hour < 12 else 'Afternoon' if now_ist.hour < 17 else 'Evening'} 👋</div>"
         f"<div style='font-size:0.86rem;color:#5070a0;margin-top:6px;'>"
         f"{now_ist.strftime('%A, %d %B %Y  •  %H:%M IST')}</div>"
         f"<div style='display:flex;gap:10px;margin-top:16px;flex-wrap:wrap;'>"
         f"<span style='background:#00c85318;border:1px solid #00c853;border-radius:20px;"
         f"padding:4px 14px;font-size:0.78rem;color:#00c853;'>📡 Live Data</span>"
         f"<span style='background:#4f8ef718;border:1px solid #4f8ef7;border-radius:20px;"
         f"padding:4px 14px;font-size:0.78rem;color:#4f8ef7;'>🧠 AI-Powered Analysis</span>"
         f"<span style='background:#ff980018;border:1px solid #ff9800;border-radius:20px;"
         f"padding:4px 14px;font-size:0.78rem;color:#ff9800;'>🌍 Global Intelligence</span>"
         f"</div></div>",
         unsafe_allow_html=True
     )

     # ── Quick-access feature cards ─────────────────────────────────────────────
     st.markdown("#### 🚀 Quick Access")
     c1, c2, c3 = st.columns([1, 1, 1], gap="medium")
     cards = [
         (c1, "📊 Investor's Dashboard",
          "Live prices · 10 KPIs · Technical charts · Forecast · Compare · Insights",
          "#4f8ef7",
          "643 validated tickers · India, USA, Europe, China"),
         (c2, "🌍 Global Intelligence",
          "West Asia conflict impact chain · AI & Job market disruption · Live news",
          "#00c853",
          "WorldMonitor map · Geopolitical & tech trend analysis"),
         (c3, "🔮 Forecast Engine",
          "Trend regression · Monte Carlo simulation · Auto-correction when accuracy < 95%",
          "#ff9800",
          "Forecast accuracy tracked & logged per stock"),
     ]
     for col, title, desc, color, sub in cards:
         with col:
             st.markdown(
                 f"<div style='background:{color}0d;border:1px solid {color}44;"
                 f"border-radius:12px;padding:18px;height:160px;'>"
                 f"<div style='font-weight:900;color:{color};font-size:0.92rem;"
                 f"margin-bottom:8px;'>{title}</div>"
                 f"<div style='font-size:0.78rem;color:#c8d6f0;line-height:1.6;"
                 f"margin-bottom:8px;'>{desc}</div>"
                 f"<div style='font-size:0.68rem;color:#4b6080;'>{sub}</div>"
                 f"</div>",
                 unsafe_allow_html=True
             )

     st.markdown("---")

     # ── Global indices snapshot ────────────────────────────────────────────────
     st.markdown("#### 🌐 Global Indices Snapshot")
     INDEX_MAP = {
         "NIFTY 50":   "^NSEI",  "SENSEX":     "^BSESN",
         "S&P 500":    "^GSPC",  "NASDAQ":     "^IXIC",
         "DAX":        "^GDAXI", "FTSE 100":   "^FTSE",
         "Hang Seng":  "^HSI",   "Nikkei 225": "^N225",
     }
     idx_cols = st.columns(min(len(INDEX_MAP), 6), gap="small")
     for col, (name, sym) in zip(idx_cols, INDEX_MAP.items()):
         try:
             d = safe_run(
                 lambda s=sym: yf.download(s, period="2d", interval="1d",
                              auto_adjust=True, progress=False),
                 f"idx:{sym}", pd.DataFrame()
             )
             if d is not None and not d.empty and len(d) >= 2:
                 d.columns = [c[0] if isinstance(c,tuple) else c for c in d.columns]
                 lp=float(_safe_close(d).iloc[-1]) if not _safe_close(d).empty else 0
                 pp = float(d["Close"].iloc[-2])
                 chg = (lp - pp) / pp * 100 if pp else 0
                 clr  = "#00c853" if chg >= 0 else "#ff4444"
                 arr  = "▲" if chg >= 0 else "▼"
                 with col:
                     st.markdown(
                         f"<div style='background:#0d1117;border:1px solid {clr}33;"
                         f"border-radius:10px;padding:10px 8px;text-align:center;'>"
                         f"<div style='font-size:0.66rem;color:#6b7a90;'>{name}</div>"
                         f"<div style='font-size:0.92rem;font-weight:900;color:#fff;"
                         f"margin:4px 0;'>{lp:,.0f}</div>"
                         f"<div style='font-size:0.74rem;color:{clr};font-weight:700;'>"
                         f"{arr}{abs(chg):.2f}%</div>"
                         f"</div>",
                         unsafe_allow_html=True
                     )
         except Exception as e:
             log_error(f"homepage_idx:{sym}", e)

     st.markdown("---")

     # ── Today's top stories (global RSS) ──────────────────────────────────────
     st.markdown("#### 📰 Today's Top Stories")
     feeds = [
         "http://feeds.reuters.com/reuters/topNews",
         "http://feeds.bbci.co.uk/news/business/rss.xml",
         "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
     ]
     stories = safe_run(lambda: fetch_topic_news(feeds, max_n=6), "homepage_news", []) or []
     if stories:
         nc = st.columns(3)
         for i, a in enumerate(stories[:6]):
             with nc[i % 3]:
                 st.markdown(
                     f"<div class='news-card'>"
                     f"<div class='news-title'>"
                     f"<a href='{a['link']}' target='_blank' "
                     f"style='color:#7eb3ff;text-decoration:none;'>{a['title']}</a></div>"
                     f"<div class='news-meta'>🗞️ {a['source']} | 🕐 {a['date']}</div>"
                     f"<div class='news-sum'>{a['summary']}</div>"
                     f"</div>",
                     unsafe_allow_html=True
                 )
     else:
         st.info("Loading top stories…")

    # ── Real-time Market Movers ──────────────────────────────────────────
    st.markdown("---")
    _hp_open = is_market_open(country) if country in MARKET_SESSIONS else False
    render_top_movers(country_tickers, cur_sym, cb, _hp_open)

    # ── Chatter pane (right column) ────────────────────────────────────────
    if chatter_open and _hchat is not None:
        with _hchat:
            topic = st.session_state.get("chatter_topic", "Global Markets")
            feeds = st.session_state.get("chatter_feeds", []) or [
                "http://feeds.reuters.com/reuters/topNews",
                "http://feeds.bbci.co.uk/news/world/rss.xml",
                "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
            ]
            render_chatter_pane(topic, feeds, cb, height=820)

# ─────────────────────────────────────────────────────────────
#  STATIC DATA
# ─────────────────────────────────────────────────────────────
TICKER_FILE = "validated_tickers.json"

@st.cache_data(ttl=86400, show_spinner=False)
def load_validated_tickers():
    if os.path.exists(TICKER_FILE):
        with open(TICKER_FILE) as f:
            return json.load(f)
    return {}

NEWS_FEEDS = {
    "India":  [("Economic Times","https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
               ("Moneycontrol","https://www.moneycontrol.com/rss/marketsnews.xml"),
               ("Business Standard","https://www.business-standard.com/rss/markets-106.rss"),
               ("LiveMint","https://www.livemint.com/rss/markets")],
    "USA":    [("MarketWatch","https://feeds.marketwatch.com/marketwatch/topstories/"),
               ("Reuters","https://feeds.reuters.com/reuters/businessNews"),
               ("CNBC","https://www.cnbc.com/id/10001147/device/rss/rss.html")],
    "Europe": [("Reuters","https://feeds.reuters.com/reuters/businessNews"),
               ("FT","https://www.ft.com/rss/home")],
    "China":  [("SCMP","https://www.scmp.com/rss/1/feed"),
               ("Reuters","https://feeds.reuters.com/reuters/businessNews")],
    "ETFs - India":   [("Moneycontrol", "https://www.moneycontrol.com/rss/marketsnews.xml"),
                       ("ET Markets",   "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms")],
    "ETFs - Global":  [("MarketWatch",  "https://feeds.marketwatch.com/marketwatch/topstories"),
                       ("Reuters",      "https://feeds.reuters.com/reuters/businessNews")],
    "Commodities":    [("Reuters",      "https://feeds.reuters.com/reuters/businessNews"),
                       ("MarketWatch",  "https://feeds.marketwatch.com/marketwatch/topstories")],
    "Debt & Rates":   [("Reuters",      "https://feeds.reuters.com/reuters/businessNews"),
                       ("MarketWatch",  "https://feeds.marketwatch.com/marketwatch/topstories")],
    "Global Indices": [("Reuters",      "https://feeds.reuters.com/reuters/worldNews"),
                       ("ET Markets",   "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms")],
    "World":          [("Al Jazeera",   "https://www.aljazeera.com/xml/rss/all.xml"),
                       ("BBC World",    "http://feeds.bbci.co.uk/news/world/rss.xml"),
                       ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml"),
                       ("Times of India","https://timesofindia.indiatimes.com/rssfeeds/296589292.cms")],
    "Tech":           [("TechCrunch",   "https://feeds.feedburner.com/TechCrunch"),
                       ("TC Alt",       "https://techcrunch.com/feed/"),
                       ("AI News",      "https://www.artificialintelligence-news.com/feed/")]
}

INDICES = {
    "India":  {"NIFTY 50":"^NSEI","SENSEX":"^BSESN","NIFTY Bank":"^NSEBANK","NIFTY IT":"^CNXIT"},
    "USA":    {"S&P 500":"^GSPC","NASDAQ":"^IXIC","Dow Jones":"^DJI","Russell 2000":"^RUT"},
    "Europe": {"Euro Stoxx 50":"^STOXX50E","FTSE 100":"^FTSE","DAX":"^GDAXI","CAC 40":"^FCHI"},
    "China":  {"Hang Seng":"^HSI","Shanghai":"000001.SS"},
}

CURRENCY = {"India": "₹", "USA": "$", "Europe": "€", "China": "HK$",
    "ETFs - India":   "₹",
    "ETFs - Global":  "$",
    "Commodities":    "$",
    "Debt & Rates":   "$",
    "Global Indices": "pts"
}

GROUPS = {
    "India": {
        "⭐ Core 50 – Liquid Leaders": {
            "description": "India's 50 most liquid blue-chips.",
            "risk": "Moderate", "horizon": "1–3 years",
            "names": ["Reliance Industries","TCS","HDFC Bank","Infosys","ICICI Bank",
                      "Bharti Airtel","SBI","Wipro","Bajaj Finance","Kotak Mahindra Bank",
                      "HUL","Maruti Suzuki","Adani Ports","Asian Paints","Axis Bank",
                      "Bajaj Auto","BPCL","Britannia","Cipla","Coal India",
                      "Divi's Lab","Dr Reddy's","Eicher Motors","Grasim","HCL Technologies",
                      "Hero MotoCorp","Hindalco","HDFC Life","IndusInd Bank","ITC",
                      "JSW Steel","L&T","LTIMindtree","M&M","Nestle India",
                      "NTPC","ONGC","Power Grid","SBI Life","Sun Pharma",
                      "Tata Consumer","Tata Motors","Tata Steel","Tech Mahindra","Titan",
                      "UltraTech Cement","UPL","Shree Cement","Trent","Pidilite"]},
        "🚀 Growth Champions": {
            "description": "High-growth mid and large caps.",
            "risk": "High", "horizon": "1–3 years",
            "names": ["Zomato","Nykaa","Dixon Technologies","Trent","Persistent Systems",
                      "Coforge","LTIMindtree","Mphasis","Bajaj Finance","ICICI Bank",
                      "Bharti Airtel","PB Fintech","Angel One","IDFC First Bank","Apollo Hospitals"]},
        "🏦 Banking & Finance": {
            "description": "Top banks and financial companies.",
            "risk": "Moderate", "horizon": "1–2 years",
            "names": ["HDFC Bank","ICICI Bank","SBI","Kotak Mahindra Bank","Axis Bank",
                      "Bajaj Finance","IndusInd Bank","IDFC First Bank","Federal Bank",
                      "Bank of Baroda","PNB","Canara Bank","SBI Life","HDFC Life","RBL Bank"]},
        "💻 Digital & Tech": {
            "description": "IT giants and digital platforms.",
            "risk": "Moderate", "horizon": "2–3 years",
            "names": ["TCS","Infosys","Wipro","HCL Technologies","Tech Mahindra",
                      "LTIMindtree","Mphasis","Persistent Systems","Coforge",
                      "Zomato","Nykaa","Paytm","PB Fintech","Angel One","Dixon Technologies"]},
        "🏗️ Infra & Capex Plays": {
            "description": "Beneficiaries of India's infra boom.",
            "risk": "Moderate–High", "horizon": "2–4 years",
            "names": ["L&T","HAL","Bharat Electronics","Adani Ports","Adani Enterprises",
                      "DLF","Godrej Properties","Siemens India","ABB India","IRCTC","NTPC"]},
    },
    "USA": {
        "⭐ Core 30 – Blue Chips": {
            "description": "America's most trusted companies.",
            "risk": "Low–Moderate", "horizon": "3–5 years",
            "names": ["Apple","Microsoft","Alphabet A (Google)","Amazon","Johnson & Johnson",
                      "JPMorgan Chase","Visa","Procter & Gamble","UnitedHealth","Exxon Mobil",
                      "Mastercard","Chevron","Home Depot","PepsiCo","Coca-Cola",
                      "Walmart","McDonald's","Nike","Cisco","AbbVie",
                      "Eli Lilly","Pfizer","Merck","Amgen","Caterpillar",
                      "Goldman Sachs","Bank of America","Wells Fargo","Walt Disney","Starbucks"]},
        "🤖 AI & Cloud Leaders": {
            "description": "Companies powering the AI revolution.",
            "risk": "High", "horizon": "2–5 years",
            "names": ["NVIDIA","Microsoft","Alphabet A (Google)","Amazon","Meta Platforms",
                      "AMD","Broadcom","Oracle","Salesforce","Adobe",
                      "Palantir","Qualcomm","Applied Materials","Lam Research","CrowdStrike"]},
        "💊 Healthcare Giants": {
            "description": "Top US healthcare and pharma.",
            "risk": "Moderate", "horizon": "2–4 years",
            "names": ["Johnson & Johnson","UnitedHealth","Eli Lilly","AbbVie","Pfizer",
                      "Merck","Amgen","Gilead Sciences","Moderna","Regeneron",
                      "Vertex Pharma","Intuitive Surgical","Danaher","Thermo Fisher","Abbott Laboratories"]},
    },
    "Europe": {
        "⭐ Euro Core 25": {
            "description": "Top 25 European blue chips.",
            "risk": "Low–Moderate", "horizon": "2–4 years",
            "names": ["ASML","LVMH","Nestle","Roche","Novartis","SAP","Siemens",
                      "HSBC","Shell","AstraZeneca","Unilever","Allianz","BNP Paribas",
                      "TotalEnergies","L'Oreal","Airbus","Sanofi","Schneider Electric",
                      "BMW","Mercedes-Benz","Diageo","GSK","Volkswagen","Inditex","BP"]},
        "👜 Luxury & Consumer": {
            "description": "Global luxury and consumer brands.",
            "risk": "Moderate", "horizon": "3–5 years",
            "names": ["LVMH","L'Oreal","Inditex","Diageo","Unilever","Nestle",
                      "Hermes","Kering","Pernod Ricard","Danone","Heineken","Adidas"]},
    },
    "China": {
        "⭐ China Core 20": {
            "description": "Top 20 liquid HK-listed Chinese stocks.",
            "risk": "High", "horizon": "2–4 years",
            "names": ["Alibaba Group (HK)","Tencent Holdings","Meituan","JD.com (HK)",
                      "BYD Co (HK)","NetEase (HK)","Xiaomi Group","China Mobile",
                      "Ping An Insurance","ICBC (HK)","CCB (HK)","Bank of China (HK)",
                      "PetroChina (HK)","CNOOC","Li Ning","Anta Sports Products",
                      "Kuaishou Technology","Geely Automobile","Sunny Optical Tech","Galaxy Entertainment"]},
    },
}

KPI_HELP = {
    "Price Momentum":   {"plain":"How strongly price moved today.",
                         "green":"Rising — buyers in control.",
                         "red":"Falling — sellers in control.",
                         "decide":"Strong upward momentum + news = good entry."},
    "RSI (14 days)":    {"plain":"0–100 score: oversold or overbought.",
                         "green":"Below 35 = potential bargain.",
                         "red":"Above 70 = may cool off.",
                         "decide":"Under 35 + good fundamentals = consider buying."},
    "MACD Histogram":   {"plain":"Strength of price trend direction.",
                         "green":"Positive = buyers gaining.",
                         "red":"Negative = sellers gaining.",
                         "decide":"Positive and rising = good time to ride trend."},
    "Bollinger Width":  {"plain":"How much the stock is swinging.",
                         "green":"Expanding after tight = big move starting.",
                         "yellow":"Very tight = coiling up for breakout.",
                         "decide":"Width expanding after squeeze = strong move started."},
    "ATR Volatility":   {"plain":"Typical daily price move — your risk number.",
                         "green":"Low = calm, predictable.",
                         "red":"High = wild swings, larger risk.",
                         "decide":"High ATR = invest smaller amounts."},
    "ADX Trend":        {"plain":"Is the stock trending or just drifting?",
                         "green":"Above 25 = strong clear trend.",
                         "yellow":"Below 20 = no clear direction.",
                         "decide":"Only ride trends when ADX > 25."},
    "Stochastic %K":    {"plain":"Today's price vs last 2 weeks' range.",
                         "green":"Below 20 = near recent low, may bounce.",
                         "red":"Above 80 = near recent high, may pull back.",
                         "decide":"Cross up from below 20 = buy signal."},
    "P/E & P/B":        {"plain":"P/E = earnings multiple. P/B = asset value multiple.",
                         "green":"P/E below sector average = possible bargain.",
                         "red":"P/E above 40 = expensive.",
                         "decide":"Low P/E + high ROE + growth = attractive."},
    "ROE & Rev Growth": {"plain":"ROE = profit efficiency. Rev Growth = business expansion.",
                         "green":"ROE > 15% and revenue growing = healthy.",
                         "red":"ROE < 8% or shrinking = losing edge.",
                         "decide":"High ROE + revenue growth = strong long-term buy."},
    "OBV & Volume":     {"plain":"Are big investors quietly buying or selling?",
                         "green":"Rising OBV = institutions accumulating.",
                         "red":"Falling OBV on rising price = fake move.",
                         "decide":"Price up + OBV up = high conviction."},
}

# ── Version Log UI (goes in sidebar expander) ────────────────────────────────
def render_version_log():
    with st.sidebar.expander(f"📋 Version Log  ({CURRENT_VERSION})"):
        for v in reversed(VERSION_LOG):
            badge_col = "#00c853" if v["version"] == CURRENT_VERSION else "#2d3a5e"
            st.markdown(
                f"<div style='border-left:3px solid {badge_col};padding:5px 10px;margin:4px 0;"
                f"background:#0d1117;border-radius:0 6px 6px 0;'>"
                f"<span style='color:#4f8ef7;font-weight:700;font-size:0.80rem;'>{v['version']}</span>"
                f"&nbsp;<span style='color:#4b6080;font-size:0.72rem;'>{v['date']}</span><br>"
                f"<span style='color:#8896b0;font-size:0.76rem;'>{v['notes']}</span></div>",
                unsafe_allow_html=True
            )

def render_error_log():
    errors = list(st.session_state.get("app_error_log", []))
    with st.sidebar.expander(
        f"{'🔴' if errors else '🟢'} Error Log  ({len(errors)} {'error' if len(errors)==1 else 'errors'})"
    ):
        if not errors:
            st.success("No errors recorded this session.")
        else:
            for e in errors[:10]:
                st.markdown(
                    f"<div style='background:#1a0a0a;border-left:3px solid #ff1744;border-radius:0 6px 6px 0;"
                    f"padding:6px 10px;margin:4px 0;font-size:0.75rem;'>"
                    f"<b style='color:#ff6060;'>{e['time']} — {e['error']}</b><br>"
                    f"<span style='color:#cc8888;'>{e['context']}</span><br>"
                    f"<span style='color:#886666;'>{e['detail']}</span></div>",
                    unsafe_allow_html=True
                )
            if st.button("🗑️ Clear error log"):
                st.session_state.app_error_log.clear()
                st.rerun()

# ─────────────────────────────────────────────────────────────
#  DATA HELPERS  (cache_buster forces fresh fetch when live)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_price_data(ticker, period="1y", cache_buster=0):
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df.dropna()
    except Exception as e:
        log_error("yf_download", e)
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_info(ticker, cache_buster=0):
    try:
        return yf.Ticker(ticker).info
    except Exception as e:
        log_error("yf_ticker", e)
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def get_ticker_prices(tickers_tuple, max_n=30, cache_buster=0):
    items = list(tickers_tuple)[:max_n]
    out   = []
    for name, sym in items:
        try:
            d = yf.download(sym, period="5d", auto_adjust=True, progress=False)
            d.columns = [c[0] if isinstance(c, tuple) else c for c in d.columns]
            if not d.empty and len(d) >= 2:
                cur = float(d["Close"].iloc[-1])
                prv = float(d["Close"].iloc[-2])
                chg = (cur - prv) / prv * 100 if prv else 0
                out.append({"sym": sym.replace(".NS","").replace(".HK","")
                                      .replace(".L","").replace(".PA","").replace(".DE",""),
                             "name": name[:18], "price": cur, "chg": chg,
                             "arrow": "▲" if chg >= 0 else "▼",
                             "color": "#00e676" if chg >= 0 else "#ff1744"})
        except Exception as e:
            log_error("general", e)
    return out

@st.cache_data(ttl=120, show_spinner=False)
def get_news(country, cache_buster=0):
    articles = []
    for source, url in NEWS_FEEDS.get(country, []):
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:6]:
                articles.append({"source": source, "title": e.get("title",""),
                    "link": e.get("link","#"), "summary": e.get("summary","")[:160],
                    "date": e.get("published","")[:22]})
        except Exception as e:
            log_error("rss_feed", e)
    return articles[:30]

@st.cache_data(ttl=120, show_spinner=False)
def get_news_headlines(country, cache_buster=0):
    headlines = []
    for source, url in NEWS_FEEDS.get(country, []):
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:4]:
                headlines.append(f"📰 {e.get('title','')}  [{source}]")
        except Exception as e:
            log_error("rss_feed", e)
    return headlines[:20]

@st.cache_data(ttl=600, show_spinner=False)
def verify_ticker_live(ticker):
    try:
        d = yf.download(ticker, period="5d", auto_adjust=True, progress=False)
        d.columns = [c[0] if isinstance(c, tuple) else c for c in d.columns]
        if not d.empty and "Close" in d.columns:
            p=float(_safe_close(d).iloc[-1]) if not _safe_close(d).empty else 0
            return (True, round(p, 2)) if p > 0 else (False, None)
    except Exception as e:
        log_error("yf_download", e)
    return False, None

def safe_float(val, default=0.0):
    try:
        v = float(val)
        return default if (np.isnan(v) or np.isinf(v)) else v
    except Exception as e:
        log_error("general", e)
        return default

def compute_indicators(df):
    if df is None or (hasattr(df, 'empty') and df.empty):
        return pd.DataFrame()
    df = df.copy()
    c=_safe_close(df)
    df["SMA20"]  = c.rolling(20).mean()
    df["SMA50"]  = c.rolling(50).mean()
    df["SMA200"] = c.rolling(200).mean()
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["MACD"]   = ema12 - ema26
    df["MACD_S"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_H"] = df["MACD"] - df["MACD_S"]
    mid = c.rolling(20).mean(); std = c.rolling(20).std()
    df["BB_U"] = mid + 2*std; df["BB_L"] = mid - 2*std
    df["BB_W"] = (df["BB_U"] - df["BB_L"]) / mid * 100
    hl  = df["High"] - df["Low"]
    hpc = (df["High"] - c.shift()).abs()
    lpc = (df["Low"]  - c.shift()).abs()
    df["ATR"] = pd.concat([hl, hpc, lpc], axis=1).max(axis=1).rolling(14).mean()
    low14  = df["Low"].rolling(14).min()
    high14 = df["High"].rolling(14).max()
    df["Stoch"] = (c - low14) / (high14 - low14 + 1e-9) * 100
    pldm = df["High"].diff().clip(lower=0)
    mndm = (-df["Low"].diff()).clip(lower=0)
    df["ADX"] = (100*(pldm.rolling(14).sum()-mndm.rolling(14).sum()).abs()
                 / hl.rolling(14).sum().replace(0, np.nan)).rolling(14).mean()
    obv = [0]
    for i in range(1, len(df)):
        obv.append(obv[-1] + df["Volume"].iloc[i] if c.iloc[i] > c.iloc[i-1]
                   else obv[-1] - df["Volume"].iloc[i] if c.iloc[i] < c.iloc[i-1]
                   else obv[-1])
    df["OBV"] = obv
    # Canonical aliases expected by KPI tiles and tests
    df["BB_upper"]  = df["BB_U"]
    df["BB_lower"]  = df["BB_L"]
    df["Volume_MA"] = df["Volume"].rolling(20).mean()
    return df

def signal_score(df, info):
    r = df.iloc[-1]; s = 0
    rsi = safe_float(r.get("RSI", 50))
    mh  = safe_float(r.get("MACD_H", 0))
    st2 = safe_float(r.get("Stoch", 50))
    if rsi < 40: s += 2
    if rsi > 65: s -= 1
    if mh  > 0:  s += 2
    else:        s -= 1
    if float(r["Close"]) > safe_float(df["SMA50"].iloc[-1]):  s += 1
    if float(r["Close"]) > safe_float(df["SMA200"].iloc[-1]): s += 1
    if st2 < 30: s += 1
    if st2 > 75: s -= 1
    pe  = info.get("trailingPE", 0) or 0
    roe = (info.get("returnOnEquity", 0) or 0) * 100
    if 0 < pe  < 20: s += 1
    if roe > 15:     s += 1
    s = max(-5, min(7, s))
    if s >= 5:    return "STRONG BUY",  "#00c853"
    elif s == 4:  return "BUY",         "#69f0ae"
    elif s == 3:  return "WEAK BUY",    "#b9f6ca"
    elif s in (1,2): return "NEUTRAL",  "#ffd600"
    elif s == 0:  return "WEAK SELL",   "#ff6d00"
    elif s == -1: return "SELL",        "#ff1744"
    else:         return "STRONG SELL", "#b71c1c"

# ─────────────────────────────────────────────────────────────
#  RENDER HELPERS
# ─────────────────────────────────────────────────────────────
def render_price_ticker(ticker_items, cur_sym="₹"):
    if not ticker_items:
        return
    parts = []
    for t in ticker_items:
        parts.append(
            f"<span style='margin:0 28px;'>"
            f"<span style='color:#c8d6f0;font-weight:700;font-size:0.92rem;'>{t['sym']}</span>"
            f"<span style='color:#6a7a90;font-size:0.78rem;margin-left:6px;'>{t['name']}</span>"
            f"&nbsp;&nbsp;<span style='color:#fff;font-weight:800;'>{cur_sym}{t['price']:,.2f}</span>"
            f"&nbsp;<span style='color:{t['color']};font-weight:700;'>{t['arrow']} {t['chg']:+.2f}%</span>"
            f"</span><span style='color:#1e2d4a;'>│</span>"
        )
    html = "".join(parts) * 2
    st.markdown(f"""
<div style='background:#060c18;border-bottom:2px solid #0d3060;padding:7px 0;overflow:hidden;'>
  <div style='display:flex;align-items:center;'>
    <div style='background:#0d3060;color:#4f8ef7;font-weight:900;font-size:0.72rem;
      padding:4px 10px;white-space:nowrap;border-right:2px solid #1e4080;
      min-width:70px;text-align:center;flex-shrink:0;letter-spacing:1px;'>LIVE<br>PRICES</div>
    <div style='overflow:hidden;flex:1;'>
      <div style='display:inline-block;white-space:nowrap;
        animation:tickerScroll 55s linear infinite;'>{html}</div>
    </div>
  </div>
</div>
<style>
@keyframes tickerScroll {{ 0% {{ transform:translateX(0); }} 100% {{ transform:translateX(-50%); }} }}
</style>
""", unsafe_allow_html=True)

def render_news_ticker(headlines):
    if not headlines:
        return
    joined = "<span style='color:#1e3050;margin:0 18px;'>◆</span>".join(
        f"<span style='color:#8aa0c0;font-size:0.79rem;'>{h}</span>"
        for h in headlines
    ) * 2
    st.markdown(f"""
<div style='background:#040810;border-bottom:1px solid #0a1a30;padding:4px 0;overflow:hidden;'>
  <div style='display:flex;align-items:center;'>
    <div style='background:#0a1f0a;color:#00c853;font-weight:900;font-size:0.68rem;
      padding:3px 8px;white-space:nowrap;border-right:2px solid #0d3020;
      min-width:70px;text-align:center;flex-shrink:0;letter-spacing:1px;'>LIVE<br>NEWS</div>
    <div style='overflow:hidden;flex:1;padding:0 8px;'>
      <div style='display:inline-block;white-space:nowrap;
        animation:newsScroll 80s linear infinite;'>{joined}</div>
    </div>
  </div>
</div>
<style>
@keyframes newsScroll {{ 0% {{ transform:translateX(0); }} 100% {{ transform:translateX(-50%); }} }}
</style>
""", unsafe_allow_html=True)

def render_morning_brief(country, country_tickers, market_open, cb):
    sess       = MARKET_SESSIONS.get(country, {})
    tz         = pytz.timezone(sess.get("tz", "UTC"))
    now        = datetime.now(tz)
    oh, om     = sess.get("open", (9, 0))
    is_pre     = (not market_open) and now.weekday() < 5 and (now.hour, now.minute) < (oh, om)
    label      = ("🌅 Pre-Market Morning Brief" if is_pre else
                  "📊 Mid-Session Update" if market_open else "🌙 After-Hours Summary")
    slbl, scol = market_status_label(country)

    next_open_html = (
        f"<div style='color:#4b6080;font-size:0.70rem;margin-top:2px;'>"
        f"Next open: {next_open_label(country)}"
        f"</div>"
    ) if not market_open else ""
    st.markdown(
        f"<div style='background:linear-gradient(135deg,#060f1e,#0a1628);"
        f"border:1px solid #0d2a50;border-radius:14px;padding:18px 22px;margin-bottom:16px;'>"
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
        f"<div>"
        f"<div style='font-size:0.70rem;color:#4b6080;text-transform:uppercase;letter-spacing:1.5px;'>"
        f"{country} Market Intelligence</div>"
        f"<div style='font-size:1.3rem;font-weight:900;color:#c8d6f0;margin-top:4px;'>{label}</div>"
        f"<div style='font-size:0.78rem;color:#5070a0;margin-top:4px;'>"
        f"{now.strftime('%A, %d %B %Y  %H:%M')} {sess.get('tz','').split('/')[-1]}</div>"
        f"</div>"
        f"<div style='background:{scol}18;border:1px solid {scol};"
        f"border-radius:8px;padding:8px 14px;text-align:center;'>"
        f"<div style='color:{scol};font-weight:900;font-size:0.84rem;'>{slbl}</div>"
        f"{next_open_html}"
        f"</div></div></div>",
        unsafe_allow_html=True
    )


    st.markdown("#### 📋 Key Headlines to Watch")
    hl = get_news_headlines(country, cache_buster=cb)
    for h in (hl[:6] if hl else ["News feed loading..."]):
        st.markdown(f"<div class='news-card'><div class='news-title'>{h}</div></div>",
                    unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

def graph_help(what, read, decide):
    st.markdown(f"""<div class='graph-help'>
      📖 <b>What this shows:</b> {what}<br>
      👁️ <b>How to read it:</b> {read}<br>
      ✅ <b>How it helps you decide:</b> {decide}
    </div>""", unsafe_allow_html=True)

def kpi_tile(col, label, value, color="", delta=None):
    hd = KPI_HELP.get(label, {})
    delta_html = ""
    if delta is not None:
        c2 = "#00c853" if delta >= 0 else "#ff1744"
        arr = "▲" if delta >= 0 else "▼"
        delta_html = (f"<div style='font-size:0.78rem;font-weight:700;color:{c2};"
                      f"margin-top:4px;'>{arr} {abs(delta):.2f}% today</div>")
    help_txt = (hd.get("green","") if color=="green" else
                hd.get("red","")   if color=="red"   else
                hd.get("yellow","") or hd.get("plain",""))
    border_col = {"green":"#00c853","red":"#ff1744","yellow":"#ffab00"}.get(color,"#2d3a5e")
    bg_col     = {"green":"#00c85310","red":"#ff174410","yellow":"#ffab0010"}.get(color,"#0d1117")
    html = (
        f"<div style='background:{bg_col};border:1px solid {border_col};"
        f"border-radius:10px;padding:12px 14px;height:100%;'>"
        f"<div style='font-size:0.72rem;color:#6b7a90;text-transform:uppercase;"
        f"letter-spacing:0.8px;margin-bottom:6px;'>{label}</div>"
        f"<div style='font-size:1.15rem;font-weight:900;color:#fff;'>{value}</div>"
        f"{delta_html}"
        f"<div style='font-size:0.68rem;color:#4b6080;margin-top:6px;'>{help_txt}</div>"
        f"</div>"
    )
    with col:
        st.markdown(html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
ALL_TICKERS = load_validated_tickers()

with st.sidebar:
    st.markdown("## 📈 Global Stock Intelligence")
    st.caption("Real-Time · Multi-KPI · 643 Validated Tickers · v3.2")
    st.markdown("---")

    # ── Navigation (top, horizontal) ─────────────────────────────────────
    try:
        active_page = st.radio(
            "Navigate",
            ["🏠 Home", "📊 Investor's Dashboard", "🌍 Global Intelligence"],
            label_visibility="collapsed",
            horizontal=True,
            key="nav_radio",
        )
    except TypeError:  # Streamlit < 1.18 fallback
        active_page = st.radio(
            "🧭 Navigate",
            ["🏠 Home", "📊 Investor's Dashboard", "🌍 Global Intelligence"],
            key="nav_radio",
        )
    st.markdown("---")

    country          = st.selectbox("🌍 Market Country", list(ALL_TICKERS.keys()))
    country_tickers  = ALL_TICKERS.get(country, {})
    country_groups   = GROUPS.get(country, {})

    universe_type = st.radio("📂 Universe Type", [
        "⭐ Curated Groups & Model Portfolios",
        "🔎 Full Validated List (Search Any Stock)"
    ])

    if universe_type.startswith("⭐") and country_groups:
        selected_group = st.selectbox("📁 Select Group", list(country_groups.keys()))
        grp = country_groups[selected_group]
        st.markdown(f"""<div class='group-badge'>
          {grp['description']}<br><br>
          🎯 <b>Risk:</b> {grp['risk']} &nbsp;|&nbsp; ⏳ <b>Horizon:</b> {grp['horizon']}
        </div>""", unsafe_allow_html=True)
        stock_map = {n: country_tickers[n] for n in grp["names"] if n in country_tickers}
        if not stock_map:
            stock_map = country_tickers
    else:
        selected_group = "Full Validated List"
        stock_map = country_tickers

    if not stock_map:
        stock_map = {"Reliance Industries": "RELIANCE.NS"}

    search = st.text_input("🔍 Search stock", "")
    filtered = ({k: v for k, v in stock_map.items()
                 if search.lower() in k.lower() or search.lower() in v.lower()}
                if search else stock_map)
    if not filtered:
        filtered = stock_map

    stock_names   = list(filtered.keys())
    selected_name = st.selectbox("📊 Select Stock", stock_names) if stock_names else None

    if not selected_name:
        st.error("❌ No stocks available. Choose a different group or country.")
        st.stop()

    selected_ticker = filtered.get(selected_name)
    if not selected_ticker:
        st.error(f"❌ Ticker not found for {selected_name}.")
        st.stop()

    is_valid, live_price = verify_ticker_live(selected_ticker)
    if is_valid:
        st.markdown(f"<div class='valid-badge'>✅ Live: {selected_ticker} @ {live_price:,.2f}</div>",
                    unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ {selected_ticker} — could not fetch live price.")

    st.markdown("---")
    horizon     = st.radio("📅 Forecast Horizon", ["3 Months","6 Months","1 Year"])
    fcast_days  = {"3 Months":65,"6 Months":130,"1 Year":252}[horizon]
    compare_names = st.multiselect("⚖️ Compare With",
                                    [k for k in stock_map if k != selected_name],
                                    max_selections=3)
    st.markdown("---")
    render_version_log()
    render_error_log()
    auto_refresh = st.checkbox("⏱ Auto-refresh (live when market open)")
    st.caption(f"🕐 {datetime.now().strftime('%d %b %Y %H:%M')}")
    st.caption("⚠️ Not investment advice.")

# ─────────────────────────────────────────────────────────────
#  COMPUTE MARKET STATUS + CACHE BUSTER  (before any data load)
# ─────────────────────────────────────────────────────────────
market_open     = is_market_open(country)
status_lbl, s_col = market_status_label(country)
cb      = int(time.time() // 10) if (auto_refresh and market_open) else 0
cur_sym = CURRENCY.get(country, "")

# ── GLOBAL HEADER: price ticker + news (all pages, updates when market open) ──
_g_ct = locals().get("country_tickers") or {}
_g_cs = locals().get("cur_sym") or ""
_g_sample    = tuple(list(_g_ct.items())[:30])
_g_items     = safe_run(
    lambda: get_ticker_prices(_g_sample, max_n=30, cache_buster=cb),
    "global_price_ticker", []
)
render_price_ticker(_g_items, _g_cs)
_g_headlines = safe_run(
    lambda: get_news_headlines(country, cache_buster=cb),
    "global_news_ticker", []
)
render_news_ticker(_g_headlines)

# ── Page routing ────────────────────────────────────────────────────────────
if active_page == "🏠 Home":
    render_homepage(cb)
    st.stop()

if active_page == "🌍 Global Intelligence":
    render_global_intelligence(cur_sym, cb)
    st.stop()


# ─────────────────────────────────────────────────────────────
#  LOAD MAIN STOCK DATA
# ─────────────────────────────────────────────────────────────
with st.spinner(f"Loading {selected_name} ({selected_ticker})..."):
    df_raw = safe_run(lambda: get_price_data(selected_ticker, "2y", cache_buster=cb),
                      "get_price_data", pd.DataFrame())
    df     = safe_run(lambda: compute_indicators(df_raw) if not df_raw.empty else pd.DataFrame(),
                      "compute_indicators", pd.DataFrame())
    info   = safe_run(lambda: get_info(selected_ticker, cache_buster=cb), "get_info", {})
    news   = safe_run(lambda: get_news(country, cache_buster=cb), "get_news", [])

if df.empty or len(df) < 5:
    st.error(f"❌ Could not load data for **{selected_name}** ({selected_ticker}). "
             "This may be a temporary Yahoo Finance issue. Try another stock.")
    st.stop()

latest = df.iloc[-1]
prev   = df.iloc[-2] if len(df) >= 2 else df.iloc[-1]
price  = float(latest["Close"])
chg    = (price - float(prev["Close"])) / float(prev["Close"]) * 100 if float(prev["Close"]) != 0 else 0.0
signal, sig_color = signal_score(df, info)

# ─────────────────────────────────────────────────────────────
#  KPI VARIABLES  (outer scope — available to all tabs)
# ─────────────────────────────────────────────────────────────
rsi    = safe_float(latest.get("RSI",    50))
macdh  = safe_float(latest.get("MACD_H",  0))
bbw    = safe_float(latest.get("BB_W",    0))
atr    = safe_float(latest.get("ATR",     0))
adx    = safe_float(latest.get("ADX",     0))
stoch  = safe_float(latest.get("Stoch",  50))
obv    = safe_float(latest.get("OBV",     0)) / 1e6
vol_m  = safe_float(latest.get("Volume",  0)) / 1e6
sma50  = safe_float(df["SMA50"].iloc[-1])
sma200 = safe_float(df["SMA200"].iloc[-1])
pe     = info.get("trailingPE",      0) or 0
pb     = info.get("priceToBook",     0) or 0
roe    = (info.get("returnOnEquity", 0) or 0) * 100
revg   = (info.get("revenueGrowth",  0) or 0) * 100
r_c    = "green" if rsi   < 40 else ("red"    if rsi   > 70 else "yellow")
m_c    = "green" if macdh > 0  else "red"
p_c    = "green" if price > sma50  else "red"
a_c    = "green" if adx   > 25 else "yellow"
s_c    = "green" if stoch < 30 else ("red"    if stoch > 75 else "yellow")
v_c    = "green" if 0 < pe < 22 else ("red"   if pe    > 40 else "yellow")
f_c    = "green" if roe   > 15 else ("red"    if roe   <  5 else "yellow")


# ─────────────────────────────────────────────────────────────
#  SCROLLING TICKERS + MORNING BRIEF
# ─────────────────────────────────────────────────────────────
# ── Fragment: only THIS block reruns every 5s when market open ───────────────
# ─────────────────────────────────────────────────────────────
#  STATIC ELEMENTS (rendered once at page load)
# ─────────────────────────────────────────────────────────────
# Dashboard: company card → KPI → tabs → morning brief → picks
# (Price + news tickers rendered globally before routing above)

# ─────────────────────────────────────────────────────────────
#  LIVE PRICE FRAGMENT  (only this updates every 5s)
#  One lightweight intraday download ~0.2s — no full page reload
# ─────────────────────────────────────────────────────────────
_HAS_FRAGMENT = hasattr(st, "fragment")

def _render_live_price(live_px, live_chg, sig, sig_col, last_updated):
    """Renders the live price header card and Price Momentum KPI tile."""
    market_cap = info.get("marketCap", 0) or 0
    sector     = info.get("sector", "") or info.get("quoteType", "")
    long_name  = info.get("longName", selected_name)
    chg_col    = "#00c853" if live_chg >= 0 else "#ff1744"
    chg_arr    = "▲" if live_chg >= 0 else "▼"
    poll_badge = "🔄 LIVE" if (auto_refresh and market_open) else "📌 STATIC"
    poll_color = "#00c853" if (auto_refresh and market_open) else "#6b7280"

    st.markdown(f"""
<div style='background:linear-gradient(135deg,#111827,#1f2937);border-radius:14px;
  padding:20px 28px;margin-bottom:18px;border:1px solid #1f2d40;'>
  <div style='font-size:0.74rem;color:#6b7280;margin-bottom:4px;'>
    🌍 {country} · {selected_group} · {sector} · Mkt Cap: {market_cap/1e9:.1f}B
  </div>
  <div style='font-size:1.85rem;font-weight:900;color:#fff;'>{long_name}</div>
  <div style='display:flex;align-items:baseline;gap:14px;margin-top:6px;'>
    <span style='font-size:2rem;font-weight:900;color:#4f8ef7;'>{cur_sym}{live_px:,.2f}</span>
    <span style='font-size:1.15rem;color:{chg_col};font-weight:700;'>{chg_arr} {abs(live_chg):.2f}% today</span>
  </div>
  <div style='margin-top:10px;display:flex;align-items:center;gap:8px;'>
    <span style='background:{sig_col}22;border:1px solid {sig_col};border-radius:20px;
      padding:4px 14px;color:{sig_col};font-weight:700;font-size:0.86rem;'>⚡ {sig}</span>
    <span style='background:{poll_color}18;border:1px solid {poll_color};border-radius:6px;
      padding:3px 10px;font-size:0.72rem;color:{poll_color};'>{poll_badge}</span>
    <span class='valid-badge'>✅ {selected_ticker}</span>
    <span style='color:#4b6080;font-size:0.70rem;margin-left:auto;'>🕐 Updated: {last_updated}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # Price Momentum KPI tile — inline to avoid st.container() scoping issues
    pm_color  = "green" if live_chg >= 0 else "red"
    pm_border = "#00c853" if live_chg >= 0 else "#ff1744"
    pm_arr    = "▲" if live_chg >= 0 else "▼"
    pm_help   = "Rising — buyers in control." if live_chg >= 0 else "Falling — sellers in control."
    st.markdown(
        f"<div style='background:{pm_border}10;border:1px solid {pm_border};"
        f"border-radius:10px;padding:12px 14px;'>"
        f"<div style='font-size:0.72rem;color:#6b7a90;text-transform:uppercase;"
        f"letter-spacing:0.8px;margin-bottom:6px;'>Price Momentum</div>"
        f"<div style='font-size:1.15rem;font-weight:900;color:#fff;'>{cur_sym}{live_px:,.2f}</div>"
        f"<div style='font-size:0.78rem;font-weight:700;color:{pm_border};margin-top:4px;'>"
        f"{pm_arr} {abs(live_chg):.2f}% today</div>"
        f"<div style='font-size:0.68rem;color:#4b6080;margin-top:6px;'>{pm_help}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

def _get_live_price_fast(ticker):
    """Lightweight 1-day intraday fetch — returns (price, 1d_chg%). ~0.2–0.5s."""
    try:
        d = yf.download(ticker, period="1d", interval="1m",
                        auto_adjust=True, progress=False)
        d.columns = [c[0] if isinstance(c, tuple) else c for c in d.columns]
        if not d.empty and len(d) >= 2:
            lp=float(_safe_close(d).iloc[-1]) if not _safe_close(d).empty else 0
            op = float(d["Open"].iloc[0])
            return lp, (lp - op) / op * 100 if op else 0.0
    except Exception as e:
        log_error("live_price_fast", e)
    # fallback to end-of-day price already computed
    return price, chg

if _HAS_FRAGMENT and auto_refresh and market_open:
    @st.fragment(run_every=5)
    def _live_price_fragment():
        lp, lc = _get_live_price_fast(selected_ticker)
        updated = datetime.now().strftime("%H:%M:%S")
        _render_live_price(lp, lc, signal, sig_color, updated)
    _live_price_fragment()
else:
    _render_live_price(price, chg, signal, sig_color,
                       datetime.now().strftime("%H:%M:%S"))

# ─────────────────────────────────────────────────────────────
#  9 HISTORICAL KPI TILES  (static — based on 2y history)
# ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>📐 KPI Signal Panel</div>", unsafe_allow_html=True)
st.caption("Historical indicators (RSI, MACD, Bollinger etc.) update when you reload the page or change stock.")

_cols1 = st.columns(4, gap="small")
kpi_tile(_cols1[0], "RSI (14 days)",    f"{rsi:.1f}",              r_c)
kpi_tile(_cols1[1], "MACD Histogram",   f"{macdh:+.2f}",           m_c)
kpi_tile(_cols1[2], "Bollinger Width",  f"{bbw:.1f}%",             "yellow")
kpi_tile(_cols1[3], "ATR Volatility",   f"{atr:.1f}",              "yellow")

_cols2 = st.columns(5, gap="small")
kpi_tile(_cols2[0], "ADX Trend",        f"{adx:.1f}",              a_c)
kpi_tile(_cols2[1], "Stochastic %K",    f"{stoch:.1f}",            s_c)
kpi_tile(_cols2[2], "P/E & P/B",        f"{pe:.1f} | {pb:.2f}x",  v_c)
kpi_tile(_cols2[3], "ROE & Rev Growth", f"{roe:.1f}% | {revg:.1f}%", f_c)
kpi_tile(_cols2[4], "OBV & Volume",     f"{obv:+,.0f}M | {vol_m:.1f}M", "")
st.markdown("---")

# Defaults — overridden by tab2 forecast computation if data loads
target = price
upside = 0.0

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Technical Charts","🔮 Forecast","⚖️ Compare","💡 Insights & Actions"
])

# ── Tab 1: Technical ─────────────────────────────────────────
with tab1:
    graph_help("Daily price + momentum indicators over 120 days.",
               "Green/red candles = daily moves. Lines = moving averages. MACD/RSI = mood.",
               "Is price trending up or down? Is momentum building or fading?")
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, row_heights=[0.45,0.20,0.20,0.15],
                        vertical_spacing=0.03,
                        subplot_titles=("Price + Bollinger + MAs","MACD","RSI","Volume"))
    dp = df.tail(120)
    fig.add_trace(go.Candlestick(x=dp.index, open=dp["Open"], high=dp["High"],
        low=dp["Low"], close=dp["Close"], name="Price",
        increasing_line_color="#00c853", decreasing_line_color="#ff1744"), row=1, col=1)
    for cn, color, dash in [("SMA20","#4fc3f7","solid"),("SMA50","#ffd600","dash"),("SMA200","#ff6d00","dot")]:
        fig.add_trace(go.Scatter(x=dp.index, y=dp[cn], name=cn,
            line=dict(color=color,width=1.2,dash=dash)), row=1, col=1)
    fig.add_trace(go.Scatter(x=dp.index, y=dp["BB_U"],
        line=dict(color="#7986cb",width=1,dash="dot"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=dp.index, y=dp["BB_L"], name="BB Band",
        line=dict(color="#7986cb",width=1,dash="dot"),
        fill="tonexty", fillcolor="rgba(121,134,203,0.06)"), row=1, col=1)
    hc = ["#00c853" if v >= 0 else "#ff1744" for v in dp["MACD_H"]]
    fig.add_trace(go.Bar(x=dp.index, y=dp["MACD_H"], marker_color=hc, name="Histogram", opacity=0.7), row=2, col=1)
    fig.add_trace(go.Scatter(x=dp.index, y=dp["MACD"],   name="MACD",   line=dict(color="#4fc3f7",width=1.2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=dp.index, y=dp["MACD_S"], name="Signal", line=dict(color="#ffd600",width=1.2,dash="dash")), row=2, col=1)
    fig.add_trace(go.Scatter(x=dp.index, y=dp["RSI"], name="RSI",
        line=dict(color="#e040fb",width=1.8),
        fill="tozeroy", fillcolor="rgba(224,64,251,0.05)"), row=3, col=1)
    fig.add_hline(y=70, row=3, col=1, line_dash="dot", line_color="#ff1744", line_width=0.8)
    fig.add_hline(y=30, row=3, col=1, line_dash="dot", line_color="#00c853", line_width=0.8)
    vc = ["#00c853" if dp["Close"].iloc[i] >= dp["Close"].iloc[max(i-1,0)] else "#ff1744" for i in range(len(dp))]
    fig.add_trace(go.Bar(x=dp.index, y=dp["Volume"], marker_color=vc, name="Volume", opacity=0.6), row=4, col=1)
    fig.update_layout(template="plotly_dark", height=720,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#c8cee8"),
        legend=dict(orientation="h",y=1.02),
        margin=dict(l=10,r=10,t=30,b=10))
    fig.update_yaxes(title_text="Price",  row=1, col=1)
    fig.update_yaxes(title_text="MACD",   row=2, col=1)
    fig.update_yaxes(title_text="RSI",    row=3, col=1)
    fig.update_yaxes(title_text="Volume", row=4, col=1)
    st.plotly_chart(fig, width='stretch', config={"responsive": True})

# ── Tab 2: Forecast ──────────────────────────────────────────
with tab2:
    graph_help("Price projection for the selected horizon.",
               "Solid = past. Dashed = forecast direction. Shaded = confidence range.",
               "Is today's price near the bottom or top of the expected range?")
    hist=_safe_close(df).tail(90)
    x    = np.arange(len(hist))
    z    = np.polyfit(x, hist.values, 1)
    fn   = np.poly1d(z)
    fx   = np.arange(len(hist), len(hist) + fcast_days)
    fv   = fn(fx)
    # Apply auto-correction factor if accuracy < 95%
    _cf  = compute_correction_factor(selected_ticker)
    fv   = fv * _cf
    # Store this forecast for future accuracy tracking
    safe_run(lambda: store_forecast(selected_ticker, fcast_days, float(fv[-1]), price),
             "store_forecast")
    safe_run(lambda: resolve_forecasts(selected_ticker, price), "resolve_forecasts")
    vol  = float(hist.pct_change().std()) * float(hist.values[-1])
    vol_arr   = vol * np.sqrt(np.arange(1, fcast_days+1))
    fc_dates  = pd.bdate_range(df.index[-1] + timedelta(1), periods=fcast_days)
    fc        = pd.DataFrame({"Date":fc_dates,"Forecast":fv,
                               "Upper":fv+1.5*vol_arr,"Lower":fv-1.5*vol_arr})
    target = float(fc["Forecast"].iloc[-1])
    upside = (target - price) / price * 100

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=hist.index, y=hist, name="Historical",
        line=dict(color="#4f8ef7",width=2),
        fill="tozeroy", fillcolor="rgba(79,142,247,0.05)"))
    fig2.add_trace(go.Scatter(x=fc["Date"], y=fc["Forecast"], name="Forecast",
        line=dict(color="#ffd600",width=2.5,dash="dash")))
    fig2.add_trace(go.Scatter(
        x=list(fc["Date"]) + list(fc["Date"][::-1]),
        y=list(fc["Upper"]) + list(fc["Lower"][::-1]),
        fill="toself", fillcolor="rgba(255,214,0,0.07)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence Band"))
    fig2.add_annotation(x=str(fc["Date"].iloc[-1].date()), y=target,
        text=f"Target: {cur_sym}{target:,.0f} ({upside:+.1f}%)",
        showarrow=True, arrowhead=2,
        font=dict(color="#ffd600",size=13), bgcolor="#1f2937", bordercolor="#ffd600")
    fig2.update_layout(template="plotly_dark", height=420,
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#c8cee8"), margin=dict(l=10,r=10,t=20,b=10))
    fig2.update_xaxes(title_text="Date")
    fig2.update_yaxes(title_text="Price")
    st.plotly_chart(fig2, width='stretch', config={"responsive": True})

    c1, c2, c3 = st.columns([1, 1, 1], gap="medium")
    c1.metric("Current Price", f"{cur_sym}{price:,.2f}", f"{chg:+.2f}%")
    c2.metric(f"Target ({horizon})", f"{cur_sym}{target:,.0f}", f"{upside:+.1f}%")
    c3.metric("52-Week Range",
              f"{cur_sym}{float(df['Close'].min()):,.0f} – {cur_sym}{float(df['Close'].max()):,.0f}")

    slope_pct = (z[0] / float(hist.iloc[0])) * 100 if hist.iloc[0] != 0 else 0
    st.markdown("#### 📋 Forecast Rationale")
    for item in [
        f"📐 **Trend slope**: {slope_pct:+.3f}% per day over 90 days — {'upward' if slope_pct>0 else 'downward'} bias in the forecast.",
        f"📊 **RSI at {rsi:.1f}**: {'Oversold — recoveries often follow.' if rsi<35 else 'Overbought — near-term resistance possible.' if rsi>70 else 'Neutral — no extreme momentum.'}",
        f"⚡ **MACD at {macdh:+.2f}**: {'Positive — buying momentum building.' if macdh>0 else 'Negative — selling pressure present.'}",
        f"📈 **vs Moving Averages**: Price is {'above' if price>sma50 else 'below'} 50-day and {'above' if price>sma200 else 'below'} 200-day average.",
        f"📉 **Volatility (ATR)**: Daily average swing of {atr:.2f} — used to size the confidence band.",
        f"🎯 **Band**: Upper {cur_sym}{float(fc['Upper'].iloc[-1]):,.0f} / Lower {cur_sym}{float(fc['Lower'].iloc[-1]):,.0f} — based on 1.5× annualised volatility.",
    ]:
        st.markdown(f"<div class='insight-box'>{item}</div>", unsafe_allow_html=True)
    render_forecast_accuracy(selected_ticker, cur_sym)

# ── Tab 3: Compare ───────────────────────────────────────────
with tab3:
    graph_help("Side-by-side performance of up to 4 stocks over 1 year.",
               "All start at 100. Higher line = better 1-year return.",
               "Choose between two stocks. Pick the one with better momentum AND fundamentals.")
    if not compare_names:
        st.info("👈 Select stocks to compare from the sidebar under '⚖️ Compare With'.")
    else:
        all_n = [selected_name] + compare_names
        all_t = [selected_ticker] + [stock_map[n] for n in compare_names]
        colors3 = ["#4f8ef7","#00c853","#ffd600","#e040fb"]
        fig3 = go.Figure()
        for i, (nm, tk) in enumerate(zip(all_n, all_t)):
            d = get_price_data(tk, "1y", cache_buster=cb)
            if not d.empty:
                norm = d["Close"] / float(d["Close"].iloc[0]) * 100
                ret  = (float(d["Close"].iloc[-1]) / float(d["Close"].iloc[0]) - 1) * 100
                fig3.add_trace(go.Scatter(x=d.index, y=norm,
                    name=f"{nm} ({ret:+.1f}%)", line=dict(color=colors3[i%4],width=2)))
        fig3.update_layout(template="plotly_dark", height=400,
            title="1-Year Relative Performance (Base = 100)",
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            legend=dict(orientation="h",y=1.05,x=0.5,xanchor="center"),
            font=dict(color="#c8cee8"), margin=dict(l=10,r=10,t=50,b=10))
        fig3.update_xaxes(title_text="Date")
        fig3.update_yaxes(title_text="Normalised (100=Start)")
        st.plotly_chart(fig3, width='stretch', config={"responsive": True})

        rows = []
        for nm, tk in zip(all_n, all_t):
            inf2 = get_info(tk, cache_buster=cb)
            d2   = get_price_data(tk, "5d", cache_buster=cb)
            cur2 = float(d2["Close"].iloc[-1]) if not d2.empty else 0
            prv2 = float(d2["Close"].iloc[-2]) if len(d2) >= 2 else cur2
            chg2 = (cur2-prv2)/prv2*100 if prv2 else 0
            rows.append({"Stock": nm, "Ticker": tk,
                "Price":   f"{cur_sym}{cur2:,.2f}",
                "1d %":    f"{chg2:+.2f}%",
                "P/E":     f"{inf2.get('trailingPE',0) or 0:.1f}",
                "P/B":     f"{inf2.get('priceToBook',0) or 0:.2f}x",
                "ROE %":   f"{(inf2.get('returnOnEquity',0) or 0)*100:.1f}",
                "Div %":   f"{(inf2.get('dividendYield',0) or 0)*100:.2f}",
                "Mkt Cap": f"{(inf2.get('marketCap',0) or 0)/1e9:.1f}B"})
        st.dataframe(pd.DataFrame(rows).set_index("Stock"), width='stretch')

# ── Tab 4: Insights ──────────────────────────────────────────
with tab4:
    graph_help("Plain-English verdict combining all signals.",
               "Signal badge = overall call. Insights = what data says. Actions = what to do.",
               "Read this last — it's your decision-support summary.")
    insights = []; actions = []; cautions = []
    if rsi < 35:
        insights.append(f"📉 <b>RSI is {rsi:.1f}</b> — stock looks <b>oversold</b>. Often precedes a bounce.")
        actions.append("Consider starting a small position. Spread over 2–3 weeks to average cost.")
    elif rsi > 70:
        insights.append(f"📈 <b>RSI is {rsi:.1f}</b> — stock looks <b>overbought</b>. Upward momentum may slow.")
        cautions.append("Avoid fresh buying. If you hold, consider booking 30–40% of gains.")
    else:
        insights.append(f"📊 <b>RSI is {rsi:.1f}</b> — <b>neutral zone</b>. No extreme signal.")
    if macdh > 0:
        insights.append(f"✅ <b>MACD positive (+{macdh:.2f})</b> — buying momentum building.")
        actions.append("Momentum is in your favour.")
    else:
        insights.append(f"⚠️ <b>MACD negative ({macdh:.2f})</b> — selling pressure stronger.")
        cautions.append("Wait until MACD turns positive before adding.")
    if price > sma50 > sma200:
        insights.append("🌟 Price above both moving averages — <b>Golden Zone</b>. Long-term trend is up.")
        actions.append("Use dips as buying opportunities.")
    elif price < sma50 < sma200:
        insights.append("🚨 Price below both averages — <b>downtrend</b>.")
        cautions.append("Wait for price to cross above the 50-day average before entering.")
    if adx > 25:
        insights.append(f"💪 <b>ADX {adx:.1f}</b> — strong, clear trend direction.")
    else:
        insights.append(f"😴 <b>ADX {adx:.1f}</b> — no clear trend, moving sideways.")
    if upside > 10:
        insights.append(f"🔮 Forecast sees <b>{upside:.1f}% upside</b> over {horizon}.")
        actions.append("Positive forecast. Regular fixed investments reduce timing risk.")
    elif upside < -5:
        insights.append(f"🔮 Forecast shows <b>{upside:.1f}% downside risk</b> over {horizon}.")
        cautions.append("Negative forecast trend. Reduce exposure or wait for reversal.")
    if 0 < pe < 20:
        insights.append(f"💰 <b>P/E {pe:.1f}x</b> — reasonably priced or cheap relative to earnings.")
        actions.append("Valuation is attractive. Long-term investors can accumulate.")
    elif pe > 40:
        insights.append(f"💸 <b>P/E {pe:.1f}x</b> — expensive. High expectations already priced in.")
        cautions.append("High valuation leaves little room for error.")
    if roe > 18:
        insights.append(f"🏆 <b>ROE {roe:.1f}%</b> — very efficient at turning capital into profit.")
    elif 0 < roe < 8:
        insights.append(f"📉 <b>ROE {roe:.1f}%</b> — low return on capital.")

    st.markdown(f"""<div style='background:{sig_color}15;border:1.5px solid {sig_color};
      border-radius:12px;padding:14px 18px;margin-bottom:14px;'>
      <div style='font-size:1.25rem;font-weight:900;color:{sig_color};'>⚡ Overall Signal: {signal}</div>
      <div style='font-size:0.80rem;color:#9aa0b4;margin-top:6px;'>
        {"Strong signals align for a buy." if "BUY" in signal else
         "Mixed signals — patience is the play." if "NEUTRAL" in signal else
         "Multiple warning signs — better opportunities likely ahead."}
      </div></div>""", unsafe_allow_html=True)

    ci, ca, cc = st.columns(3)
    with ci:
        st.markdown("#### 🔍 What the data says")
        for ins in insights:
            st.markdown(f"<div class='insight-box'>{ins}</div>", unsafe_allow_html=True)
    with ca:
        st.markdown("#### ✅ What to consider doing")
        for a in (actions or ["No strong action signal right now. Monitor and wait."]):
            st.markdown(f"<div class='action-box'>→ {a}</div>", unsafe_allow_html=True)
    with cc:
        st.markdown("#### ⚠️ What to be careful about")
        for c in (cautions or ["No major red flags. Keep stop-losses in place."]):
            st.markdown(f"<div class='warn-box'>⚡ {c}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  INDICES OVERVIEW
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<div class='section-title'>🌐 Market Indices — {country}</div>", unsafe_allow_html=True)
graph_help(f"{country} benchmark performance over 6 months.",
           "All normalised to 100 at start. Higher = better.",
           "Is your stock riding a broad market wave or moving on its own merits?")
idx_map  = INDICES.get(country, {})
idx_data = {}
for nm, sym in idx_map.items():
    d = get_price_data(sym, "6mo", cache_buster=cb)
    if not d.empty:
        idx_data[nm]=_safe_close(d)

if idx_data:
    fig_idx = go.Figure()
    idx_colors = ["#4f8ef7","#ffd600","#00c853","#e040fb"]
    for i, (nm, series) in enumerate(idx_data.items()):
        norm = series / float(series.iloc[0]) * 100
        ret  = (float(series.iloc[-1]) / float(series.iloc[0]) - 1) * 100
        fig_idx.add_trace(go.Scatter(x=series.index, y=norm,
            name=f"{nm} ({ret:+.1f}%)", line=dict(color=idx_colors[i%4], width=2)))
    fig_idx.update_layout(template="plotly_dark", height=350,
        title=f"{country} — 6-Month Index Performance (Base = 100)",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        legend=dict(orientation="h",y=1.05,x=0.5,xanchor="center"),
        font=dict(color="#c8cee8"), margin=dict(l=10,r=10,t=50,b=10))
    fig_idx.update_xaxes(title_text="Date")
    fig_idx.update_yaxes(title_text="Index (Base 100)")
    st.plotly_chart(fig_idx, width='stretch', config={"responsive": True})

    idx_cols = st.columns(len(idx_data))
    for i, (nm, sym) in enumerate(idx_map.items()):
        d2 = get_price_data(sym, "5d", cache_buster=cb)
        if not d2.empty and len(d2) >= 2:
            cur2 = float(d2["Close"].iloc[-1]); prv2 = float(d2["Close"].iloc[-2])
            idx_cols[i].metric(nm, f"{cur2:,.0f}", f"{(cur2-prv2)/prv2*100:+.2f}%")

# ─────────────────────────────────────────────────────────────
#  LIVE NEWS FEED
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<div class='section-title'>📰 Live News — {country}</div>", unsafe_allow_html=True)
if news:
    nc = st.columns(2)
    for i, art in enumerate(news):
        with nc[i % 2]:
            st.markdown(f"""<div class='news-card'>
              <div class='news-title'>
                <a href='{art["link"]}' target='_blank' style='color:#7eb3ff;text-decoration:none;'>
                  {art["title"]}</a></div>
              <div class='news-meta'>🗞️ {art["source"]} &nbsp;|&nbsp; 🕐 {art["date"]}</div>
              <div class='news-sum'>{art["summary"]}</div>
            </div>""", unsafe_allow_html=True)
else:
    st.warning("News currently unavailable.")

# ─────────────────────────────────────────────────────────────
#  KPI GLOSSARY
# ─────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📖 KPI Glossary"):
    gc = st.columns(2)
    for i, (name, data) in enumerate(KPI_HELP.items()):
        with gc[i % 2]:
            st.markdown(f"""<div class='group-badge'>
              <b style='color:#c8cee8;'>{name}</b><br>
              {data['plain']}<br>
              🟢 {data.get('green','')} &nbsp; 🔴 {data.get('red','')}
            </div>""", unsafe_allow_html=True)

with st.expander(f"📋 Full {country} Validated Stock List ({len(country_tickers)} stocks)"):
    st.dataframe(pd.DataFrame(
        [{"Company": k, "Ticker": v} for k, v in sorted(country_tickers.items())]
    ), width='stretch', height=400)

# ─────────────────────────────────────────────────────────────
#  FOOTER + AUTO-REFRESH  (always last — page renders first)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#4b5563;font-size:0.74rem;padding:18px;'>
  📊 Global Stock Intelligence v3.3 (Phase 1+2+3) &nbsp;|&nbsp;
  643 Validated Tickers · India 204 · USA 239 · Europe 137 · China 63 &nbsp;|&nbsp;
  Data: Yahoo Finance · Verified RSS Feeds &nbsp;|&nbsp;
  ⚠️ Not SEBI/SEC-registered investment advice.
</div>
""", unsafe_allow_html=True)

render_morning_brief(country, country_tickers, market_open, cb)
render_stock_picks(country_tickers, cur_sym, cb)

# Auto-refresh status in sidebar (fragment handles actual refresh)
if auto_refresh:
    if market_open:
        st.sidebar.markdown(
            "<div style='background:#0d2614;border:1px solid #1a4d24;border-radius:8px;"
            "padding:8px 12px;font-size:0.78rem;color:#00c853;margin-top:8px;'>"
            "🔄 <b>Live polling active</b><br>"
            "<span style='color:#4b8060;'>Price tiles update every 5s.<br>"
            "Charts stay still — no full page reload.</span>"
            "</div>", unsafe_allow_html=True
        )
    else:
        st.sidebar.info(
            f"⏸ Market **CLOSED** for {country}.\n\n"
            "Auto-refresh paused. News and insights show latest cached data."
        )
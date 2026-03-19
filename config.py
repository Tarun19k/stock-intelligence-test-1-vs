# config.py
# Depends on: version.py (re-export), tickers.json (data)
# Called from: all modules
# Contains: ONLY constants, session config, and help text.
#            Ticker data lives in tickers.json.
#            Version history lives in version.py.
# Zero Streamlit calls.

import json
import os
from version import VERSION_LOG, CURRENT_VERSION  # re-exported for back-compat

# ── Ticker data ───────────────────────────────────────────────────────────────
# Load once at import time from tickers.json (same directory as this file).
# All modules that do `from config import GROUPS` continue to work unchanged.
_TICKERS_PATH = os.path.join(os.path.dirname(__file__), "tickers.json")
try:
    with open(_TICKERS_PATH, encoding="utf-8") as _f:
        GROUPS: dict = json.load(_f)
except FileNotFoundError:
    GROUPS = {}
    import warnings
    warnings.warn(
        f"tickers.json not found at {_TICKERS_PATH}. GROUPS will be empty.",
        RuntimeWarning,
        stacklevel=2,
    )
except json.JSONDecodeError as _e:
    GROUPS = {}
    import warnings
    warnings.warn(
        f"tickers.json is malformed: {_e}. GROUPS will be empty.",
        RuntimeWarning,
        stacklevel=2,
    )

# ── Market sessions ───────────────────────────────────────────────────────────
MARKET_SESSIONS: dict = {
    "India":          {"tz": "Asia/Kolkata",      "open": (9,  15), "close": (15, 30)},
    "USA":            {"tz": "America/New_York",   "open": (9,  30), "close": (16,  0)},
    "Europe":         {"tz": "Europe/London",      "open": (8,   0), "close": (16, 30)},
    "China":          {"tz": "Asia/Hong_Kong",     "open": (9,  30), "close": (16,  0)},
    "ETFs - India":   {"tz": "Asia/Kolkata",       "open": (9,  15), "close": (15, 30)},
    "ETFs - Global":  {"tz": "America/New_York",   "open": (9,  30), "close": (16,  0)},
    "Commodities":    {"tz": "America/New_York",   "open": (8,   0), "close": (17, 30)},
    "Debt & Rates":   {"tz": "America/New_York",   "open": (8,   0), "close": (17,  0)},
    "Global Indices": {"tz": "Asia/Kolkata",       "open": (9,  15), "close": (15, 30)},
}

# ── Currency symbols ──────────────────────────────────────────────────────────
CURRENCY: dict = {
    "India":          "₹",
    "USA":            "$",
    "Europe":         "€",
    "China":          "¥",
    "ETFs - India":   "₹",
    "ETFs - Global":  "$",
    "Commodities":    "$",
    "Debt & Rates":   "%",
    "Global Indices": "Pts",
}

# ── Forecast persistence ──────────────────────────────────────────────────────
# Used by forecast.py. On Streamlit Cloud this file will not persist across
# redeploys; forecast.py handles graceful degradation to session_state.
FORECAST_STORE_FILE: str = "forecast_history.json"

# ── Global Intelligence topics ────────────────────────────────────────────────
GLOBAL_TOPICS: dict = {
    "🔴 West Asia Conflict": {
        "color": "#ff4444",
        "subtitle": "Geopolitical Crisis · Supply Chain · Consumer Impact",
        "overview": (
            "The ongoing conflict across West Asia is reshaping global trade routes, "
            "energy supply chains, and inflationary pressures — with second and third-order "
            "effects felt from crude oil desks in Mumbai to grocery shelves worldwide."
        ),
        "chain": [
            ("Active Conflict Zones",    "#7f0000", "Direct military engagement in Gaza, Lebanon, Red Sea"),
            ("Regional Destabilisation", "#b71c1c", "Iran–Israel tensions, Houthi Red Sea attacks"),
            ("Oil & Energy Supply Risk", "#c62828", "Strait of Hormuz risk premium, Brent spike"),
            ("Shipping Route Disruption","#d32f2f", "Suez Canal diversions → +14 days transit → +30% freight"),
            ("Global Energy Inflation",  "#e53935", "Fuel, fertiliser, plastics cost surge"),
            ("Supply Chain Repricing",   "#ef5350", "Electronics, autos, agriculture inputs"),
            ("Consumer Goods Costs",     "#ff7043", "Edible oils, fuel, transport — basic needs impacted"),
        ],
        "market_sectors": ["Energy", "Defense & Aerospace", "Shipping & Logistics", "FMCG", "Agri"],
        "rss": [
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://feeds.reuters.com/reuters/worldNews",
            "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        ],
        "india_impact": (
            "India imports ~87% of its crude oil. Every $10/bbl rise in Brent adds ~₹1.2L cr "
            "to the import bill, weakens INR ~50–80 paise, and pushes petrol/diesel up ₹2–4/litre. "
            "FMCG and logistics companies see direct margin compression."
        ),
        "watchlist": ["BPCL.NS", "IOC.NS", "ONGC.NS", "HAL.NS", "BEL.NS", "MAZDOCK.NS"],
    },
    "🤖 AI & Job Markets": {
        "color": "#4f8ef7",
        "subtitle": "Technology Disruption · Workforce Evolution · New Opportunities",
        "overview": (
            "Generative AI is compressing the automation curve from decades to years. "
            "White-collar roles in software, legal, finance, and media are being repriced. "
            "Simultaneously, new roles in AI oversight, prompt engineering, and human-AI "
            "collaboration are emerging faster than universities can respond."
        ),
        "chain": [
            ("Foundation Model Capabilities", "#0d47a1", "GPT-5, Gemini 2, Claude 4 — reasoning at expert level"),
            ("Enterprise Adoption Wave",      "#1565c0", "70% of Fortune 500 deploying AI co-pilots by 2026"),
            ("Task-Level Automation",         "#1976d2", "Code generation, legal review, customer support, data analysis"),
            ("Job Role Displacement",         "#1e88e5", "Entry-level IT, BPO, content, paralegal at risk"),
            ("Reskilling & New Roles",        "#2196f3", "AI trainers, ethics auditors, integration architects"),
            ("Productivity & GDP Gains",      "#42a5f5", "McKinsey: $4.4T annual value from GenAI"),
            ("Market Repricing",              "#64b5f6", "IT multiples shift — services vs platforms diverge"),
        ],
        "market_sectors": ["IT Services", "Cloud & SaaS", "EdTech", "Robotics", "Semiconductors"],
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
        "watchlist": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "PERSISTENT.NS", "LTIM.NS"],
    },
}

NEXT_STEPS_AI: list = [
    ("📚 Upskill Immediately",
     "Python + LLM APIs (OpenAI, Gemini). 3 months of consistent learning creates a "
     "defensible skill moat. Free resources: fast.ai, Deeplearning.ai, Hugging Face.", "#00c853"),
    ("💼 Audit Your Role",
     "Identify which 40% of your daily tasks could be AI-assisted. Build that tool yourself — "
     "it makes you the expert instead of the disrupted.", "#4f8ef7"),
    ("📈 Invest in the Infrastructure",
     "AI demand runs on semiconductors (NVDA, TSM), cloud (MSFT Azure, AWS, GCP), and "
     "data pipelines. Platform winners compound faster than service providers.", "#ff9800"),
    ("🌐 Follow the Hiring Signal",
     "Track job postings weekly for AI roles in your sector. A 3x spike in a domain is a "
     "leading indicator of where value is migrating — both as a career and investment signal.", "#e040fb"),
    ("🛡️ Diversify Income Streams",
     "AI makes knowledge productisable. Build one passive asset: a course, a tool, a niche "
     "newsletter. These compound while your primary income remains intact.", "#00bcd4"),
]

# ── KPI help tooltips ─────────────────────────────────────────────────────────
KPI_HELP: dict = {
    "Price":      "Latest closing price from Yahoo Finance",
    "Change %":   "1-day percentage change vs prior close",
    "52W High":   "Highest price over the trailing 52 weeks",
    "52W Low":    "Lowest price over the trailing 52 weeks",
    "Volume":     "Total shares/units traded today",
    "Market Cap": "Total market capitalisation",
    "P/E Ratio":  "Price-to-Earnings — valuation multiple",
    "Beta":       "Volatility relative to the broader market (1 = market, >1 = more volatile)",
}

# ── Technical & section help text ────────────────────────────────────────────
HELP_TEXT: dict = {
    # Header badges
    "signal": (
        "Overall verdict combining all technical + fundamental signals. "
        "BUY = strong positive alignment. WATCH = mixed signals — monitor before acting. "
        "CAUTION = warning signs present, risk elevated. SELL = multiple negative signals."
    ),
    "score": (
        "Composite score 0–100 combining RSI, MACD, ADX, Stochastic, Bollinger, "
        "P/E, ROE and trend direction. Above 60 = bullish. Below 40 = bearish. 40–60 = neutral."
    ),
    "ticker": (
        "Exchange symbol used to fetch live data. "
        ".NS = NSE India. .BO = Bombay Stock Exchange. No suffix = US (NYSE/Nasdaq). "
        "^ prefix = market index (e.g. ^NSEI = Nifty 50, ^GSPC = S&P 500). "
        "=F suffix = futures contract (e.g. GC=F = Gold futures). "
        "Debt & Rates values are yields (%); Global Indices values are in points (Pts)."
    ),
    # KPI panel
    "rsi": (
        "RSI (Relative Strength Index, 14 days) — momentum on a 0–100 scale. "
        "Below 30 = oversold, potential bounce. Above 70 = overbought, potential pullback. "
        "30–70 = neutral zone."
    ),
    "macd_h": (
        "MACD Histogram = MACD line minus Signal line. "
        "Positive and growing = buying momentum building. "
        "Negative and shrinking = selling pressure easing. "
        "Flip from negative → positive = early buy signal."
    ),
    "bbw": (
        "Bollinger Band Width — how wide the price bands are vs the moving average (%). "
        "High % = high volatility, large swings expected. "
        "Low % = quiet market, often precedes a sharp breakout."
    ),
    "atr": (
        "ATR (Average True Range) — average daily price swing in currency terms. "
        "Higher = more volatile stock. Use to size positions: larger ATR = smaller position."
    ),
    "adx": (
        "ADX (Average Directional Index) — trend strength, not direction. "
        "Above 25 = strong trend in place. Below 20 = no clear trend, ranging market."
    ),
    "stoch": (
        "Stochastic %K — today's price vs recent highs/lows (0–100). "
        "Below 30 = near recent low, potential buy zone. "
        "Above 75 = near recent high, potential sell zone."
    ),
    "pe_pb": (
        "P/E (Price-to-Earnings): how much you pay per ₹1 of profit. "
        "P/B (Price-to-Book): how much you pay vs net asset value. "
        "Lower values = potentially cheaper — but fast-growing companies carry higher ratios."
    ),
    "roe_revg": (
        "ROE (Return on Equity): how efficiently the company uses shareholder money — above 15% is strong. "
        "Rev Growth: year-on-year revenue growth %. Positive = business expanding."
    ),
    "obv_vol": (
        "OBV (On-Balance Volume): running total of buying vs selling pressure (millions). "
        "Rising OBV with rising price = healthy uptrend. "
        "Falling OBV with rising price = rally may be running out of steam."
    ),
    # Charts tab
    "sma": (
        "SMA (Simple Moving Average) — average closing price over a period. "
        "SMA20 (cyan) = short-term. SMA50 (yellow) = medium. SMA200 (orange) = long-term. "
        "Price above all three = strong uptrend."
    ),
    "bollinger": (
        "Bollinger Bands — 2 standard deviations above/below SMA20. "
        "Price at upper band = potentially overbought. Price at lower band = potentially oversold. "
        "Bands squeezing = low volatility, breakout often follows."
    ),
    "candlestick": (
        "Each candle = one trading day. "
        "Green = closed higher than it opened (bullish). Red = closed lower (bearish). "
        "Thin wicks = the day's high and low range."
    ),
    # Forecast tab
    "lookback": (
        "Days of historical data used to calculate the trend direction. "
        "Longer = smoother long-term signal. Shorter = more responsive to recent moves."
    ),
    "horizon": (
        "How far ahead the forecast projects. 1M ≈ 21 trading days. 3M ≈ 63 days. "
        "Longer horizons have wider confidence bands — uncertainty grows over time."
    ),
    "confidence_band": (
        "Shaded area = confidence range based on 1.5× annualised volatility. "
        "High probability the price stays within this band, "
        "but earnings or news can push it outside."
    ),
    # Insights tab
    "insights_section": (
        "Plain-English summary of what the technical and fundamental signals are saying together — "
        "no formulas, just conclusions."
    ),
    "actions_section": (
        "Suggested starting points based on the current signal combination. "
        "Not financial advice — always consider your own risk tolerance and timeline."
    ),
    "cautions_section": (
        "Warning flags raised by the current signals. "
        "Even BUY-rated stocks can have cautions — use these to manage risk."
    ),
    # Home page
    "market_status": (
        "Live session status based on official trading hours. "
        "OPEN = you can trade now. CLOSED = prices shown are from the last close. "
        "Times shown in the exchange's local timezone."
    ),
    "top_movers": (
        "Stocks with the highest % price change today. "
        "High movers often have news or events driving them — click a name to investigate."
    ),
    # Week summary
    "weekly_heatmap": (
        "Weekly return for each Nifty 50 stock (% change from Monday open to now). "
        "Green = positive week. Red = negative week. Longer bar = bigger move."
    ),
    "sector_snapshot": (
        "Weekly performance of each major NSE sector index. "
        "Shows which sectors are leading (outperforming) vs lagging this week."
    ),
}

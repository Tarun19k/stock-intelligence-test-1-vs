# config.py
# Depends on: nothing
# Called from: all modules
# Contains: all constants, dicts, version log — zero Streamlit calls

from datetime import datetime

# ── Version Log ───────────────────────────────────────────────────────────────
VERSION_LOG = [
    {"version": "v1.0",  "date": "2026-02-28", "notes": "Initial build — India stocks, 5 KPIs"},
    {"version": "v2.0",  "date": "2026-03-06", "notes": "USP layer: NLP sentiment, narrative detector, Monte Carlo ROI"},
    {"version": "v3.0",  "date": "2026-03-10", "notes": "643 validated tickers across India/USA/Europe/China"},
    {"version": "v3.1",  "date": "2026-03-10", "notes": "Phase 2: scrolling tickers, news feed, morning brief"},
    {"version": "v3.2",  "date": "2026-03-10", "notes": "Live auto-refresh via st.fragment — no full page reload"},
    {"version": "v3.3",  "date": "2026-03-10", "notes": "Phase 3: forecast accuracy tracking + auto-correction logic"},
    {"version": "v3.4",  "date": "2026-03-11", "notes": "[dev skip] Rapid iteration day — v3.4 tag not cut; changes rolled into v3.5"},
    {"version": "v3.5",  "date": "2026-03-11", "notes": "Phase 4-5: nav realign, global tickers, top movers, dashboard reorder"},
    {"version": "v3.6",  "date": "2026-03-11", "notes": "[dev skip] UI overhaul started same day; v3.6 tag not cut; promoted directly to v4.1"},
    {"version": "v4.1",  "date": "2026-03-11", "notes": "Fully responsive UI — mobile/tablet/desktop CSS + Plotly responsive config"},
    {"version": "v5.0",  "date": "2026-03-14", "notes": "Refactor: 10-file modular structure"},
    {"version": "v5.1",  "date": "2026-03-16", "notes": "USA stock universe expanded: +8 groups, 169 total US tickers incl. Accenture, IBM, Palo Alto, Coinbase, Tesla, Boeing"},
    {"version": "v5.2",  "date": "2026-03-17", "notes": "Ticker bar fix: z-index 9999→1000000, Streamlit header suppressed, width:100vw, sidebar push-down"},
    {"version": "v5.3",  "date": "2026-03-17", "notes": "Streamlit toolbar buttons hidden for clean production UI"},
    {"version": "v5.4",  "date": "2026-03-17", "notes": "Localised tab filters: Forecast horizon+lookback inline, Compare With multiselect+period inline"},
    {"version": "v5.5",  "date": "2026-03-17", "notes": "Deprecation fix: use_container_width replaced with width=\'stretch\' across all files"},
    {"version": "v5.6",  "date": "2026-03-17", "notes": "Insights cards fix: sanitise_bold() added, explicit text colors on all 3 card types"},
    {"version": "v5.7",  "date": "2026-03-17", "notes": "Global readability audit: dark bg missing-color fixes across app.py, dashboard, global_intelligence, utils, styles"},
    {"version": "v5.8",  "date": "2026-03-17", "notes": "Audit session: cross-file import scan, 38 issues catalogued across 10 categories"},
    {"version": "v5.9",  "date": "2026-03-18", "notes": "Patches shipped: _safe_close (5 files), sanitise_bold import, NEWS_FEEDS self-ref fix, ticker CSS split, market sessions moved to Homepage"},
    {"version": "v5.10", "date": "2026-03-18", "notes": "UI fixes: ticker via window.parent JS (truly fixed overlay), vv5.9 double-v, MPA sidebar nav hidden"},
    {"version": "v5.11", "date": "2026-03-18", "notes": "RSS allowlist: bbci.co.uk + bbc.co.uk added; all http:// feed URLs upgraded to https://"},
    {"version": "v5.12", "date": "2026-03-18", "notes": "Regression suite: pd import fix in global_intelligence.py; full 10-category validation green"},
    {"version": "v5.13", "date": "2026-03-18", "notes": "Ticker fix: TATAMOTORS.NS delisted Oct 2025 demerger — replaced with TMCV.NS (CV) + TMPV.NS (PV/EV) in 4 locations"},
    {"version": "v5.14", "date": "2026-03-18", "notes": "Auto-refresh redesign: @st.fragment (1s tick, non-blocking), scoped rerun, Dashboard manual refresh, toggle key persists"},
    {"version": "v5.15", "date": "2026-03-18", "notes": "Auto-refresh: fragment called inside sidebar (fixes StreamlitAPIException), market-open auto-toggle, partial UI refresh (dynamic sections only)"},
    {"version": "v5.15.1","date": "2026-03-18", "notes": "Hotfix: market_open param missing from render_dashboard — was fixed in memory but not written to zip; _live_kpi_panel also backfilled"},
    {"version": "v5.15.2","date": "2026-03-18", "notes": "Added regression.py (166-check suite, KI-coded) + KNOWN_ISSUES_LOG.md (KI-001 thru KI-014 + EXT-001 thru EXT-003)"},
]
CURRENT_VERSION = VERSION_LOG[-1]["version"]

# ── Market Sessions ────────────────────────────────────────────────────────────
MARKET_SESSIONS = {
    "India":          {"tz": "Asia/Kolkata",    "open": (9, 15),  "close": (15, 30)},
    "USA":            {"tz": "America/New_York", "open": (9, 30),  "close": (16, 0)},
    "Europe":         {"tz": "Europe/London",   "open": (8, 0),   "close": (16, 30)},
    "China":          {"tz": "Asia/Hong_Kong",  "open": (9, 30),  "close": (16, 0)},
    "ETFs - India":   {"tz": "Asia/Kolkata",    "open": (9, 15),  "close": (15, 30)},
    "ETFs - Global":  {"tz": "America/New_York","open": (9, 30),  "close": (16, 0)},
    "Commodities":    {"tz": "America/New_York","open": (8, 0),   "close": (17, 30)},
    "Debt & Rates":   {"tz": "America/New_York","open": (8, 0),   "close": (17, 0)},
    "Global Indices": {"tz": "Asia/Kolkata",    "open": (9, 15),  "close": (15, 30)},
}

# ── Currency symbols per country group ────────────────────────────────────────
CURRENCY = {
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

# ── Forecast store file path ───────────────────────────────────────────────────
FORECAST_STORE_FILE = "forecast_history.json"

# ── Global Intelligence Topics ────────────────────────────────────────────────
GLOBAL_TOPICS = {
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
        "watchlist": ["BPCL.NS","IOC.NS","ONGC.NS","HAL.NS","BEL.NS","MAZDOCK.NS"],
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
            ("Task‑Level Automation",         "#1976d2", "Code generation, legal review, customer support, data analysis"),
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
        "watchlist": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","PERSISTENT.NS","LTIM.NS"],
    },
}

NEXT_STEPS_AI = [
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

# ── KPI Help Text ─────────────────────────────────────────────────────────────
KPI_HELP = {
    "Price":       "Latest closing price from Yahoo Finance",
    "Change %":    "1-day percentage change vs prior close",
    "52W High":    "Highest price over the trailing 52 weeks",
    "52W Low":     "Lowest price over the trailing 52 weeks",
    "Volume":      "Total shares/units traded today",
    "Market Cap":  "Total market capitalisation",
    "P/E Ratio":   "Price-to-Earnings — valuation multiple",
    "Beta":        "Volatility relative to the broader market (1 = market, >1 = more volatile)",
}


# ═══════════════════════════════════════════════════════════════════
# STOCK GROUPS — Full India Universe
# 334 entries · Nifty50 · NiftyNext50 · Sensex · Sectoral · Smallcap
# ═══════════════════════════════════════════════════════════════════
GROUPS = {
    "India": {
        "🏆 Nifty 50": {
            "Reliance Industries":          "RELIANCE.NS",
            "TCS":                          "TCS.NS",
            "HDFC Bank":                    "HDFCBANK.NS",
            "Infosys":                      "INFY.NS",
            "ICICI Bank":                   "ICICIBANK.NS",
            "Hindustan Unilever":           "HINDUNILVR.NS",
            "ITC":                          "ITC.NS",
            "SBI":                          "SBIN.NS",
            "Bharti Airtel":                "BHARTIARTL.NS",
            "Kotak Mahindra Bank":          "KOTAKBANK.NS",
            "Larsen & Toubro":              "LT.NS",
            "HCL Technologies":             "HCLTECH.NS",
            "Asian Paints":                 "ASIANPAINT.NS",
            "Axis Bank":                    "AXISBANK.NS",
            "Wipro":                        "WIPRO.NS",
            "Maruti Suzuki":                "MARUTI.NS",
            "Sun Pharmaceutical":           "SUNPHARMA.NS",
            "Titan Company":                "TITAN.NS",
            "Bajaj Finance":                "BAJFINANCE.NS",
            "Nestle India":                 "NESTLEIND.NS",
            "UltraTech Cement":             "ULTRACEMCO.NS",
            "NTPC":                         "NTPC.NS",
            "Power Grid Corp":              "POWERGRID.NS",
            "Mahindra & Mahindra":          "M&M.NS",
            "ONGC":                         "ONGC.NS",
            "Divi's Laboratories":          "DIVISLAB.NS",
            "Bajaj Finserv":                "BAJAJFINSV.NS",
            "Dr. Reddy's Laboratories":     "DRREDDY.NS",
            "Adani Ports":                  "ADANIPORTS.NS",
            "Tata Motors":                  "TMCV.NS",
            "Tata Steel":                   "TATASTEEL.NS",
            "Cipla":                        "CIPLA.NS",
            "Eicher Motors":                "EICHERMOT.NS",
            "Hero MotoCorp":                "HEROMOTOCO.NS",
            "Hindalco Industries":          "HINDALCO.NS",
            "IndusInd Bank":                "INDUSINDBK.NS",
            "JSW Steel":                    "JSWSTEEL.NS",
            "Coal India":                   "COALINDIA.NS",
            "Bajaj Auto":                   "BAJAJ-AUTO.NS",
            "Grasim Industries":            "GRASIM.NS",
            "Tata Consumer Products":       "TATACONSUM.NS",
            "Tech Mahindra":                "TECHM.NS",
            "Apollo Hospitals":             "APOLLOHOSP.NS",
            "Britannia Industries":         "BRITANNIA.NS",
            "HDFC Life Insurance":          "HDFCLIFE.NS",
            "SBI Life Insurance":           "SBILIFE.NS",
            "Shriram Finance":              "SHRIRAMFIN.NS",
            "Adani Enterprises":            "ADANIENT.NS",
            "BEL":                          "BEL.NS",
        },
        "🥈 Nifty Next 50": {
            "Adani Green Energy":           "ADANIGREEN.NS",
            "Adani Total Gas":              "ATGL.NS",
            "Ambuja Cements":               "AMBUJACEMENT.NS",
            "Avenue Supermarts (DMart)":    "DMART.NS",
            "Bandhan Bank":                 "BANDHANBNK.NS",
            "Bank of Baroda":               "BANKBARODA.NS",
            "Berger Paints":                "BERGEPAINT.NS",
            "Bosch":                        "BOSCHLTD.NS",
            "Canara Bank":                  "CANBK.NS",
            "Cholamandalam Investment":     "CHOLAFIN.NS",
            "DLF":                          "DLF.NS",
            "Godrej Consumer Products":     "GODREJCP.NS",
            "Havells India":                "HAVELLS.NS",
            "Indian Oil Corp":              "IOC.NS",
            "Info Edge (Naukri)":           "NAUKRI.NS",
            "IndiGo":                       "INDIGO.NS",
            "Lodha (Macrotech)":            "LODHA.NS",
            "LTIMindtree":                  "LTIM.NS",
            "Lupin":                        "LUPIN.NS",
            "Muthoot Finance":              "MUTHOOTFIN.NS",
            "Persistent Systems":           "PERSISTENT.NS",
            "PI Industries":                "PIIND.NS",
            "Punjab National Bank":         "PNB.NS",
            "SBI Cards":                    "SBICARD.NS",
            "Siemens India":                "SIEMENS.NS",
            "Tata Communications":          "TATACOMM.NS",
            "Tata Power":                   "TATAPOWER.NS",
            "Torrent Pharmaceuticals":      "TORNTPHARM.NS",
            "TVS Motor":                    "TVSMOTOR.NS",
            "Varun Beverages":              "VBL.NS",
            "Vedanta":                      "VEDL.NS",
            "Zomato":                       "ZOMATO.NS",
            "Paytm":                        "PAYTM.NS",
            "Nykaa":                        "NYKAA.NS",
            "Policybazaar":                 "POLICYBZR.NS",
            "Dixon Technologies":           "DIXON.NS",
            "Cummins India":                "CUMMINSIND.NS",
            "Oracle Financial Services":    "OFSS.NS",
            "Pidilite Industries":          "PIDILITIND.NS",
            "Colgate-Palmolive India":      "COLPAL.NS",
        },
        "📊 Sensex 30": {
            "Reliance Industries":          "RELIANCE.NS",
            "TCS":                          "TCS.NS",
            "HDFC Bank":                    "HDFCBANK.NS",
            "Infosys":                      "INFY.NS",
            "ICICI Bank":                   "ICICIBANK.NS",
            "Hindustan Unilever":           "HINDUNILVR.NS",
            "ITC":                          "ITC.NS",
            "SBI":                          "SBIN.NS",
            "Bharti Airtel":                "BHARTIARTL.NS",
            "Kotak Mahindra Bank":          "KOTAKBANK.NS",
            "Larsen & Toubro":              "LT.NS",
            "HCL Technologies":             "HCLTECH.NS",
            "Asian Paints":                 "ASIANPAINT.NS",
            "Axis Bank":                    "AXISBANK.NS",
            "Wipro":                        "WIPRO.NS",
            "Maruti Suzuki":                "MARUTI.NS",
            "Sun Pharmaceutical":           "SUNPHARMA.NS",
            "Titan Company":                "TITAN.NS",
            "Bajaj Finance":                "BAJFINANCE.NS",
            "Nestle India":                 "NESTLEIND.NS",
            "UltraTech Cement":             "ULTRACEMCO.NS",
            "NTPC":                         "NTPC.NS",
            "Power Grid Corp":              "POWERGRID.NS",
            "Mahindra & Mahindra":          "M&M.NS",
            "Tata Steel":                   "TATASTEEL.NS",
            "Bajaj Finserv":                "BAJAJFINSV.NS",
            "Tata Motors":                  "TMCV.NS",
            "IndusInd Bank":                "INDUSINDBK.NS",
            "JSW Steel":                    "JSWSTEEL.NS",
            "Tech Mahindra":                "TECHM.NS",
        },
        "💻 IT & Technology": {
            "TCS":                          "TCS.NS",
            "Infosys":                      "INFY.NS",
            "HCL Technologies":             "HCLTECH.NS",
            "Wipro":                        "WIPRO.NS",
            "Tech Mahindra":                "TECHM.NS",
            "LTIMindtree":                  "LTIM.NS",
            "Persistent Systems":           "PERSISTENT.NS",
            "Mphasis":                      "MPHASIS.NS",
            "Coforge":                      "COFORGE.NS",
            "L&T Technology Services":      "LTTS.NS",
            "KPIT Technologies":            "KPITTECH.NS",
            "Tata Elxsi":                   "TATAELXSI.NS",
            "Oracle Financial Services":    "OFSS.NS",
            "Zensar Technologies":          "ZENSARTECH.NS",
            "Mastek":                       "MASTEK.NS",
            "Birlasoft":                    "BSOFT.NS",
            "Info Edge (Naukri)":           "NAUKRI.NS",
            "Zomato":                       "ZOMATO.NS",
            "Paytm":                        "PAYTM.NS",
        },
        "🏦 Banks & Finance": {
            "HDFC Bank":                    "HDFCBANK.NS",
            "ICICI Bank":                   "ICICIBANK.NS",
            "SBI":                          "SBIN.NS",
            "Kotak Mahindra Bank":          "KOTAKBANK.NS",
            "Axis Bank":                    "AXISBANK.NS",
            "IndusInd Bank":                "INDUSINDBK.NS",
            "Bajaj Finance":                "BAJFINANCE.NS",
            "Bajaj Finserv":                "BAJAJFINSV.NS",
            "Bank of Baroda":               "BANKBARODA.NS",
            "Canara Bank":                  "CANBK.NS",
            "Punjab National Bank":         "PNB.NS",
            "Federal Bank":                 "FEDERALBNK.NS",
            "IDFC First Bank":              "IDFCFIRSTB.NS",
            "Bandhan Bank":                 "BANDHANBNK.NS",
            "AU Small Finance Bank":        "AUBANK.NS",
            "Shriram Finance":              "SHRIRAMFIN.NS",
            "Muthoot Finance":              "MUTHOOTFIN.NS",
            "Cholamandalam Investment":     "CHOLAFIN.NS",
            "HDFC Life Insurance":          "HDFCLIFE.NS",
            "SBI Life Insurance":           "SBILIFE.NS",
            "SBI Cards":                    "SBICARD.NS",
        },
        "💊 Pharma & Healthcare": {
            "Sun Pharmaceutical":           "SUNPHARMA.NS",
            "Divi's Laboratories":          "DIVISLAB.NS",
            "Dr. Reddy's Laboratories":     "DRREDDY.NS",
            "Cipla":                        "CIPLA.NS",
            "Lupin":                        "LUPIN.NS",
            "Apollo Hospitals":             "APOLLOHOSP.NS",
            "Torrent Pharmaceuticals":      "TORNTPHARM.NS",
            "Biocon":                       "BIOCON.NS",
            "Aurobindo Pharma":             "AUROPHARMA.NS",
            "Glenmark Pharmaceuticals":     "GLENMARK.NS",
            "Ipca Laboratories":            "IPCALAB.NS",
            "Mankind Pharma":               "MANKIND.NS",
            "Max Healthcare":               "MAXHEALTH.NS",
            "Fortis Healthcare":            "FORTIS.NS",
            "Alkem Laboratories":           "ALKEM.NS",
            "Laurus Labs":                  "LAURUSLABS.NS",
            "Cupid":                        "CUPID.NS",
            "Granules India":               "GRANULES.NS",
            "Natco Pharma":                 "NATCOPHARM.NS",
            "JB Chemicals":                 "JBCHEPHARM.NS",
        },
        "🚗 Auto & EV": {
            "Maruti Suzuki":                "MARUTI.NS",
            "Tata Motors (CV)":             "TMCV.NS",
            "Tata Motors (PV)": "TMPV.NS",
            "Mahindra & Mahindra":          "M&M.NS",
            "Hero MotoCorp":                "HEROMOTOCO.NS",
            "Bajaj Auto":                   "BAJAJ-AUTO.NS",
            "Eicher Motors":                "EICHERMOT.NS",
            "TVS Motor":                    "TVSMOTOR.NS",
            "Ashok Leyland":                "ASHOKLEY.NS",
            "Bosch":                        "BOSCHLTD.NS",
            "Motherson Sumi":               "MOTHERSON.NS",
            "Bharat Forge":                 "BHARATFORG.NS",
            "Exide Industries":             "EXIDEIND.NS",
            "Amara Raja Energy":            "AMARAJABAT.NS",
            "Ola Electric":                 "OLAELECTRIC.NS",
            "Olectra Greentech":            "OLECTRA.NS",
        },
        "🏠 FMCG & Consumer": {
            "Hindustan Unilever":           "HINDUNILVR.NS",
            "ITC":                          "ITC.NS",
            "Nestle India":                 "NESTLEIND.NS",
            "Britannia Industries":         "BRITANNIA.NS",
            "Dabur India":                  "DABUR.NS",
            "Marico":                       "MARICO.NS",
            "Godrej Consumer Products":     "GODREJCP.NS",
            "Colgate-Palmolive India":      "COLPAL.NS",
            "Varun Beverages":              "VBL.NS",
            "Tata Consumer Products":       "TATACONSUM.NS",
            "Emami":                        "EMAMILTD.NS",
            "Jyothy Labs":                  "JYOTHYLAB.NS",
            "Avenue Supermarts (DMart)":    "DMART.NS",
            "Jubilant FoodWorks":           "JUBLFOOD.NS",
        },
        "⚡ Energy & Power": {
            "Reliance Industries":          "RELIANCE.NS",
            "ONGC":                         "ONGC.NS",
            "NTPC":                         "NTPC.NS",
            "Power Grid Corp":              "POWERGRID.NS",
            "Tata Power":                   "TATAPOWER.NS",
            "Adani Power":                  "ADANIPOWER.NS",
            "Adani Green Energy":           "ADANIGREEN.NS",
            "BPCL":                         "BPCL.NS",
            "Indian Oil Corp":              "IOC.NS",
            "GAIL India":                   "GAIL.NS",
            "Oil India":                    "OIL.NS",
            "Torrent Power":                "TORNTPOWER.NS",
            "JSW Energy":                   "JSWENERGY.NS",
        },
        "🏗️ Infra & Real Estate": {
            "Larsen & Toubro":              "LT.NS",
            "DLF":                          "DLF.NS",
            "Lodha (Macrotech)":            "LODHA.NS",
            "Godrej Properties":            "GODREJPROP.NS",
            "Oberoi Realty":                "OBEROIRLTY.NS",
            "Prestige Estates":             "PRESTIGE.NS",
            "Sobha":                        "SOBHA.NS",
            "Phoenix Mills":                "PHOENIXLTD.NS",
            "Brigade Enterprises":          "BRIGADE.NS",
            "NCC":                          "NCC.NS",
            "Adani Ports":                  "ADANIPORTS.NS",
            "Container Corp":               "CONCOR.NS",
            "GMR Airports":                 "GMRINFRA.NS",
        },
        "🔩 Metals & Mining": {
            "Tata Steel":                   "TATASTEEL.NS",
            "JSW Steel":                    "JSWSTEEL.NS",
            "Hindalco Industries":          "HINDALCO.NS",
            "Vedanta":                      "VEDL.NS",
            "Coal India":                   "COALINDIA.NS",
            "NMDC":                         "NMDC.NS",
            "Steel Authority (SAIL)":       "SAIL.NS",
            "Jindal Steel & Power":         "JINDALSTEL.NS",
            "National Aluminium (NALCO)":   "NATIONALUM.NS",
            "Hindustan Copper":             "HINDCOPPER.NS",
            "APL Apollo Tubes":             "APLAPOLLO.NS",
        },
        "🛡️ Defence & Aerospace": {
            "HAL":                          "HAL.NS",
            "BEL":                          "BEL.NS",
            "BHEL":                         "BHEL.NS",
            "Mazagon Dock":                 "MAZDOCK.NS",
            "Garden Reach Shipbuilders":    "GRSE.NS",
            "Cochin Shipyard":              "COCHINSHIP.NS",
            "Bharat Dynamics":              "BDL.NS",
            "Data Patterns":                "DATAPATTNS.NS",
            "MTAR Technologies":            "MTARTECH.NS",
            "Paras Defence":                "PARAS.NS",
        },
        "🧵 Textiles & Apparel": {
            "Trident":                      "TRIDENT.NS",
            "Welspun India":                "WELSPUNIND.NS",
            "Vardhman Textiles":            "VTL.NS",
            "Raymond":                      "RAYMOND.NS",
            "Page Industries (Jockey)":     "PAGEIND.NS",
            "Arvind":                       "ARVIND.NS",
            "KPR Mill":                     "KPRMILL.NS",
            "Nitin Spinners":               "NITINSPIN.NS",
            "Indo Count Industries":        "ICIL.NS",
            "Gokaldas Exports":             "GOKALDAS.NS",
        },
        "🏭 Smallcap — Specialty Chemicals": {
            "Balaji Amines":                "BALAMINES.NS",
            "Gujarat Fluorochemicals":      "FLUOROCHEM.NS",
            "Alkyl Amines":                 "ALKYLAMINE.NS",
            "Deepak Nitrite":               "DEEPAKNTR.NS",
            "Clean Science":                "CLEAN.NS",
            "Fine Organic Industries":      "FINEORG.NS",
            "Navin Fluorine":               "NAVINFLUOR.NS",
            "Galaxy Surfactants":           "GALAXYSURF.NS",
            "Vinati Organics":              "VINATIORGA.NS",
            "Aarti Industries":             "AARTIIND.NS",
            "Ami Organics":                 "AMIORG.NS",
            "Anupam Rasayan":               "ANURAS.NS",
        },
        "📡 Telecom & Media": {
            "Bharti Airtel":                "BHARTIARTL.NS",
            "Vodafone Idea":                "IDEA.NS",
            "Indus Towers":                 "INDUSTOWER.NS",
            "Tata Communications":          "TATACOMM.NS",
            "Sun TV Network":               "SUNTV.NS",
            "Zee Entertainment":            "ZEEL.NS",
            "PVR Inox":                     "PVRINOX.NS",
        },
        "🏨 Hospitality & Travel": {
            "Indian Hotels (Taj)":          "INDHOTEL.NS",
            "EIH (Oberoi Hotels)":          "EIHOTEL.NS",
            "Lemon Tree Hotels":            "LEMONTREE.NS",
            "IndiGo":                       "INDIGO.NS",
            "SpiceJet":                     "SPICEJET.NS",
            "Mahindra Holidays":            "MHRIL.NS",
        },
        "📈 Indices": {
            "Nifty 50":                     "^NSEI",
            "Sensex":                       "^BSESN",
            "Nifty Bank":                   "^NSEBANK",
            "Nifty IT":                     "^CNXIT",
            "Nifty Pharma":                 "^CNXPHARMA",
            "Nifty Midcap 100":             "^NSEMDCP100",
            "Nifty Smallcap 100":           "^NSESC100",
            "Nifty Auto":                   "^CNXAUTO",
            "Nifty FMCG":                   "^CNXFMCG",
            "Nifty Realty":                 "^CNXREALTY",
            "Nifty Metal":                  "^CNXMETAL",
            "Nifty Energy":                 "^CNXENERGY",
        },
    },
    "USA": {
        "🏆 S&P 500 — Mega Cap": {
            "Apple":                        "AAPL",
            "Microsoft":                    "MSFT",
            "Nvidia":                       "NVDA",
            "Alphabet (Google)":            "GOOGL",
            "Amazon":                       "AMZN",
            "Meta":                         "META",
            "Tesla":                        "TSLA",
            "Berkshire Hathaway B":         "BRK-B",
            "Broadcom":                     "AVGO",
            "JPMorgan Chase":               "JPM",
        },
        "💻 US Tech": {
            "Apple":                        "AAPL",
            "Microsoft":                    "MSFT",
            "Nvidia":                       "NVDA",
            "Alphabet":                     "GOOGL",
            "Amazon":                       "AMZN",
            "Meta":                         "META",
            "Tesla":                        "TSLA",
            "Broadcom":                     "AVGO",
            "AMD":                          "AMD",
            "Intel":                        "INTC",
            "Salesforce":                   "CRM",
            "Adobe":                        "ADBE",
            "Netflix":                      "NFLX",
            "Palantir":                     "PLTR",
            "Snowflake":                    "SNOW",
            "Crowdstrike":                  "CRWD",
        },
        "🏦 US Banks & Finance": {
            "JPMorgan Chase":               "JPM",
            "Bank of America":              "BAC",
            "Goldman Sachs":                "GS",
            "Morgan Stanley":               "MS",
            "Wells Fargo":                  "WFC",
            "Citigroup":                    "C",
            "Visa":                         "V",
            "Mastercard":                   "MA",
            "American Express":             "AXP",
            "PayPal":                       "PYPL",
        },
        "📈 US Indices": {
            "S&P 500":                      "^GSPC",
            "Dow Jones":                    "^DJI",
            "Nasdaq 100":                   "^NDX",
            "Russell 2000":                 "^RUT",
            "VIX (Volatility)":             "^VIX",
        },
    
        "💼 IT Services & Consulting": {
            "Accenture":                        "ACN",
            "IBM":                              "IBM",
            "Cognizant":                        "CTSH",
            "Automatic Data Processing":        "ADP",
            "Paychex":                          "PAYX",
            "Fiserv":                           "FI",
            "Global Payments":                  "GPN",
            "Gartner":                          "IT",
            "Leidos":                           "LDOS",
            "Booz Allen Hamilton":              "BAH",
            "SAIC":                             "SAIC",
            "EPAM Systems":                     "EPAM",
            "DXC Technology":                   "DXC",
            "Conduent":                         "CNDT",
            "Unisys":                           "UIS",
        },
        "🔐 Cybersecurity": {
            "Palo Alto Networks":               "PANW",
            "CrowdStrike":                      "CRWD",
            "Fortinet":                         "FTNT",
            "Zscaler":                          "ZS",
            "SentinelOne":                      "S",
            "Okta":                             "OKTA",
            "Cloudflare":                       "NET",
            "Tenable":                          "TENB",
            "Qualys":                           "QLYS",
            "Rapid7":                           "RPD",
            "Check Point Software":             "CHKP",
            "CyberArk":                         "CYBR",
        },
        "🗄️ Enterprise SaaS & Cloud": {
            "Workday":                          "WDAY",
            "Datadog":                          "DDOG",
            "MongoDB":                          "MDB",
            "Snowflake":                        "SNOW",
            "HubSpot":                          "HUBS",
            "Twilio":                           "TWLO",
            "Zendesk":                          "ZEN",
            "Veeva Systems":                    "VEEV",
            "Tyler Technologies":               "TYL",
            "Fair Isaac (FICO)":                "FICO",
            "Intuit":                           "INTU",
            "VeriSign":                         "VRSN",
            "Jack Henry":                       "JKHY",
        },
        "💾 Semiconductors & Hardware": {
            "Texas Instruments":                "TXN",
            "Micron Technology":                "MU",
            "Marvell Technology":               "MRVL",
            "ON Semiconductor":                 "ON",
            "Skyworks Solutions":               "SWKS",
            "Qorvo":                            "QRVO",
            "Lattice Semiconductor":            "LSCC",
            "Western Digital":                  "WDC",
            "Seagate Technology":               "STX",
            "NetApp":                           "NTAP",
            "Dell Technologies":                "DELL",
            "HP Inc":                           "HPQ",
            "HP Enterprise":                    "HPE",
            "Motorola Solutions":               "MSI",
            "Zebra Technologies":               "ZBRA",
        },
        "⚡ Energy & Industrials": {
            "ExxonMobil":                       "XOM",
            "Chevron":                          "CVX",
            "ConocoPhillips":                   "COP",
            "EOG Resources":                    "EOG",
            "Pioneer Natural Resources":        "PXD",
            "Schlumberger (SLB)":               "SLB",
            "Halliburton":                      "HAL",
            "Baker Hughes":                     "BKR",
            "General Electric":                 "GE",
            "Honeywell":                        "HON",
            "3M":                               "MMM",
            "Caterpillar":                      "CAT",
            "Deere & Company":                  "DE",
            "Parker Hannifin":                  "PH",
            "Emerson Electric":                 "EMR",
            "Eaton Corp":                       "ETN",
            "Illinois Tool Works":              "ITW",
            "Rockwell Automation":              "ROK",
            "Boeing":                           "BA",
            "Lockheed Martin":                  "LMT",
            "Raytheon Technologies":            "RTX",
            "Northrop Grumman":                 "NOC",
            "General Dynamics":                 "GD",
            "L3Harris":                         "LHX",
        },
        "🛍️ Consumer, Retail & Autos": {
            "Walmart":                          "WMT",
            "Amazon":                           "AMZN",
            "Costco":                           "COST",
            "Target":                           "TGT",
            "Home Depot":                       "HD",
            "Lowe's":                           "LOW",
            "TJX Companies":                    "TJX",
            "Dollar General":                   "DG",
            "Dollar Tree":                      "DLTR",
            "McDonald's":                       "MCD",
            "Starbucks":                        "SBUX",
            "Yum! Brands":                      "YUM",
            "Chipotle":                         "CMG",
            "Marriott":                         "MAR",
            "Hilton":                           "HLT",
            "Tesla":                            "TSLA",
            "Ford":                             "F",
            "General Motors":                   "GM",
            "Rivian":                           "RIVN",
            "Lucid Group":                      "LCID",
            "Uber":                             "UBER",
            "Lyft":                             "LYFT",
            "Airbnb":                           "ABNB",
            "Booking Holdings":                 "BKNG",
            "Expedia":                          "EXPE",
        },
        "🏥 Healthcare & Biotech": {
            "Johnson & Johnson":                "JNJ",
            "UnitedHealth Group":               "UNH",
            "Eli Lilly":                        "LLY",
            "AbbVie":                           "ABBV",
            "Pfizer":                           "PFE",
            "Merck":                            "MRK",
            "Abbott Laboratories":              "ABT",
            "Thermo Fisher Scientific":         "TMO",
            "Danaher":                          "DHR",
            "Intuitive Surgical":               "ISRG",
            "Medtronic":                        "MDT",
            "Stryker":                          "SYK",
            "Boston Scientific":                "BSX",
            "Becton Dickinson":                 "BDX",
            "Edwards Lifesciences":             "EW",
            "Zimmer Biomet":                    "ZBH",
            "Amgen":                            "AMGN",
            "Gilead Sciences":                  "GILD",
            "Biogen":                           "BIIB",
            "Moderna":                          "MRNA",
            "Regeneron":                        "REGN",
            "Vertex Pharma":                    "VRTX",
            "BioNTech":                         "BNTX",
            "Catalent":                         "CTLT",
        },
        "🚀 Fintech & Digital Finance": {
            "PayPal":                           "PYPL",
            "Block (Square)":                   "SQ",
            "Robinhood":                        "HOOD",
            "Coinbase":                         "COIN",
            "SoFi Technologies":                "SOFI",
            "Affirm":                           "AFRM",
            "Marqeta":                          "MQ",
            "Adyen":                            "ADYEY",
            "Toast":                            "TOST",
            "Nuvei":                            "NVEI",
            "Green Dot":                        "GDOT",
            "WEX":                              "WEX",
        },
},
    "Europe": {
        "🌍 European Blue Chips": {
            "ASML Holding":                 "ASML",
            "LVMH":                         "MC.PA",
            "Nestle":                       "NESN.SW",
            "Roche":                        "ROG.SW",
            "SAP":                          "SAP",
            "Siemens":                      "SIE.DE",
            "Novo Nordisk":                 "NVO",
            "TotalEnergies":                "TTE.PA",
            "Shell":                        "SHEL",
            "Unilever":                     "UL",
            "AstraZeneca":                  "AZN",
            "BP":                           "BP",
            "BHP Group":                    "BHP",
        },
        "📈 European Indices": {
            "FTSE 100 (UK)":                "^FTSE",
            "DAX 40 (Germany)":             "^GDAXI",
            "CAC 40 (France)":              "^FCHI",
            "Euro Stoxx 50":                "^STOXX50E",
        },
    },
    "China": {
        "🇨🇳 China Large Cap": {
            "Alibaba":                      "BABA",
            "Tencent":                      "0700.HK",
            "JD.com":                       "JD",
            "Baidu":                        "BIDU",
            "Pinduoduo":                    "PDD",
            "NIO":                          "NIO",
            "BYD":                          "BYDDY",
            "CNOOC":                        "CEO",
        },
        "📈 China Indices": {
            "Hang Seng (HK)":               "^HSI",
            "Shanghai Composite":           "000001.SS",
            "CSI 300":                      "000300.SS",
        },
    },
    "ETFs - India": {
        "📦 India ETFs": {
            "Nifty BeES":                   "NIFTYBEES.NS",
            "Bank BeES":                    "BANKBEES.NS",
            "Junior BeES (Nifty Next 50)":  "JUNIORBEES.NS",
            "Kotak Nifty ETF":              "KOTAKPSUBK.NS",
            "SBI Nifty ETF":                "SETFNIF50.NS",
            "Nippon India Gold ETF":        "GOLDBEES.NS",
            "HDFC Sensex ETF":              "HDFCSENSEX.NS",
            "Mirae Asset Nifty 50":         "MAFANG.NS",
        },
    },
    "ETFs - Global": {
        "🌍 Global ETFs": {
            "SPDR S&P 500 ETF":             "SPY",
            "Invesco QQQ (Nasdaq 100)":     "QQQ",
            "iShares MSCI World":           "URTH",
            "iShares MSCI Emerging Mkts":   "EEM",
            "iShares MSCI India":           "INDA",
            "VanEck India Growth":          "GLIN",
            "Vanguard Total World":         "VT",
            "iShares Core MSCI Europe":     "IEUR",
            "iShares MSCI China":           "MCHI",
        },
    },
    "Commodities": {
        "🪙 Commodities": {
            "Gold":                         "GC=F",
            "Silver":                       "SI=F",
            "Crude Oil (WTI)":              "CL=F",
            "Brent Crude":                  "BZ=F",
            "Natural Gas":                  "NG=F",
            "Copper":                       "HG=F",
            "Aluminium":                    "ALI=F",
            "Platinum":                     "PL=F",
            "Palladium":                    "PA=F",
            "Corn":                         "ZC=F",
            "Wheat":                        "ZW=F",
            "Soybean":                      "ZS=F",
            "Cotton":                       "CT=F",
            "Coffee":                       "KC=F",
            "Sugar":                        "SB=F",
        },
    },
    "Debt & Rates": {
        "📊 Bonds & Rates": {
            "US 10Y Treasury Yield":        "^TNX",
            "US 2Y Treasury Yield":         "^IRX",
            "US 30Y Treasury Yield":        "^TYX",
            "iShares 20Y+ Treasury ETF":    "TLT",
            "iShares 7-10Y Treasury ETF":   "IEF",
            "iShares TIPS Bond ETF":        "TIP",
            "Vanguard Total Bond Market":   "BND",
        },
    },
    "Global Indices": {
        "🌐 World Indices": {
            "Nifty 50 (India)":             "^NSEI",
            "Sensex (India)":               "^BSESN",
            "S&P 500 (USA)":                "^GSPC",
            "Dow Jones (USA)":              "^DJI",
            "Nasdaq 100 (USA)":             "^NDX",
            "FTSE 100 (UK)":                "^FTSE",
            "DAX 40 (Germany)":             "^GDAXI",
            "CAC 40 (France)":              "^FCHI",
            "Nikkei 225 (Japan)":           "^N225",
            "Hang Seng (Hong Kong)":        "^HSI",
            "Shanghai Composite (China)":   "000001.SS",
            "ASX 200 (Australia)":          "^AXJO",
            "Straits Times (Singapore)":    "^STI",
        },
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# HELP_TEXT — plain-English tooltips for every technical term shown to the user.
# Used via info_tip() / section_title_with_tip() from utils.py across all pages.
# KPI_HELP (above) handles basic price/change tiles; HELP_TEXT handles
# technical indicators, signals, badges, chart terms, and section titles.
# ──────────────────────────────────────────────────────────────────────────────
HELP_TEXT = {
    # ── Header badges ──────────────────────────────────────────────────────────
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
        ".NS = NSE India.  .BO = Bombay Stock Exchange.  No suffix = US (NYSE/Nasdaq).  "
        "^ prefix = market index (e.g. ^NSEI = Nifty 50, ^GSPC = S&P 500).  "
        "=F suffix = futures contract (e.g. GC=F = Gold futures).  "
        "Debt & Rates values are yields (%); Global Indices values are in points (Pts)."
    ),
    # ── KPI Panel ──────────────────────────────────────────────────────────────
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
        "Lower values = potentially cheaper — but fast-growing companies naturally carry higher ratios."
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
    # ── Charts tab ─────────────────────────────────────────────────────────────
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
    # ── Forecast tab ───────────────────────────────────────────────────────────
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
        "High probability the price stays within this band, but earnings or news can push it outside."
    ),
    # ── Insights tab ───────────────────────────────────────────────────────────
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
    # ── Home page ──────────────────────────────────────────────────────────────
    "market_status": (
        "Live session status based on official trading hours. "
        "OPEN = you can trade now. CLOSED = prices shown are from the last close. "
        "Times shown in the exchange\'s local timezone."
    ),
    "top_movers": (
        "Stocks with the highest % price change today. "
        "High movers often have news or events driving them — click a name to investigate."
    ),
    # ── Week Summary ───────────────────────────────────────────────────────────
    "weekly_heatmap": (
        "Weekly return for each Nifty 50 stock (% change from Monday open to now). "
        "Green = positive week. Red = negative week. Longer bar = bigger move."
    ),
    "sector_snapshot": (
        "Weekly performance of each major NSE sector index. "
        "Shows which sectors are leading (outperforming) vs lagging this week."
    ),
}

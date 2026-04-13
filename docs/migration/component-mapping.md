# GSI Dashboard — Streamlit to Next.js Component Mapping
**Researched:** 2026-04-13 | session_024
**Source:** Full code audit of app.py, pages/*.py, market_data.py

---

## Data Fetching Patterns

| Streamlit pattern | Next.js/Vercel equivalent | Notes |
|---|---|---|
| `@st.cache_data(ttl=5)` | SWR `revalidateOnFocus + dedupingInterval=5000` | Live price (5s) |
| `@st.cache_data(ttl=300)` | `unstable_cache(fn, ['key'], { revalidate: 300 })` | OHLCV (5 min) |
| `@st.cache_data(ttl=600)` | `unstable_cache(fn, ['key'], { revalidate: 600 })` | Ticker info, news |
| `@st.cache_data(ttl=86400)` | `unstable_cache(fn, ['key'], { revalidate: 86400 })` | Financials |
| `@st.fragment(run_every=5)` | `useSWR(url, { refreshInterval: 5000 })` | Live price fragment |
| `@st.fragment(run_every=60)` | `useSWR(url, { refreshInterval: 60000 })` | Global signals, top movers |
| `@st.fragment(run_every=300)` | `useSWR(url, { refreshInterval: 300000 })` | News feed |
| `st.session_state["key"]` | Zustand store + Supabase for persistence | Forecast history → Supabase |
| `st.session_state["forecast_history"]` | Supabase `forecast_history` table | **Resolves OPEN-003** |
| `cache_buster: int = 0` | Cache tag invalidation via `revalidateTag()` | Same purpose, Next.js idiom |
| `is_ticker_cache_warm()` | Redis `EXISTS ticker:*` key check | Module-level cache → Redis |
| `_ticker_cache` dict | Upstash Redis KV | Must be distributed (not module-level) |
| `_global_throttle()` | Upstash Ratelimit sliding window | Must be distributed |

---

## UI Component Mapping

### Layout & Navigation

| Streamlit component | React/Next.js equivalent | Notes |
|---|---|---|
| `app.py` routing (MPA, CSS-hidden sidebar) | `app/layout.tsx` + route groups | Clean routing, no CSS hacks |
| `st.sidebar` (CSS-hidden) | `nav` component, `position: fixed` | No iframe manipulation needed |
| `st.set_page_config(layout="wide")` | Tailwind `max-w-screen-2xl mx-auto` | |
| `st.columns([1, 2, 1])` | Tailwind `grid grid-cols-4 gap-4` | |
| `st.tabs(["Charts", "Forecast"])` | shadcn/ui Tabs component | |
| `st.expander(expanded=True)` | shadcn/ui Accordion, default open | |
| `st.container()` | div or shadcn/ui Card | |
| `st.empty()` | Conditional rendering `{data && Component}` | |

### Forms & Inputs

| Streamlit component | React/Next.js equivalent | Notes |
|---|---|---|
| `st.selectbox("Market", options)` | shadcn/ui Select | |
| `st.selectbox("Ticker", options)` | shadcn/ui Combobox (searchable) | 559 tickers needs search |
| `st.slider("Horizon", 7, 63)` | shadcn/ui Slider | Forecast horizon |
| `st.radio("Period", options)` | shadcn/ui RadioGroup | |
| `st.checkbox("Include X")` | shadcn/ui Checkbox | |
| `st.multiselect("Tickers", options)` | shadcn/ui MultiSelect | Portfolio allocator |
| `st.button("Run Analysis")` | shadcn/ui Button | |
| `st.text_input("Search")` | shadcn/ui Input + combobox | |

### Data Display

| Streamlit component | React/Next.js equivalent | Notes |
|---|---|---|
| `st.dataframe(df)` | TanStack Table + shadcn/ui Table | Sortable, filterable |
| `st.metric("ROE", "32%")` | Custom KPICard component | 3-column KPI grid |
| `st.plotly_chart(fig)` | Plotly React (react-plotly.js) | Keep Plotly for consistency |
| `st.markdown(unsafe_allow_html=True)` | HTML rendered via DOMPurify-sanitized function | RISK-001: always sanitize before render |
| `st.caption("disclaimer")` | Typography `p` with `text-xs text-muted-foreground` class | |
| `st.success("BUY")` | Badge variant="success" | |
| `st.warning("WATCH")` | Badge variant="warning" | |
| `st.error("AVOID")` | Badge variant="destructive" | |
| `st.info("Note")` | Alert component | |
| `st.progress(0.7)` | shadcn/ui Progress value={70} | |
| `st.spinner("Loading...")` | shadcn/ui Skeleton / loading states | |
| `st.image(url)` | Next.js Image component | |
| `st.link_button("WorldMonitor", url)` | Button as anchor tag | ADR-022: keeps link-only approach |

### State & Control Flow

| Streamlit pattern | React/Next.js equivalent | Notes |
|---|---|---|
| `st.rerun()` | React useState trigger / router.refresh() | |
| `st.stop()` | Early return from component | |
| `st.toast("Message")` | shadcn/ui toast() | |
| `st.session_state` initialization | Zustand store create() | |

---

## Server-Side Python API Routes

| Current function | API route | Method | Notes |
|---|---|---|---|
| `get_price_data(ticker, period, interval)` | `POST /api/market/price` | POST | Params in body |
| `get_ticker_info(ticker)` | `GET /api/market/info/[ticker]` | GET | Cached 600s |
| `get_live_price(ticker)` | `GET /api/market/live/[ticker]` | GET | Cached 5s |
| `get_batch_data(tickers, period)` | Workflow step (long-running) | — | >30s, needs Workflow DevKit |
| `get_top_movers(symbols)` | `GET /api/market/movers` | GET | Cached 300s |
| `get_news(feeds, max_n)` | `GET /api/news` | GET | Cached 600s |
| `get_intraday_chart_data(ticker)` | `GET /api/market/intraday/[ticker]` | GET | Cached 60s |
| `compute_indicators(df)` | Called server-side in market route | — | No separate route needed |
| `signal_score(df, info)` | Called server-side in market route | — | |
| `compute_unified_verdict(...)` | Called server-side in market route | — | |
| `compute_forecast(df)` | `POST /api/forecast/compute` | POST | Workflow step (2000 sims) |
| `store_forecast(...)` | Supabase insert via `/api/forecast/store` | POST | Replaces session_state |
| `optimise_mean_cvar(...)` | `POST /api/portfolio/optimize` | POST | 1024 MB Fluid Compute |
| `compute_efficient_frontier(...)` | `POST /api/portfolio/frontier` | POST | Same function, same route |
| `compute_stability_score(...)` | `POST /api/portfolio/stability` | POST | |
| `get_health_stats()` | `GET /api/health` | GET | DEV_TOKEN gated |
| `get_rate_limit_state()` | `GET /api/health/ratelimit` | GET | DEV_TOKEN gated |

---

## Fragment to SWR Polling Map

| Fragment | `run_every` | SWR `refreshInterval` | Key difference |
|---|---|---|---|
| `_render_live_price_fragment` | 5s (market hours only) | `market_open ? 5000 : undefined` | Conditional refresh |
| `_render_global_signals` | 60s | `60000` | Always active |
| `_render_top_movers` | 60s | `60000` | Always active |
| `_render_news_feed` | 300s | `300000` | Always active |
| N/A | — | Add `revalidateOnFocus: false` | Prevent rapid refetch on tab switch |

---

## Environment Variables

| Streamlit | Next.js | Scope |
|---|---|---|
| `st.secrets.DEV_TOKEN` | `process.env.DEV_TOKEN` | Server-only |
| N/A (new) | `process.env.UPSTASH_REDIS_URL` | Server-only |
| N/A (new) | `process.env.SUPABASE_URL` | Server-only |
| N/A (new) | `NEXT_PUBLIC_APP_VERSION` | Public (client) |

---

*Generated by Vercel migration research agent (Track C) + main context | 2026-04-13 | session_024*

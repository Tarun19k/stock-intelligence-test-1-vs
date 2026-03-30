# GSI Dashboard — Dependency & Compatibility Log
# ════════════════════════════════════════════════════════════════════════
# PURPOSE: Every painful compatibility issue discovered is recorded here.
# Before changing any dependency version, check this file first.
# ════════════════════════════════════════════════════════════════════════

## Current Pinned Environment (v5.32)

```
streamlit==1.55.0
yfinance==1.2.0
pandas>=1.4.0          # NOT >=3.0.0 — see CONSTRAINT-001
numpy>=2.0.0
cvxpy==1.8.2
plotly==5.24.1
feedparser==6.0.11
pytz==2024.2
requests==2.32.3
```

System deps (`packages.txt`):
```
libopenblas-dev        # Required by cvxpy on Streamlit Cloud Linux
```

Runtime: Python 3.14 (no runtime.txt — Cloud auto-selects latest)

---

## Constraint Registry

### CONSTRAINT-001 | 2026-03-28 | ACTIVE
**Package:** pandas
**Constraint:** Use `pandas>=1.4.0` — NOT `pandas>=3.0.0`
**Symptom:** `ResolutionImpossible` on `pip install` and `uv pip install` on local and Streamlit Cloud
**Root cause:** streamlit==1.55.0 package metadata declares `pandas<3` as a dependency. pip/uv correctly reject pandas>=3.0.0 as incompatible.
**Note:** The GSI codebase is actually compatible with both 2.x and 3.x. This is a metadata constraint only — streamlit's code runs fine with pandas 3.x. But package resolvers respect the declared metadata.
**Fix:** `pandas>=1.4.0` lets pip resolve to the latest 2.x version automatically.
**Verified:** v5.28 crisis resolution. ADR-011.

---

### CONSTRAINT-002 | 2026-03-28 | ACTIVE
**Package:** streamlit
**Constraint:** Pin to `streamlit==1.55.0` — do not upgrade without testing CSS selectors
**Symptom:** Sidebar collapse button disappeared after upgrading to 1.55 (v5.30 bug)
**Root cause:** Streamlit 1.55 changed the DOM structure of the sidebar collapse control. The CSS selector `[data-testid="stToolbar"]` no longer works.
**Working selectors for 1.55:**
```css
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
section[data-testid="stMain"] button[data-testid="baseButton-headerNoPadding"]
```
**Note:** `width="content"` is valid in 1.52+ — do not flag in R2 regression.
**Fix:** See styles.py sidebar collapse pill block. GSI_SKILLS.md Skill 7.
**Verified:** v5.30. CSS updated to use 1.55-compatible selectors.

---

### CONSTRAINT-003 | 2026-03-28 | ACTIVE
**Package:** yfinance
**Constraint:** Pin to `yfinance==1.2.0` — do not upgrade without re-testing MultiIndex normalisation
**Symptom:** v5.27 — MultiIndex column order changed in single-ticker downloads. `df["Close"]` returned a DataFrame instead of a Series.
**Root cause:** yfinance 1.2.0 changed MultiIndex structure for `yf.download(single_ticker)` — columns became `(field, ticker)` tuples in all cases.
**Fix:** `_normalize_df()` in market_data.py detects MultiIndex level and normalises. Pattern: `cl = df["Close"].iloc[:, 0] if isinstance(df["Close"], pd.DataFrame) else df["Close"]`
**Note:** This guard is now in every place that reads Close/Open/High/Low/Volume.
**Verified:** v5.28. GSI_SKILLS.md Skill 6.

---

### CONSTRAINT-004 | 2026-03-28 | ACTIVE
**Package:** yfinance (Indian stocks specifically)
**Constraint:** `Ticker.info["returnOnEquity"]` returns `None` for most NSE/BSE stocks
**Symptom:** ROE shows 0.0% (safe_float(None) = 0.0) for RELIANCE.NS, HDFC.NS, TCS.NS
**Root cause:** Yahoo Finance does not reliably populate fundamental metadata for Indian exchange-listed stocks via the free API.
**Coverage:** ~70–80% of Nifty 50 large caps have data via `Ticker.financials` + `Ticker.balance_sheet`. Mid/small caps: partial.
**Fix v5.31:** ROE null guard — `roe_str = f'{val:.1f}%' if val != 0 else "N/A"`. Prevents 0.0% being displayed as data.
**Future fix (OPEN — v5.33):** Self-calculate ROE from `Ticker.financials` (Net Income) + `Ticker.balance_sheet` (Stockholders Equity). TTL 24h.
**Verified:** D-02 audit finding. ADR-012 related.

---

### CONSTRAINT-005 | 2026-03-28 | ACTIVE
**Package:** yfinance + Yahoo Finance rate limiting
**Constraint:** From Streamlit Cloud's datacenter IP, Yahoo Finance enforces ~0.2–0.4 req/s
**Symptom:** 8,345-event 429 death spiral in v5.27 when rate limit gate was missing from `get_ticker_info()`
**Rate limit architecture:**
- Token bucket: `_BUCKET_MAX=5`, `_BUCKET_RATE=0.4s`
- Chunk size: 3 tickers per batch
- Inter-chunk gap: 5s
- Cold-cache delay: 2s on first call
- Rate-limit backoff: 10s on `YFRateLimitError`
- Gate: `_is_rate_limited()` must be called before every yfinance function
**Fix:** v5.29 added `_is_rate_limited()` gate to `get_ticker_info()` (was missing).
**Verified:** v5.28 crisis. GSI_SKILLS.md Skill 6.

---

### CONSTRAINT-006 | 2026-03-28 | ACTIVE
**Package:** streamlit / Python 3.14
**Constraint:** `warnings.filterwarnings("ignore", category=FutureWarning)` required
**Symptom:** Streamlit Cloud logs flooded with `FutureWarning: ChainedAssignmentError` from yfinance internals on Python 3.14
**Root cause:** pandas 3.x in Python 3.14 enables strict chained-assignment checking. yfinance 1.2.0 has internal assignments that trigger this.
**Fix:** In market_data.py: `warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")`
**Note:** This suppresses warnings from yfinance only — not from GSI code.
**Verified:** v5.28.

---

### CONSTRAINT-007 | 2026-03-28 | ACTIVE
**Package:** cvxpy
**Constraint:** Requires `libopenblas-dev` on Streamlit Cloud Linux
**Symptom:** Import error on Streamlit Cloud — `ImportError: libopenblas.so.0: cannot open shared object file`
**Fix:** Add `libopenblas-dev` to `packages.txt` in repo root.
**Note:** No impact on local macOS/Windows development — BLAS is bundled with numpy. Only affects Linux (Streamlit Cloud).
**Verified:** v5.23 portfolio allocator launch.

---

### CONSTRAINT-008 | 2026-03-28 | ACTIVE
**Package:** streamlit
**Constraint:** `st.rerun(scope='fragment')` raises `StreamlitAPIException`
**Symptom:** `StreamlitAPIException: The 'scope' parameter is not supported`
**Root cause:** `scope` parameter exists in Streamlit docs but not in deployed versions as of 1.55.
**Fix:** Use plain `st.rerun()` always. DO NOT UNDO rule 3 in CLAUDE.md.
**Verified:** Multiple sessions. GSI_SKILLS.md Skill 7.

---

### CONSTRAINT-009 | 2026-03-28 | ACTIVE
**Package:** WorldMonitor (external embed)
**Constraint:** CSP blocks *.streamlit.app from embedding worldmonitor.app via iframe
**Symptom:** Iframe renders as blank white space — no error shown to user
**Root cause:** WorldMonitor sets `frame-ancestors: 'self'` in their CSP headers, blocking all external embeds
**Fix:** Replaced iframe with an external link button + caption. G-01 finding. WONT_FIX resolution in GSI_AUDIT_TRAIL.md.
**Note:** Cannot be resolved from GSI side — requires WorldMonitor to add `*.streamlit.app` to their CSP allowlist.

---

## Upgrade Decision Framework

Before upgrading any dependency:

1. Check this file for existing constraints on that package
2. Check whether the constraint is ACTIVE or superseded
3. If upgrading streamlit: re-test all CSS selectors in styles.py
4. If upgrading yfinance: re-test `_normalize_df()` with single-ticker and multi-ticker downloads
5. If upgrading pandas: test `pandas>=X.0.0` resolves without conflict locally via `uv pip install -r requirements.txt`
6. Run full regression suite (392/392) after any upgrade
7. Deploy to Streamlit Cloud and verify cold-start completes within 30s

## Known Safe Upgrade Paths

- `plotly`: safe to upgrade — no compatibility dependencies with other packages
- `feedparser`: safe to upgrade — only used for RSS parsing, no version-sensitive code
- `pytz`: safe to upgrade — only used for timezone lookups
- `requests`: safe to upgrade — only used in `safe_url()` utility

## Known Risky Upgrades

- `streamlit`: CSS selectors break on minor versions (see CONSTRAINT-002)
- `yfinance`: MultiIndex structure changed in 1.2.0 (see CONSTRAINT-003)
- `pandas`: metadata conflict with streamlit (see CONSTRAINT-001)
- `cvxpy`: Clarabel solver backend changed APIs in 1.8.x — test portfolio optimiser after upgrade

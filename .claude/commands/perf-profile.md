# Performance Profiling — GSI Dashboard

Profile Streamlit app memory and speed against Streamlit Cloud free tier constraints.

## Constraints to test against
- RAM: 1GB total (Streamlit Cloud free tier) — target <900MB at rest
- Cold start: app sleep after 12h inactivity — target <15s first load
- Fragment auto-refresh: 60s movers, 60s global signals, 300s news, 5s live price
- Batch download: CHUNK=3 tickers, 5s inter-chunk — must not block UI thread

## Memory profiling

### Quick baseline check
```python
import tracemalloc, streamlit as st
tracemalloc.start()
# ... run app operations ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current/1e6:.1f}MB | Peak: {peak/1e6:.1f}MB")
tracemalloc.stop()
```

### Module-level cache size
```python
import sys
from market_data import _ticker_cache
cache_mb = sys.getsizeof(_ticker_cache) / 1e6
print(f"_ticker_cache: {cache_mb:.1f}MB, {len(_ticker_cache)} entries")
```

### @st.cache_data audit
Check all cached functions — are TTLs correct?
```bash
grep -n "@st.cache_data" market_data.py pages/*.py
```
Expected TTLs: live_price=5s, OHLCV=300s, ticker_info=600s, news=600s

## Speed profiling

### Cold start sequence
Time each stage: imports → session_state init → ticker_bar render → homepage fragments
Target: total cold start <15s on Streamlit Cloud (simulated by clearing cache)

### Fragment refresh timing
Each fragment should complete its fetch+render within its refresh interval.
_render_top_movers (60s): fetch must complete in <10s
_render_news_feed (300s): fetch must complete in <30s

## Common memory leaks to check

1. **_ticker_cache unbounded growth**
   Module-level cache has no eviction. After 100 tickers: ~50MB.
   After all 559 tickers: ~280MB. Acceptable.

2. **Plotly figure objects**
   Each chart keeps data in memory until garbage collected.
   Use `fig = None` after `st.plotly_chart(fig)` in loops.

3. **pandas DataFrames in session_state**
   DFs stored in `st.session_state` persist across reruns.
   Only store small summary data — not full OHLCV history.

## Pre-launch memory checklist
- [ ] App starts fresh: <400MB
- [ ] After loading 10 tickers: <600MB
- [ ] After full ticker bar warm (all groups): <800MB
- [ ] Headroom from 1GB limit: >100MB
- [ ] No obvious memory leak over 30-minute session

## When memory exceeds 900MB
1. Check _ticker_cache size first
2. Check st.session_state for large DataFrames
3. Reduce CHUNK size in _yf_batch_download
4. Increase TTL on get_batch_data to reduce re-fetches

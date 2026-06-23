# Commercial Gate Rules — AlphaVeda

## State detection — NEVER use env flag
Commercial state is derived from data, not configuration:

```python
def is_commercial() -> bool:
    result = supabase.table('waitlist').select('id') \
        .not_.is_('converted_at', None).limit(1).execute()
    return len(result.data) > 0
```

Fail-closed: if Supabase is unreachable, assume commercial=True (block yfinance).

## What changes at commercial=True
- yfinance: BLOCKED (CommercialLicenseError raised in DataProvider)
- FMP: REQUIRED (must be configured via ALPHAVEDA_FMP_KEY in .env)
- Layer 4 rupee amounts: SUPPRESSED (show direction + confidence only)
- SEBI framing: unchanged (still research-only)

## What stays the same
- SEBI disclaimer: always pinned
- Signal direction + confidence: always shown
- Data viewer: always shown
- Accuracy ledger: always shown

## Suppression is deliberate
When commercial=True, the Path page shows "BULLISH signal" not "₹72,500 position".
This is intentional SEBI compliance — not a bug. The UX must present this as a
designed state, not a degraded fallback.

## yfinance licence
yfinance data is licensed for personal use only (terms of service).
Using it for commercial subscribers violates yfinance ToS.
The CommercialLicenseError guard enforces this boundary at the DataProvider level.

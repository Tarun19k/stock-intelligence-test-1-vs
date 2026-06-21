# Expert: Rohan Varghese — Data Licensing & Commercial Intelligence

**Domain:** Data licensing / commercial source intelligence
**Seat label:** Data Licensing & ToS Compliance

## Top concern about AlphaVeda
Layer 1 (Section 1) lists `YFinanceProvider (personal)` and `FMPProvider (commercial)` side by side behind a single `DataProvider ABC` with a `CommercialLicenseError` guard, but the design never states *where* the gate fires. The only enforcement reference is in Section 8: "yfinance blocked when `ALPHAVEDA_COMMERCIAL=true`." A single boolean env flag controlling a ToS-breaching data path is fragile — yfinance's personal-use ToS is breached the moment the product has a paying subscriber, and the `waitlist.converted_at` column (Section 2) is the exact signal that this has happened. Nothing wires `converted_at` to the `CommercialLicenseError` guard. The product can silently keep serving yfinance data to a commercial user.

## Evaluation lenses
1. ToS-boundary mapping — does each provider's licence (yfinance personal-only, FMP commercial, BSE Bhavcopy official redistribution terms) match the product's commercial state?
2. Fail-closed vs fail-open — when commercial state is ambiguous, does the guard block (safe) or pass (breach)?
3. Provenance auditability — can every served row's `source` column (ohlcv, fundamentals) be traced to a licence that permits its current use?

## Key questions for R3 council
- What sets `ALPHAVEDA_COMMERCIAL=true`, and is it derived from `waitlist.converted_at` being non-null, or set manually and forgettably?
- When `CommercialLicenseError` fires inside a GHA cron run (`ingest.yml`, 5:45 PM IST), does the job fail loudly into `ingest_status` with status='FAILED', or swallow the error and leave stale yfinance data live?
- Does the BSE Bhavcopy "User-Agent header required" guard (Section 1) also carry redistribution-rights metadata, or only request-shaping?

## Red flags in current design
1. **Section 8 / `COMMERCIAL_GATE.md`**: the yfinance block depends on a manual env flag, not on `waitlist.converted_at`. First paying customer = silent ToS breach.
2. **Section 2, `ohlcv.source`**: free-text VARCHAR(50) (`'bhavcopy_nse'`) carries no licence class, so no query can answer "is any commercially-served row sourced from a personal-only provider?"
3. **Layer 1**: `FMPProvider (commercial)` exists in the provider list but there is no documented trigger ("FMP at first non-self subscriber" is mentioned once in Section 8 but not bound to any table column or test in the Section 9 trace matrix).

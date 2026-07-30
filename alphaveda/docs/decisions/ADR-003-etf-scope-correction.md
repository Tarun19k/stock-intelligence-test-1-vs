# ADR-003: ETF Scope Correction — No Parser Change Needed

**Status:** Accepted (2026-07-30)
**Related commit:** `c06f4a1`

## Context

OHY Prereq 2 (Market & Instrument Scope) initially assumed that including ETFs required a
`bhavcopy.py` parser change, based on a docstring comment stating the parser "excludes derivatives,
ETFs-on-debt, and other non-equity instruments." This assumption was not verified before being
drafted into `OFFSET_HARVEST_YIELD_FOUNDATION.md`.

## Decision

Live verification (fetching a real NSE Bhavcopy CSV and checking 5 real ETF tickers — NIFTYBEES,
GOLDBEES, BANKBEES, JUNIORBEES, LIQUIDBEES) found they already trade under `SERIES: EQ`, which
`bhavcopy.py`'s `_VALID_SERIES = {"EQ", "BE", "BL"}` already accepts. **No parser change is
required for standard ETF OHLCV ingestion.**

## Consequences

- The original assumption was corrected in the same document before being acted on, not left as a
  stale claim — matches this session's Claim Verification Gate discipline.
- Remaining real gap: an `asset_class` schema column and an ETF-specific fundamentals analog
  (NAV/expense-ratio/tracking-index) — genuinely unbuilt, tracked separately, not conflated with
  the (already-solved) OHLCV ingestion question.
- General lesson encoded: a docstring comment is not verified behavior — this ADR exists partly to
  make that correction traceable, not just fixed silently.

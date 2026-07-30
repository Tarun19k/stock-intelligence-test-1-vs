# No Hardcoding — AlphaVeda (added 2026-07-30, Tarun-mandated, standing rule)

**Nothing in AlphaVeda gets hardcoded into the codebase.** Applies to every script, migration,
and page in this workspace, not just the one incident that prompted this rule.

## The real incident behind this rule

While ingesting Tarun's real P&L data (`scripts/ingest_holdings_from_pnl.py`), a real ISIN
mismatch was found: the P&L export's Yes Bank ISIN (`INE528G01027`) didn't match BSE's live
scrip master (`INE528G01035`) — likely from the 2020 RBI-led reconstruction scheme reissuing the
ISIN. The first fix was a hardcoded dict: `_KNOWN_ISIN_MISMATCHES = {"YES BANK": "YESBANK"}`.
Flagged and removed same session, before it shipped — replaced with a generic normalized-name
fallback matcher (`_normalize_name()` + `name_index` built from the live BSE scrip master's own
`Scrip_Name`/`Issuer_Name` fields) that resolves *any* future ISIN-mismatch case the same way,
not just this one company.

## What counts as hardcoding, specifically

- A dict/list mapping specific company names, tickers, or ISINs to a fixed value in source code
  (the Yes Bank case above)
- A hardcoded threshold, rate, or date standing in for something that should come from a
  config file, a database row, or a live source (tax rates, materiality thresholds — see
  `OFFSET_HARVEST_YIELD_FOUNDATION.md`'s own G2 rule against inventing financial constants)
- A hardcoded file path, credential, or environment-specific value that should come from `.env`
  or a config source
- A hardcoded list of tickers/instruments that should instead be derived from a live query
  (e.g. AlphaVeda's `instruments` table) or a versioned config file

## What's NOT a violation

- Named constants that represent a real, versioned, cited decision (e.g. the STCG/LTCG rate
  tables in `OFFSET_HARVEST_YIELD_FOUNDATION.md` §10 — these are **content**, cited to real
  sources with effective dates, living in a document meant to be read and updated, not a magic
  number silently buried in code logic)
- Genuinely fixed schema/API contracts (column names, enum values already agreed in the OHY
  contracts) — these are interfaces, not the kind of hardcoding this rule targets
- Test fixtures and synthetic data explicitly labeled as such (`ohy_synthetic_prototype.py`'s
  `SYNTHETIC_PORTFOLIO`) — clearly fake data for testing is not the same as a silent real-world
  assumption baked into logic

## The test to apply before writing any constant/mapping into code

**Will this same line of code still be correct the next time real data changes?** The Yes Bank
case fails this test — a hardcoded dict entry only helps for that one company; the next ISIN
reissue (or any future demerger, delisting, name change) would need its own new hardcoded entry,
forever. The fix must resolve the *class* of problem, not the one instance.

## Enforcement

No mechanical hook exists for this (same honest limitation as other discipline-based rules in
this system — nothing currently greps a diff for hardcoded-mapping patterns automatically).
Verified by review: before any script/migration touching real financial data is considered done,
check it against the test above explicitly, same discipline as the Claim Verification Gate.

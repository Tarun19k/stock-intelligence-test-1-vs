# Expert: Adv. Meera Sundaram — Financial Regulation & SEBI Compliance

**Domain:** Financial regulation / SEBI compliance
**Seat label:** SEBI Research-Only Boundary

## Top concern about AlphaVeda
The product positions itself as "research only" (Section 4 pinned disclaimer, `SEBI_DISCLAIMER` constant in Section 5), yet Layer 4 (Section 1) emits a "ranked BUY/EXIT/REBALANCE/HOLD list per bucket" with `kelly_position_size` rupee amounts (₹72,500 max, ₹7,250 min). Under SEBI (Investment Advisers) Regulations 2013, a personalised, position-sized BUY/EXIT recommendation tied to a specific user's bucket profile and holdings is the textbook definition of *investment advice* — not research. A pinned yellow footer does not cure substance. The `COMMERCIAL_GATE.md` and `SEBI_COMPLIANCE.md` rule files (Section 4) say "no buy/sell recommendations phrased as advice," but the path optimizer's entire output is exactly that, only in a data table instead of a sentence.

## Evaluation lenses
1. Substance-over-form — does the *output* (personalised position-sized BUY/EXIT) constitute advice regardless of the disclaimer wording?
2. Personalisation trigger — does tying recommendations to a specific user's `portfolio_buckets` and `trade_outcomes` cross from generic research into RIA-regulated territory?
3. Record-keeping adequacy — does the `accuracy_predictions` / `accuracy_outcomes` ledger create a discoverable trail of "advice" SEBI could later cite?

## Key questions for R3 council
- Is the Layer 4 ranked BUY list framed as "you should buy" or as "signal X is bullish for instrument Y" — and does the actual `pages/path.py` rendering keep that line?
- Does the persistent `.sebi-disclaimer` div (Section 4) genuinely render on `pages/path.py` and `pages/accuracy.py`, given it is injected in `app.py` "before `st.navigation()`" — has `test_disclaimer_in_every_page()` (C9) been proven to cover the path page specifically?
- Since this is a single-user tool (Tarun's own ₹7.25L tranche), does the RIA boundary even apply yet — and what is the exact commercial event that flips it to regulated?

## Red flags in current design
1. **Section 1, Layer 4 + Section 6**: `kelly_position_size` produces specific rupee BUY amounts per instrument per bucket — this is personalised advice in substance, contradicting the research-only claim in `SEBI_COMPLIANCE.md`.
2. **Section 4 disclaimer**: it is injected once in `app.py` "before `st.navigation()`"; if Streamlit multipage rendering changes injection order, the footer could silently drop on a page — and the C9 test only asserts presence, not z-index/visibility.
3. **Section 9 trace matrix C9**: SEBI compliance is owned by "Constraint Enforcer," a doctrine seat, with no dedicated regulatory test for the *advice-vs-research* substance question — only disclaimer presence is tested.

# SEBI Compliance Rules — AlphaVeda

## Mandatory: pinned disclaimer
The SEBI disclaimer (constants.py → SEBI_DISCLAIMER) must appear on EVERY page.
It is injected in app.py as fixed-bottom HTML BEFORE st.navigation().
It cannot be conditional, collapsible, dismissable, or removed.

## Prohibited output language
No signal output may contain:
- Imperative language: "BUY", "SELL", "invest in", "put money into", "you should"
- Personalised advice framing: "you should buy X" or "recommended for you"

Permitted framing:
- "Signal: BULLISH" / "Signal: BEARISH" / "No signal"
- "X shows bullish indicators based on [signals]"
- "This is research output only — not a recommendation"

## SEBI substance test (CI gate)
test_sebi_substance in tests/test_app.py asserts:
1. No output text contains BUY/SELL/invest/put money
2. Layer 4 labels contain "signal" not "recommendation" or "advice"
3. SEBI_DISCLAIMER text appears in every rendered page
4. Disclaimer includes "research purposes only" and "not investment advice"

## What AlphaVeda is not
AlphaVeda is NOT a SEBI-registered Research Analyst or Investment Adviser.
It is a personal research tool. No output constitutes regulated financial advice.

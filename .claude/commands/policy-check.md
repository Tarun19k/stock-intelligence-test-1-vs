# Policy Check — National Investment Regulations

Reference for what is permitted, required, and prohibited when displaying stock signals
to retail investors in each of GSI's 9 covered markets.

## Quick reference: what the app can and cannot show

| Action | India | USA | EU | UK | China | Safe framing |
|---|---|---|---|---|---|---|
| Technical indicator values (RSI, MACD) | ✅ | ✅ | ✅ | ✅ | ✅ | Always OK |
| BUY/WATCH/AVOID verdict with disclaimer | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | "Signal", not "recommendation" |
| Weinstein Stage label | ✅ | ✅ | ✅ | ✅ | ✅ | Educational framing |
| Price target / expected return | ❌ | ❌ | ❌ | ❌ | ❌ | Never |
| Personalised advice | ❌ | ❌ | ❌ | ❌ | ❌ | Never without licence |
| Live signal + disclaimer in social post | ⚠️ | ✅ | ✅ | ✅ | ❌ | India: avoid live signals on social |
| Historical backtested signals | ✅ | ✅ | ✅ | ✅ | ⚠️ | With substantiation |

## India — SEBI (highest regulatory risk for GSI)
- **Safe harbour phrase:** "Signal visualisation for self-directed research"
- **Required disclosure:** "Not SEBI-registered. Not investment advice."
- **Finfluencer rule:** Social posts must not use live market data to predict trends or recommend stocks.
  → For social media, use screenshots of historical data or general methodology explanations only.
- **Algo trading (Aug 2025):** Retail algo trading now permitted under exchange-approved frameworks.
  GSI is NOT providing algo trading — it provides signal visualisation. Clearly stated.
- **Research Analyst route (future):** If SEBI-RA registered, can provide formal recommendations.
  Registration fee: ₹10,000. Ongoing compliance requirements significant.

## USA — SEC
- **Safe harbour phrase:** "Educational content for informational purposes only."
- **Required disclosure:** "Not investment advice. Consult a registered investment adviser."
- Investment adviser registration only required if providing personalised advice.
  GSI provides generic signals → no registration required currently.
- Marketing Rule (Rule 206(4)-1): No performance claims without substantiation.
  → Never display "our signals returned X%" without rigorous backtesting records.

## European Union — MiFID II
- **Safe harbour phrase:** "This is general information, not investment research or advice."
- **Required disclosure:** If content could be construed as investment research:
  "This is a marketing communication. Not prepared per legal requirements for independent research.
   Not subject to investment research dealing restrictions."
- Displaying specific stock signals for EU-listed securities enters MiFID II research territory.
  → Mitigation: explicitly label all content as "educational technical analysis overview"
  not "investment research."

## United Kingdom — FCA
- **Safe harbour phrase:** "General information only — not a financial promotion."
- **Required disclosure:** "This is not financial advice. Seek independent financial advice before investing."
- FCA COBS 4: All digital content must be "fair, clear, and not misleading."
  → No implied returns. No "beat the market" language. No selective performance display.
- Risk warnings acceptable via tooltip/pop-up in digital formats.

## China — CSRC (highest caution — approach conservatively)
- Chinese A-shares are covered but display is highest risk jurisdiction.
- **Do not** feature Chinese stock signals prominently in marketing materials.
- **Do not** translate disclaimer into Chinese without legal review (implies targeting Chinese retail).
- Programme trading rules (July 2025): GSI is read-only visualisation, not trading — not directly applicable.
- Advisory institutions require CSRC licensing — GSI must clearly not position as advisory.

## Australia, Canada, Switzerland, Commodities, ETFs
- No specific market-targeting currently — general educational disclaimer covers.
- AUS: ASIC requires "financial product advice" licence for personalised recommendations.
- Canada: Provincial securities regulators (OSC, AMF) apply similar rules to SEC.
- GSI disclaimer coverage: sufficient for educational framing in these markets.

## Disclaimer update protocol
If GSI expands to a new market: run /policy-check before shipping, update GSI_RISK_REGISTER.md
with jurisdiction-specific risks, and add jurisdiction-specific disclaimer if required.

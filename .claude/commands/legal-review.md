# Legal Review — GSI Dashboard

Multi-jurisdiction compliance check for any content, feature, or communication before shipping.

## Trigger conditions
Run this before:
- Any new feature that displays stock signals, verdicts, or price data
- Any marketing copy, social post, or public-facing text
- Adding a new data source or RSS feed
- Shipping Claude API narrative generation
- Any text that mentions specific stocks in the context of performance

## The 5-question legal checklist

### Q1 — Investment advice test
Does this content tell a user what to do with their money?
- "Buy X" / "Sell X" / "You should hold X" → STOP. Requires SEBI/SEC/FCA registration.
- "Signal shows BUY" / "Weinstein Stage 2" / "RSI above 60" → OK with disclaimer.

### Q2 — Personalisation test
Is this content tailored to a specific user's financial situation?
- Personalised → Requires investment adviser registration in all 5 jurisdictions.
- Generic educational content → OK with disclaimer.

### Q3 — Data redistribution test
Is this content derived from Yahoo Finance / yfinance data?
- Public display of yfinance data = covered by Yahoo ToS (personal/educational use only)
- Commercial redistribution (API, paid tier, white-label) → Must switch to licensed source.
- Free educational tool with disclaimer → Accepted risk (see RISK-L02).

### Q4 — Jurisdiction sweep
| Jurisdiction | Key check | Blocker? |
|---|---|---|
| India (SEBI) | SEBI disclaimer visible, no specific stock recommendation | Hard blocker |
| India (SEBI) | No 3-month-old data requirement (finfluencer rule for social posts) | Social posts only |
| USA (SEC) | "Educational only" framing, no personalisation | Blocker if personalised |
| EU (MiFID II) | Not claiming independent research, not providing specific ratings | Blocker if ratings present |
| UK (FCA) | "Fair, clear, not misleading" — no implied returns or performance claims | Blocker if misleading |
| China (CSRC) | Minimal exposure — do not display Chinese stock picks prominently in marketing | High caution |

### Q5 — Analytics / privacy test
Does this feature collect any user data?
- No login, no cookies, session-only → GDPR-exempt under Art. 6(1)(f)
- IP logging, cross-session tracking → Requires consent banner
- streamlit-analytics with JSON persistence → OK (no PII, no IP)

## Mandatory disclaimers (always check these are present)

### For any page showing BUY/WATCH/AVOID:
```
Not investment advice. Not SEBI-registered. For educational purposes only.
```

### For any AI-generated narrative:
```
This analysis is algorithmically generated. Verify independently. Not investment advice.
```

### For any export (PDF/Excel):
```
Educational purposes only. Not investment advice. Not SEBI/SEC/FCA/MiFID II registered.
Data sourced via yfinance from Yahoo Finance — subject to Yahoo Finance ToS.
```

### For all social media posts about the tool:
```
Educational tool — not investment advice — not SEBI-registered
```

## Red lines (never cross regardless of framing)
- Target prices for any stock
- Entry / exit levels
- "Our algorithm recommends"
- Performance comparison claims ("our signals beat the index")
- Implied suitability for any investor type

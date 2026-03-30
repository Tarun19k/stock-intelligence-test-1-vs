---
paths:
  - "pages/*.py"
  - "dashboard.py"
---

# Financial Safety Rules — applies to all page files

These rules are loaded automatically when editing any page file.

## Mandatory in every signal section
Every section displaying BUY/WATCH/AVOID signals, action guidance, or stock recommendations MUST include the SEBI disclaimer. The exact text is:
"For informational purposes only. Not financial advice. Consult a SEBI-registered investment advisor before making investment decisions. Past performance is not indicative of future results."

## Algorithmic labeling
Every AI-generated narrative section (What the data says / What to consider / Watch out for) MUST be preceded by: "Algorithmically generated from quantitative signals. Not a human analyst opinion."

## No false safety statements
The fallback text for "Watch Out For" when cautions list is empty MUST check RSI and MACD before claiming neutrality. Never use "No major red flags at this time." as an unconditional fallback.

## No raw Momentum score in the dashboard header
The score (X/100) must not appear in `_render_header_static()`. Verdict badge + plain-English reason only. Score lives in the KPI panel section.

## ROE null guard
Before displaying ROE: `roe_str = f'{val:.1f}%' if val != 0 else "N/A"`. `safe_float(None)` returns 0.0 — zero is a data gap, not a real ROE.

## Named stocks must show their signal
Any section naming a specific stock as watchlist/recommendation must display that stock's current BUY/WATCH/AVOID verdict alongside the name.

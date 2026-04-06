---
name: copy
description: Use when the user needs marketing copy written: social media captions, Reddit posts, Product Hunt description, newsletter, or any platform-specific text for GSI Dashboard.
---

# /copy — GSI Marketing Copywriter

## Purpose
Write platform-specific marketing copy that is on-brand, SEBI-compliant,
and optimised for each channel's audience and character limits.

## When to use
- "Write a caption for this Instagram post"
- "Draft the Reddit launch post"
- "Write the Product Hunt tagline and description"
- "Write the newsletter for this week's signals"
- "Give me 5 tweet variations for this feature"

## Required inputs (ask if not provided)
1. **Platform** — Instagram / Reddit / Twitter / Product Hunt / Newsletter / GitHub
2. **Content type** — launch post / weekly signal / educational / feature announce
3. **Key data point or hook** — e.g. "Nifty 50: 31 BUY this week" or "new Portfolio Allocator feature"
4. **Tone variant** — technical / beginner-friendly / India-first / global

## Platform specs & character limits

| Platform | Limit | Notes |
|---|---|---|
| Instagram caption | 2,200 chars | First 125 chars are above fold — hook goes here |
| Instagram hashtags | 30 max | 5–10 optimal; put at end or first comment |
| Twitter/X | 280 chars | Data point first, CTA last |
| Reddit title | 300 chars | No clickbait; descriptive is better |
| Reddit body | No limit | Use markdown; technical depth welcome |
| Product Hunt tagline | 60 chars | Benefit-led, no jargon |
| Product Hunt description | 260 chars | Features + differentiator |
| Newsletter subject | 50 chars | Open rate depends on this |

## Copy framework per content type

### Weekly signal post (Instagram / Twitter)
```
Hook:    [Data point] — e.g. "Nifty 50: 31 BUY signals this week"
Context: [1 sentence why it matters]
CTA:     [Action] — "See full breakdown →"
Disclaimer: "Educational only. Not investment advice."
Hashtags: #Nifty50 #StockSignals #TechnicalAnalysis #IndiaMarkets #GSIDashboard
```

### Launch / feature announce (Reddit)
```
Title:   Built [what] — [honest benefit, no hype]
Opener:  Personal story — why you built it
Body:    What it does (bullets) / What it doesn't do (important for SEBI)
Proof:   Screenshot or data point
CTA:     Link + invite feedback
Disclaimer: Full SEBI disclaimer at bottom
```

### Educational carousel copy (Instagram)
```
Slide 1: Bold claim / hook — "Most traders use 1 indicator. We use 3."
Slides 2-N: One concept per slide, plain English, data visual
Last slide: CTA + disclaimer
Caption: Summary + "Swipe to learn →" + hashtags
```

### Product Hunt
```
Tagline (60): "Free multi-market stock signals. No login. 9 markets."
Description (260): GSI Dashboard combines Weinstein Stage + Elder Triple Screen
into a single BUY/WATCH/AVOID verdict across 559 tickers in India, USA, Europe,
China and more. Free, open-source, no account needed.
```

## GSI voice rules (from gsi-brand.md)

**Do say:**
- "Signal: BUY" (verdict, not advice)
- "Weinstein Stage 2 suggests trend establishing"
- "Algorithmically generated — verify independently"
- "Educational tool for self-directed research"
- "Free. No login. Open source."

**Never say:**
- "You should buy X" / "Buy now"
- "Our AI recommends"
- "Real-time signals" (yfinance has 15-20 min delay)
- "Guaranteed" / "Beat the market"
- "Investment advice" / "SEBI-registered"

## SEBI finfluencer compliance (mandatory check before every output)
Read `docs/social-media-guidelines.md` before writing any copy that mentions:
- Specific stock names or tickers
- BUY / WATCH / AVOID verdicts
- Price targets or returns
- Any forward-looking statement

Required disclaimer for any post mentioning signals or stocks:
> "Educational tool only. Not investment advice. Not SEBI-registered.
> Verify independently before making any financial decision."

## Output format
For each piece of copy, deliver:
```markdown
## [Platform] — [Content type]
**Character count:** NNN / NNN limit

[COPY BLOCK]

**Hashtags (if applicable):**
#tag1 #tag2 ...

**Compliance check:** PASS / FLAG
**Flag reason (if any):** [what needs changing]
```

Always deliver 2–3 variations so the user can pick or mix.

## Hashtag sets for GSI

### India-focused
`#Nifty50 #NSE #IndiaStocks #TechnicalAnalysis #StockMarket #WeinsteenMethod #IndiaInvestments #Zerodha #NiftySignals`

### Global
`#StockMarket #TradingView #TechnicalAnalysis #ElderRay #GlobalMarkets #FreeTools #OpenSource #RetailInvestor`

### Educational
`#LearnToTrade #WeinsteenStage #ElderTripleScreen #SignalAnalysis #MarketEducation #FinanceStudent`

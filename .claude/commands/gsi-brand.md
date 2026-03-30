# GSI Brand Guidelines

Visual identity and tone-of-voice standards for the Global Stock Intelligence Dashboard.

## Brand personality
- **Precise** — every number is sourced, every signal is explained
- **Transparent** — open source, methodology visible, limitations stated
- **Accessible** — institutional-grade analysis, retail-friendly language
- NOT: gamified, hyped, AI-buzzwordy, flashy

## Colour palette
| Role | Hex | Usage |
|---|---|---|
| Background primary | `#0d1b2a` | App dark background, landing page hero |
| Background secondary | `#1a2332` | Cards, sidebar |
| Border / divider | `#2d3a5e` | Card borders, separators |
| Accent blue | `#4fc3f7` | Signal highlights, active states, links |
| Text primary | `#e8eaf0` | Main body text |
| Text secondary | `#7eb3ff` | Labels, captions, metadata |
| BUY signal | `#00c853` | Positive verdict |
| WATCH signal | `#ffd600` | Neutral verdict |
| AVOID signal | `#ff1744` | Negative verdict |

## Typography
| Context | Font | Fallback |
|---|---|---|
| Ticker symbols, numbers | JetBrains Mono | IBM Plex Mono, monospace |
| Dashboard UI | Inter | system-ui, sans-serif |
| Marketing / landing page body | DM Sans | Inter, sans-serif |
| Code / technical docs | JetBrains Mono | Courier New |

Avoid: Arial (too generic), Inter everywhere (overused in fintech), Comic Sans, decorative fonts.

## Logo / mark
- Primary: `📈 GSI` in JetBrains Mono — acceptable for MVP
- Future: Custom mark — upward signal path through a globe wireframe
- Favicon: simple upward-trending line, electric blue on navy, 32×32

## Voice and tone
**Do say:**
- "Signal: BUY" (verdict, not advice)
- "Weinstein Stage 2 suggests trend is establishing"
- "Algorithmically generated — verify independently"
- "Educational tool for self-directed research"

**Never say:**
- "You should buy X"
- "Our AI recommends"
- "Guaranteed returns"
- "Real-time signals" (yfinance has delay)
- "Beat the market"

## Open Graph / social image spec
- Size: 1200 × 630px
- Background: `#0d1b2a`
- Headline: "Global Stock Intelligence Dashboard" in DM Sans Bold, `#e8eaf0`
- Subline: "9 Markets · 559 Tickers · Free" in JetBrains Mono, `#4fc3f7`
- Visual: screenshot of dashboard or signal panel, right-aligned

## Tone across platforms
| Platform | Tone | Example |
|---|---|---|
| Reddit | Technical, humble, inviting feedback | "Built this to solve my own TradingView frustration" |
| Product Hunt | Crisp, benefit-led, no jargon | "Free multi-market signals. No login." |
| GitHub | Developer-direct, architecture-focused | "14-module Streamlit app with Weinstein + Elder" |
| Twitter/X | Punchy, data point led | "Nifty 50: 31 BUY / 12 WATCH / 7 AVOID today" |

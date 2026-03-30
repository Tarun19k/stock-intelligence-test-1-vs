# Frontend Design — Landing Page & Marketing Assets

Build the GSI Dashboard public landing page and marketing assets.

## Design direction for GSI
- Tone: Precise, data-driven, professional — not playful or gamified
- Palette: Dark navy (#0d1b2a) base, electric blue (#4fc3f7) accent, white text
  (mirrors app's dark theme — consistent brand experience)
- Typography: JetBrains Mono or IBM Plex Mono for data/numbers; Inter for body
- Avoid: Generic stock photo charts, green/red clichés, "AI-powered" buzzwords

## Landing page must-haves
1. **Hero**: One-line value prop + live app embed or screenshot
2. **What it does**: 3 signal types (Weinstein, Elder, Unified verdict) in plain English
3. **Markets covered**: 9 markets, 559 tickers — visual map or flag grid
4. **Disclaimer**: "Educational tool. Not investment advice. Not SEBI-registered."
5. **CTA**: "Open Dashboard →" (links to Streamlit app)
6. **No signup wall** — free, instant access

## Hosting options (free)
- GitHub Pages (simplest — deploy from /docs folder or gh-pages branch)
- Vercel (free tier, custom domain support)

## Assets to build
- `index.html` — landing page
- `og-image.png` — 1200×630 Open Graph image for social sharing
- `favicon.ico` — chart/signal icon

## Key messaging (from GSI_MARKETING.md positioning)
- "Multi-market signal dashboard. Free. No login."
- "Weinstein Stage + Elder Triple Screen — two methods, one verdict."
- "India · USA · Europe · China · Commodities — one dashboard."
- NOT: "AI-powered investment advice" — regulatory red line

## Performance constraint
Landing page must load in <2s. No heavy JS frameworks. Plain HTML + CSS or minimal JS.
Static assets only — no backend calls from landing page.

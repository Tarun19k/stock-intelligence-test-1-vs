# Pitch Deck — GSI Dashboard

Create presentations for product launch, investor conversations, and community education.

## Deck types for GSI

### Product Hunt / Community Launch Deck
Audience: Retail investors, traders, developers
Slides: Problem → Solution → Markets Covered → Signal Engine → Free vs Competitors → CTA

### Investor / Accelerator Deck
Audience: Angel investors, accelerators, fintech VCs
Slides: Problem → Market Size → Solution → Traction → Tech → Monetisation Path → Team → Ask

### Educational Deck (Weinstein + Elder explainer)
Audience: Finance students, Reddit community
Slides: What is Weinstein Stage? → 4 stages visualised → Elder Triple Screen → How GSI combines them → Try it

## Design direction
- Dark navy (#0d1b2a) background — matches app theme
- Electric blue (#4fc3f7) for data/signal highlights
- JetBrains Mono for ticker symbols and numbers
- Inter or DM Sans for body text
- Never: white slides, generic stock photos, green/red traffic lights

## Creating with PptxGenJS
```bash
npm install pptxgenjs
```
```javascript
const pptx = require('pptxgenjs');
let pres = new pptx();
let slide = pres.addSlide();
slide.addText("GSI Dashboard", { x:0.5, y:0.5, fontSize:36, color:'4fc3f7' });
pres.writeFile({ fileName: "GSI_pitch.pptx" });
```

## Quality checks (from PPTX skill)
- Convert slides to images and inspect for: text overflow, element overlap, contrast issues
- "Assume there are problems. Your job is to find them."
- Complete at least one fix-and-verify cycle before sharing
- Every slide needs a visual element — text-only slides are forgettable

## Legal slide (required in all decks)
Must include: "Educational tool only — not investment advice — not SEBI/SEC/FCA registered —
data from Yahoo Finance via yfinance — verify independently."

## Colour palette reference (from 10 PPTX themes)
For GSI, use "Midnight Galaxy" base: deep navy + electric blue + white.
Accent with "Tech Innovation" highlights for signal/data slides.

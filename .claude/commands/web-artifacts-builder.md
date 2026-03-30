# Web Artifacts Builder — GSI Dashboard

Build self-contained interactive HTML widgets and embeds for the landing page and marketing.

## GSI use cases
1. **Signal heatmap widget** — embeddable group-level BUY/WATCH/AVOID heatmap (no Streamlit)
2. **Weinstein Stage explainer** — interactive 4-stage cycle visualiser for landing page
3. **Live demo embed** — pre-rendered snapshot of dashboard for Product Hunt GIF source
4. **Portfolio frontier chart** — efficient frontier visualisation for marketing materials

## Stack
React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
40+ pre-built components. Single-file bundle output.

## Setup
```bash
# From the skill's init script (adapts to GSI project context)
npx @anthropic-ai/web-artifacts-builder init gsi-widgets
cd gsi-widgets
npm install
```

## Build + bundle
```bash
npm run bundle  # outputs bundle.html — single self-contained file
```
Open `bundle.html` directly in browser — no server needed.

## Design guardrails for GSI widgets
- Match app colour palette: `#0d1b2a` background, `#4fc3f7` accent
- Use JetBrains Mono for ticker symbols and numbers
- No external API calls from widgets — use static/demo data only
- Widgets must be <500KB bundled
- Avoid: centered layouts, purple gradients, Inter font everywhere, uniform rounded corners

## Landing page integration
Embed `bundle.html` in GitHub Pages site as an `<iframe>` or inline the bundle directly.
```html
<iframe src="signal-heatmap.html" width="100%" height="400" frameborder="0"></iframe>
```
For GitHub Pages (static), inline the bundle content directly into `index.html`.

## shadcn/ui components most useful for GSI
- `Table` — ticker/signal grid
- `Badge` — BUY/WATCH/AVOID verdict pills
- `Card` — market status panels
- `Tooltip` — HELP_TEXT style explanations
- `Progress` — momentum score bar
- `Chart` — Recharts-based sparklines

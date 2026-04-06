---
name: marketing
description: Use when the user wants to run a marketing campaign, plan content across channels, or produce a complete set of marketing deliverables (assets + copy + calendar) for GSI Dashboard.
---

# /marketing — GSI Marketing Orchestrator

## Purpose
Intake a marketing brief and coordinate the full marketing team:
research → strategy → creative + copy (parallel) → compliance gate.
Produces a complete, SEBI-compliant deliverable package.

## When to use
- "Plan the launch campaign for vX.XX"
- "Create Instagram content for this week"
- "What should we post on Product Hunt / Reddit / Twitter?"
- "Give me a full marketing plan for [goal]"
- "Run a campaign for [feature / launch / milestone]"

## Inputs (ask the user if not provided)
1. **Brief** — what is the goal? (launch, feature announce, community growth, education)
2. **Channels** — which platforms? (Instagram, Reddit, Twitter/X, Product Hunt, GitHub, all)
3. **Timeline** — when does this go out? (this week, next month, ongoing)
4. **Tone** — any special angle? (technical, beginner-friendly, India-first, global)

## Agent team & dispatch order

### Phase 1 — Parallel (no dependencies)
Dispatch simultaneously:
- **research-agent** → invoke `/market-position` skill for competitive context
- **strategy-agent** → invoke `/content-calendar` skill for channel plan + posting schedule

### Phase 2 — Parallel (after Phase 1 complete)
Feed Phase 1 outputs into:
- **creative-agent** → invoke `/canvas-design` skill for visual assets (PNGs)
  - Also invoke `/pitch-deck` if a deck is needed
- **copy-agent** → invoke `/copy` skill for captions, post copy, hashtags

### Phase 3 — Sequential (must be last)
- **compliance-agent** → read `docs/social-media-guidelines.md` + `GSI_MARKETING.md` legal guardrails
  - Flag any output that violates SEBI finfluencer rules
  - Replace prohibited phrases before delivering

## Shared context (load before any agent dispatch)
- `GSI_MARKETING.md` — positioning, personas, legal guardrails, channel strategy
- `.claude/commands/gsi-brand.md` — colour palette, typography, tone of voice
- `docs/social-media-guidelines.md` — SEBI/finfluencer compliance rules

## Output package structure
```
marketing/
├── strategy/
│   ├── brief_summary.md        — campaign goal + channel plan
│   └── content_calendar.md     — posting schedule with dates
├── creative/
│   ├── [platform]_[type].png   — all visual assets
│   └── build_[campaign].py     — generator script for reproducibility
├── copy/
│   ├── captions.md             — per-post copy + hashtags
│   └── reddit_post.md          — long-form community post if applicable
└── compliance/
    └── review.md               — flagged items + approved / modified copy
```

## GSI-specific constraints
- NEVER say: "investment advice", "real-time signals", "buy X", "guaranteed", "AI recommends"
- ALWAYS include: "Educational tool", "Not SEBI-registered", "Verify independently"
- Data attribution: "Data via Yahoo Finance (yfinance) — 15-20 min delay"
- Every visual must pass the brand check: `#0d1b2a` background, `#4fc3f7` accent, JetBrains Mono for numbers
- Compliance review is non-negotiable — no output ships without it

## Quality gate (before delivering to user)
- [ ] Every visual is 1080×1080px (carousel) or correct spec for platform
- [ ] Every caption is under platform character limit (Instagram: 2200, Twitter: 280)
- [ ] Compliance agent has reviewed all copy
- [ ] At least one visual element per post (no text-only posts)
- [ ] SEBI disclaimer present wherever signals or stock names appear

## Tone by platform (from GSI_MARKETING.md)
| Platform | Tone | Hook style |
|---|---|---|
| Reddit | Humble, technical, inviting feedback | "Built this to solve my own problem" |
| Product Hunt | Crisp, benefit-led | "Free. No login. 9 markets." |
| Instagram | Visual-first, data point as headline | "31 BUY signals in Nifty 50 today" |
| Twitter/X | Punchy, one data point | "Nifty 50: 31 BUY / 12 WATCH / 7 AVOID" |
| GitHub | Developer-direct | "14-module Streamlit app, open source" |

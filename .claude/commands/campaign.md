---
name: campaign
description: Use when the user wants to run a complete end-to-end marketing campaign for a specific launch, feature, or milestone — from brief through assets, copy, calendar, and compliance in one coordinated execution.
---

# /campaign — GSI End-to-End Campaign Runner

## Purpose
One command to go from brief → complete campaign package.
Coordinates all specialist skills in the right order, parallelising where possible.

## When to use
- "Run the Product Hunt launch campaign"
- "Create everything needed for the v5.36 launch"
- "I want to launch on Reddit + Instagram this week — set it all up"
- "Full campaign for [feature/milestone]"

Difference from `/marketing`: `/campaign` is execution-focused (produces files and copy now).
`/marketing` is planning-focused (strategy + structure first). Use `/campaign` when you're ready to ship.

## Required brief (collect before starting)

```
Campaign name:     [e.g. "v5.35 Community Launch"]
Goal:              [awareness | feature launch | community growth | education]
Channels:          [Instagram | Reddit | Twitter | Product Hunt | all]
Launch date:       [YYYY-MM-DD]
Hero data point:   [e.g. "Nifty 50: 31 BUY signals" or "556 tickers, free"]
Tone:              [technical | beginner | India-first | global]
Special angle:     [anything unique about this campaign]
```

## Execution sequence

### Step 1 — Load shared context (always)
Read in parallel:
- `GSI_MARKETING.md` — personas, channel strategy, legal guardrails
- `.claude/commands/gsi-brand.md` — palette, typography, voice
- `docs/social-media-guidelines.md` — SEBI compliance rules

### Step 2 — Strategy (invoke /content-calendar)
Produce:
- Channel plan (which platforms, which content types)
- Posting schedule with exact dates
- Asset list (what PNGs need to be built)

### Step 3 — Parallel execution
Run simultaneously:

**Creative track** (invoke /canvas-design):
- Static posts at correct platform specs
- Carousel slide PNGs (1080×1080 each)
- OG image (1200×630) if needed
- Output: `marketing/creative/`

**Copy track** (invoke /copy):
- Caption for each visual asset
- Platform-native variations (IG / Twitter / Reddit / PH)
- Hashtag sets
- Output: `marketing/copy/`

### Step 4 — Compliance gate (mandatory, sequential)
Read `docs/social-media-guidelines.md`.
For every piece of copy and every visual text overlay:
- [ ] No prohibited phrases (investment advice, real-time, guaranteed, buy X)
- [ ] SEBI disclaimer present where signals/stocks are mentioned
- [ ] Data attribution present ("Data via Yahoo Finance — 15–20 min delay")
- [ ] No implied returns or performance claims

Flag and rewrite any violations before Step 5.

### Step 5 — Package and deliver
```
marketing/
├── campaign_brief.md          — approved brief + channel plan
├── content_calendar.md        — full schedule with status column
├── creative/
│   ├── [platform]_[type].png  — all assets, named by platform + content type
│   └── build_campaign.py      — reproducible generator script
├── copy/
│   ├── captions.md            — all captions, platform-labelled
│   └── reddit_post.md         — long-form if applicable
└── compliance/
    └── review.md              — what was flagged + what was changed
```

## Campaign templates by type

### Product Hunt launch
Assets: PH thumbnail (240×240) + hero (1270×760) + 3–5 screenshots
Copy: Tagline (60 chars) + Description (260 chars) + First comment (maker note)
Calendar: Post Friday 12:01am PT; Reddit same day; Instagram teaser 3 days before

### Weekly signal post (recurring)
Assets: 1 static 1080×1080 with market name + BUY/WATCH/AVOID counts
Copy: Hook line + 1 context sentence + CTA + disclaimer + hashtags
Calendar: Monday 9am IST every week

### Educational carousel
Assets: 5–8 slides at 1080×1080 (title + content + CTA slide)
Copy: Caption summary + "Swipe to learn →" + hashtags
Calendar: Wednesday — mid-week engagement peak

### Feature spotlight
Assets: 2 slides — feature name + what it does
Copy: Lead with the user benefit, not the technical name
Calendar: Friday — end-of-week, pre-weekend browsing

## Quality gates (check before declaring campaign COMPLETE)
- [ ] Every asset is at correct pixel spec for its platform
- [ ] Every caption is under character limit
- [ ] Compliance review is PASS (no flags open)
- [ ] Content calendar has exact dates, not "next week"
- [ ] Generator script runs cleanly (reproducible)
- [ ] At least one asset has been visually QA'd (Playwright screenshot or manual check)

## Figma integration (if authenticated)
If `mcp__plugin_figma_figma__authenticate` has been completed:
- Export frames directly from Figma at correct specs
- Push programmatic PNGs back to Figma for designer review
Invoke only if user has connected Figma this session.

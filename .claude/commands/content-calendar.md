---
name: content-calendar
description: Use when the user wants a content posting schedule, weekly/monthly social media plan, or channel-by-channel publishing calendar for GSI Dashboard.
---

# /content-calendar — GSI Content Calendar

## Purpose
Build a structured, realistic content posting schedule across all active channels.
Maps content types to platforms, cadence, and responsible assets needed.

## When to use
- "Plan next month's content"
- "What should we post this week?"
- "Give me a 4-week content calendar"
- "How often should we post on each platform?"

## Recommended posting cadence

| Platform | Frequency | Best time (IST) | Content type |
|---|---|---|---|
| Instagram | 3×/week | Mon/Wed/Fri 9am | Carousel (edu) + Static (signal) |
| Twitter/X | Daily | 8am + 6pm | Signal snapshot + repost |
| Reddit | 1×/week | Mon 9am | Long-form post, r/IndiaInvestments first |
| Product Hunt | One-time launch | Friday 12:01am PT | Full launch package |
| GitHub | On release | On commit | CHANGELOG post |
| Newsletter | 1×/week | Sunday 8pm | Week in markets summary |

## Content pillars (rotate across the week)

| Pillar | Frequency | Example |
|---|---|---|
| **Signal snapshot** | 2×/week | "Nifty 50: 31 BUY / 12 WATCH / 7 AVOID" |
| **Education** | 2×/week | "What is Weinstein Stage 2?" carousel |
| **Behind the build** | 1×/week | "Why we built GSI — the TradingView frustration" |
| **Market breadth** | 1×/week | "India vs USA vs Europe signals this week" |
| **Feature spotlight** | 1×2 weeks | "Portfolio Allocator — what it does" |
| **Community** | Ad-hoc | Respond to comments, repost user questions |

## 4-week rolling template

### Week 1 — Launch / Awareness
| Day | Platform | Pillar | Asset needed |
|---|---|---|---|
| Mon | Instagram + Twitter | Signal snapshot | Static 1080×1080 |
| Mon | Reddit | Behind the build | Long-form copy |
| Wed | Instagram | Education | Carousel (Weinstein 4 stages) |
| Wed | Twitter | Signal snapshot | Text only |
| Fri | Instagram | Feature spotlight | Static + caption |
| Fri | Twitter | Market breadth | Text + data table |
| Sun | Newsletter | Week summary | Email copy |

### Week 2 — Education push
| Day | Platform | Pillar | Asset needed |
|---|---|---|---|
| Mon | Instagram + Twitter | Signal snapshot | Static |
| Tue | Reddit | Technical post (r/algotrading) | Long-form copy |
| Wed | Instagram | Education | Carousel (Elder Triple Screen) |
| Thu | Twitter | Education | Thread (5 tweets) |
| Fri | Instagram | Market breadth | Carousel (9 markets heatmap) |
| Sun | Newsletter | Week summary | Email copy |

### Week 3 — Community / Social proof
| Day | Platform | Pillar | Asset needed |
|---|---|---|---|
| Mon | Instagram + Twitter | Signal snapshot | Static |
| Wed | Reddit | r/stocks launch post | Long-form copy |
| Wed | Instagram | Behind the build | Static + story |
| Fri | Instagram | Feature spotlight | Carousel (Portfolio Allocator) |
| Sun | Newsletter | Week summary | Email copy |

### Week 4 — Product Hunt launch week
| Day | Platform | Pillar | Asset needed |
|---|---|---|---|
| Mon | Instagram | Teaser | Static "Something's coming" |
| Mon | Twitter | Teaser thread | Text |
| Wed | Instagram | Education | Carousel (signal engine) |
| Thu | All | Pre-launch reminder | Cross-post |
| Fri 12:01am PT | Product Hunt | Full launch | All PH assets |
| Fri | Reddit | Launch post | r/IndiaInvestments + r/stocks |
| Fri | Twitter | Launch day | Live updates |
| Sun | Newsletter | Launch recap | Email copy |

## Asset checklist per piece

For each calendar entry, the following must be ready before posting:

- [ ] Visual asset (PNG at correct spec)
- [ ] Caption copy (compliance-checked)
- [ ] Hashtags selected
- [ ] SEBI disclaimer present (if signals/stocks mentioned)
- [ ] Link verified (Streamlit app live, not sleeping)

## Output format

Deliver as a markdown table with columns:
`Date | Platform | Pillar | Caption hook | Asset file | Status`

Status values: `PLANNED` | `ASSETS READY` | `COPY READY` | `APPROVED` | `POSTED`

## Integration with /marketing workflow
This skill is called by `/marketing` as the strategy-agent.
Feed the calendar output into `/copy` (for caption generation) and
`/canvas-design` (for asset generation) with the specific dates and content types.

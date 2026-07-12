# AlphaVeda — Text and Infographic Design Overview

**Purpose:** Provide a detailed, text-first design blueprint for AlphaVeda so product designers, developers, Claude, Codex, and stakeholders can understand the intended user experience without needing screenshots or visual mockups.

**Audience:** Product leadership, product managers, UX/UI designers, frontend engineers, backend engineers, compliance reviewers, and AI agents collaborating on AlphaVeda.

**Product framing:** AlphaVeda is an Indian equity research tool. It presents market data, algorithmic research signals, position-sizing context, and model accuracy evidence in a compliance-safe format. It is research-only and must not be framed as investment advice.

---

## 1. High-Level Product Concept

AlphaVeda is designed around one central promise:

> **Show fewer, clearer, better-explained stock research signals — and publicly grade whether those signals were right.**

The application should feel calm, analytical, transparent, and restrained. It should not feel like a trading terminal, stock-tip feed, or recommendation engine. The design should repeatedly communicate three ideas:

1. **Research, not advice** — AlphaVeda provides analysis and signals, not personalized recommendations.
2. **Evidence before confidence** — signals, confidence scores, and position-sizing context should be tied to observable data and historical grading.
3. **Trust through restraint** — the product should be comfortable saying “no call,” “not enough data,” or “too early to judge.”

---

## 2. Application Map

```text
AlphaVeda
│
├── Global Shell
│   ├── Top/side navigation
│   ├── Language mode: Simple / Pro
│   ├── Tap-to-learn glossary affordances
│   └── Fixed SEBI disclaimer on every page
│
├── 1. Market Data
│   ├── Instrument coverage
│   ├── Latest OHLCV data
│   ├── Circuit flags
│   ├── Data freshness / ingest status
│   └── Empty or stale data states
│
├── 2. Signals
│   ├── Latest research signal per instrument
│   ├── Direction: positive / negative / no call
│   ├── Confidence or cold-start state
│   ├── Segment and regime context
│   └── Research-only explanatory copy
│
├── 3. Path
│   ├── Position-sizing research view
│   ├── Direction and confidence context
│   ├── Kelly-style sizing band or suppressed amount
│   ├── Downside and exit-rule context
│   └── Commercial/personal-context guardrails
│
└── 4. Accuracy
    ├── Historical grading of emitted signals
    ├── Hit-rate / scorecard by segment
    ├── Observation counts and cold-start thresholds
    ├── Weight-review queue
    └── Past-performance disclaimers
```

---

## 3. Navigation and Global UX Structure

### 3.1 Primary Navigation

The navigation should be simple and persistent. AlphaVeda has four primary destinations:

```text
┌──────────────────────────────────────────────────────────────┐
│ AlphaVeda                         Simple | Pro      Glossary │
├──────────────────────────────────────────────────────────────┤
│ Market Data | Signals | Path | Accuracy                     │
└──────────────────────────────────────────────────────────────┘
```

**Navigation intent:**

| Navigation Item | User Question Answered | Primary User Mode |
|---|---|---|
| Market Data | “What raw data is AlphaVeda seeing?” | Inspect / verify |
| Signals | “What does AlphaVeda currently think?” | Research / compare |
| Path | “If this signal matters, how might sizing be framed?” | Risk context |
| Accuracy | “Has AlphaVeda been right before?” | Trust evaluation |

### 3.2 Global Components

Every page should include:

1. **Product identity** — AlphaVeda name and research-only tone.
2. **Navigation** — clear access to all four core routes.
3. **Language mode toggle** — Simple for plain-language explanations, Pro for finance-native labels.
4. **Glossary interactions** — tap/click explanations for terms like “confidence,” “cold start,” “market regime,” and “Kelly.”
5. **SEBI disclaimer** — fixed or always-visible regulatory disclaimer.

### 3.3 Suggested Information Hierarchy

Each page should follow a consistent hierarchy:

```text
Page Title
Short plain-language explanation
Primary controls / filters
Main content panel
Secondary context / explanatory notes
Risk, compliance, or data-quality annotation
```

This structure helps users quickly understand what the page is for, what they can interact with, and how much trust to place in the content.

---

## 4. End-to-End User Flow

AlphaVeda’s ideal user journey is not “pick stock → buy stock.” It is:

```text
1. Verify the data
   ↓
2. Review the current signal
   ↓
3. Understand confidence and uncertainty
   ↓
4. Inspect possible sizing/risk context
   ↓
5. Check historical accuracy
   ↓
6. Make an independent decision outside AlphaVeda
```

### 4.1 Primary Research Flow

```text
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Market Data   │ ──▶ │ Signals       │ ──▶ │ Path          │
│ Verify input  │     │ Review output │     │ Risk context  │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────▼─────────────────────┘
                              │
                       ┌──────▼──────┐
                       │ Accuracy    │
                       │ Trust check │
                       └─────────────┘
```

### 4.2 Trust-Building Flow

```text
Signal emitted
   ↓
Prediction recorded
   ↓
Outcome matures after defined horizon
   ↓
Prediction is graded
   ↓
Accuracy ledger updates
   ↓
Confidence and weight-review logic become more credible over time
```

### 4.3 Cold-Start Flow

```text
New instrument / segment
   ↓
Insufficient observations
   ↓
Display: “Too early” / “Not enough graded results yet”
   ↓
Avoid overconfident score presentation
   ↓
Graduate to fuller confidence display after threshold is met
```

---

## 5. Page Blueprint: Market Data

### 5.1 Purpose

The Market Data page shows the raw market information AlphaVeda uses as input. Its job is to build confidence that the data pipeline is alive, current, and transparent.

### 5.2 User Questions

- Which instruments are being tracked?
- What is the latest price, volume, and trading date?
- Is the data fresh or stale?
- Were any securities circuit-locked?
- Is AlphaVeda missing data for this instrument?

### 5.3 Suggested Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Market Data                                                  │
│ Latest end-of-day prices from NSE/BSE sources.               │
├──────────────────────────────────────────────────────────────┤
│ Data freshness banner                                        │
│ Example: “Data last updated 1 day ago. Next ingest after      │
│ market close.”                                               │
├──────────────────────────────────────────────────────────────┤
│ Filters                                                      │
│ [Instrument search] [Segment/Class filter] [Flag filter]     │
├──────────────────────────────────────────────────────────────┤
│ Summary Cards                                                │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐      │
│ │Tracked   │ │Latest    │ │Rows      │ │Circuit flags │      │
│ │stocks    │ │date      │ │loaded    │ │today         │      │
│ └──────────┘ └──────────┘ └──────────┘ └──────────────┘      │
├──────────────────────────────────────────────────────────────┤
│ OHLCV Table                                                  │
│ Ticker | Class | Date | Open | High | Low | Close | Volume   │
│ Flag   | Freshness                                           │
├──────────────────────────────────────────────────────────────┤
│ Empty / stale / error state explanation                      │
└──────────────────────────────────────────────────────────────┘
```

### 5.4 Data Presented

| Data Type | Presentation | Design Intent |
|---|---|---|
| Instrument ticker | Table cell, mono font | Fast scanning |
| Classification | Tag or plain-language label | Explain business type |
| OHLCV | Numeric table | Transparent raw inputs |
| Circuit flag | Pill/badge | Warn about distorted price action |
| Ingest status | Banner and summary card | Show freshness and operational state |
| Missing data | Empty state row | Avoid silent failure |

### 5.5 UX Notes

- Stale data should never be hidden. If data is stale, the page should visibly say so.
- Missing rows should not look like normal rows.
- Circuit flags should use a distinct badge because circuit-locked prices may not represent normal market discovery.
- This page should feel like the “audit trail” for the product’s inputs.

---

## 6. Page Blueprint: Signals

### 6.1 Purpose

The Signals page is the core research surface. It shows AlphaVeda’s latest algorithmic view of an instrument while avoiding advice-like language.

### 6.2 User Questions

- Does AlphaVeda currently have a signal for this stock?
- Is the signal leaning positive, negative, or silent?
- How confident is the system?
- Is the confidence mature or still cold-start?
- What context affects the signal?

### 6.3 Suggested Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Signals                                                      │
│ Research signals with confidence context. Not advice.        │
├──────────────────────────────────────────────────────────────┤
│ Optional banners                                             │
│ - Cold-start: “Just getting started — not enough graded       │
│   results yet.”                                              │
│ - Weight review: “Some signal weights are pending review.”   │
├──────────────────────────────────────────────────────────────┤
│ Controls                                                     │
│ [Instrument selector] [Segment selector] [Simple/Pro mode]   │
├──────────────────────────────────────────────────────────────┤
│ Main Signal Card                                             │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ TICKER / Company or instrument name                     │ │
│ │                                                          │ │
│ │ Signal: LOOKS POSITIVE / LEANS UP                       │ │
│ │ Confidence: ███████░░░ 68%                              │ │
│ │ Context: fast-growing company · market rising           │ │
│ │ Status: mature / cold-start / no opinion today          │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ Explanation Panel                                            │
│ “This signal is algorithmically generated from market data    │
│ and historical grading. It is research-only.”                │
├──────────────────────────────────────────────────────────────┤
│ Related links                                                │
│ [View raw data] [View path] [Check accuracy history]         │
└──────────────────────────────────────────────────────────────┘
```

### 6.4 Data Presented

| Data Type | Presentation | Design Intent |
|---|---|---|
| Direction | Large chip or badge | Immediate signal recognition |
| Confidence | Progress bar and percent, when mature | Scannable strength indicator |
| Cold-start status | Info banner and status label | Prevent false certainty |
| Segment/class | Tag with glossary | Explain why context matters |
| Market regime | Tag or short text | Show macro context |
| No-call state | Neutral card | Reinforce restraint |

### 6.5 No-Call State

A no-call state should look intentional and trustworthy:

```text
┌──────────────────────────────────────────────────────────────┐
│ NO OPINION TODAY                                             │
│ AlphaVeda does not see enough evidence for a useful research  │
│ signal on this instrument right now.                         │
│                                                              │
│ This is not an error. A tool that always has an opinion is    │
│ easier to misuse.                                            │
└──────────────────────────────────────────────────────────────┘
```

### 6.6 UX Notes

- Do not use “Buy,” “Sell,” or “Hold.”
- Use signal labels such as “Looks positive,” “Looks negative,” “Leans up,” “Leans down,” or “No opinion today.”
- Confidence should be visually meaningful but not over-dramatic.
- Cold-start language should not sound like a system failure.

---

## 7. Page Blueprint: Path

### 7.1 Purpose

The Path page provides position-sizing and risk context for a signal. It should be framed as research support, not as an instruction to deploy capital.

### 7.2 User Questions

- If this signal is worth studying, how large might the research-based sizing band be?
- Is the signal strong enough to justify any allocation in the model?
- What downside or exit context should I consider?
- Are rupee amounts hidden because of commercial or personal-context rules?

### 7.3 Suggested Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Path                                                         │
│ Position-sizing context for research use only.               │
├──────────────────────────────────────────────────────────────┤
│ Context banner                                               │
│ Example: “Position size is shown as direction + confidence    │
│ only in this context.”                                       │
├──────────────────────────────────────────────────────────────┤
│ Controls                                                     │
│ [Instrument selector] [Segment selector]                     │
├──────────────────────────────────────────────────────────────┤
│ Direction and Confidence                                     │
│ ┌──────────────────────┐ ┌───────────────────────────────┐   │
│ │ Direction            │ │ Confidence                    │   │
│ │ LOOKS POSITIVE       │ │ ██████░░░░ 62%                │   │
│ └──────────────────────┘ └───────────────────────────────┘   │
├──────────────────────────────────────────────────────────────┤
│ Sizing / Band Panel                                          │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Suggested research band: — / ₹ amount / range            │ │
│ │ Method: cautious fraction of full Kelly formula          │ │
│ │ Status: below / within / above healthy range             │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ Risk and Exit Context                                        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ E1       │ │ E2       │ │ E3       │ │ E4       │          │
│ │ Rule     │ │ Rule     │ │ Rule     │ │ Rule     │          │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├──────────────────────────────────────────────────────────────┤
│ Explanation and disclaimer                                   │
│ “This is a research sizing model, not a recommendation.”     │
└──────────────────────────────────────────────────────────────┘
```

### 7.4 Data Presented

| Data Type | Presentation | Design Intent |
|---|---|---|
| Signal direction | Large text/chip | Connect to Signals page |
| Confidence | Progress indicator | Carry forward signal strength |
| Kelly output | Amount, range, or suppressed dash | Provide risk-aware context |
| Sizing status | Below / within / above band | Avoid one-number overconfidence |
| Downside target | Short metric or note | Emphasize risk |
| Exit rules | Card grid | Show discipline after entry |

### 7.5 UX Notes

- The Path page is the most compliance-sensitive surface.
- Rupee values should be hidden or clearly contextualized when required.
- The page should avoid sounding like “how much you should buy.”
- Prefer wording such as “research band,” “model context,” or “sizing view.”
- The page should repeatedly remind users that final decisions happen outside AlphaVeda.

---

## 8. Page Blueprint: Accuracy

### 8.1 Purpose

The Accuracy page is the trust engine of AlphaVeda. It shows how past signals performed and whether the system has enough history to support confidence claims.

### 8.2 User Questions

- How many signals has AlphaVeda emitted?
- How many have matured and been graded?
- How often has AlphaVeda been right in similar cases?
- Which segments are still too early to judge?
- Are any weights pending review?

### 8.3 Suggested Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Accuracy                                                     │
│ A public scorecard for AlphaVeda’s research signals.         │
├──────────────────────────────────────────────────────────────┤
│ Past-performance disclaimer                                  │
│ “Past signal accuracy does not guarantee future returns.”    │
├──────────────────────────────────────────────────────────────┤
│ Summary Cards                                                │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐      │
│ │Signals   │ │Graded    │ │Hit rate  │ │Cold segments │      │
│ │emitted   │ │signals   │ │or score  │ │remaining     │      │
│ └──────────┘ └──────────┘ └──────────┘ └──────────────┘      │
├──────────────────────────────────────────────────────────────┤
│ Segment Scorecard                                            │
│ Segment | Observations | Hit rate | Status | Last reviewed   │
│ Fast grower | 28/30 | Too early | Cold | —                  │
│ Stalwart    | 45    | 61%       | Mature | 2026-07-10       │
├──────────────────────────────────────────────────────────────┤
│ Observation Progress                                         │
│ fast_grower: ███████████████████░░ 28 / 30                  │
│ cyclical:    ███████░░░░░░░░░░░░░ 11 / 30                  │
├──────────────────────────────────────────────────────────────┤
│ Weight Review Queue                                          │
│ Proposed changes awaiting review, with rationale and status. │
└──────────────────────────────────────────────────────────────┘
```

### 8.4 Data Presented

| Data Type | Presentation | Design Intent |
|---|---|---|
| Emitted signals | Summary metric | Show activity level |
| Graded outcomes | Summary metric | Show evidence base |
| Hit rate | Table and cards | Performance transparency |
| Observation count | Progress bars | Explain maturity threshold |
| Segment status | Status pill | Cold / mature / under review |
| Proposed weights | Expandable queue | Show governance and review |
| Last review date | Table field | Prevent stale model confidence |

### 8.5 UX Notes

- Accuracy must not be marketed as a guarantee.
- Low sample sizes should be visually distinguished from mature performance.
- “Too early” should be normalized, not hidden.
- The page should help users understand that a transparent model can still be wrong.

---

## 9. Data and System Process Infographic

```text
External Market Sources
(NSE/BSE Bhavcopy, fundamentals, macro data)
        │
        ▼
Ingest Pipeline
(fetch, normalize, validate, flag staleness/circuits)
        │
        ▼
Supabase Database
(instruments, OHLCV, predictions, outcomes, weights, ingest status)
        │
        ├──────────────────────┐
        ▼                      ▼
Signal Engine              Market Data UI
(arbitration, confidence,  (raw data visibility)
 calibration, no-call)
        │
        ▼
Prediction Ledger
(record emitted signal)
        │
        ▼
Outcome Resolution
(grade signal after horizon)
        │
        ▼
Accuracy UI
(public scorecard, trust loop)
```

### 9.1 Design Meaning

The data pipeline should be visible through the product. Users do not need to see every backend detail, but they should understand:

- when data last updated,
- whether signals are based on fresh inputs,
- whether a signal has been recorded,
- whether enough outcomes exist to trust a confidence claim,
- and whether the model is still in a cold-start state.

---

## 10. Interaction Patterns

### 10.1 Search and Selection

Users should be able to search or select an instrument from Market Data, Signals, and Path. The selected instrument should become a shared mental context across pages.

```text
Select TICKER on Market Data
        ↓
Open Signals for same TICKER
        ↓
Open Path for same TICKER
        ↓
Open Accuracy filtered to relevant segment
```

### 10.2 Simple / Pro Language Toggle

```text
Simple mode:
“Looks positive”
“How often right”
“Too early”
“No opinion today”

Pro mode:
“Leans up”
“Hit rate”
“Cold start”
“No call”
```

The toggle should not change calculations. It should only change labels, explanatory copy, and glossary framing.

### 10.3 Glossary Pattern

Terms that may confuse users should be clickable or tappable:

```text
Confidence [?]
Cold start [?]
Market regime [?]
Kelly band [?]
No call [?]
```

Each glossary entry should answer:

1. What does this mean?
2. Why does it matter?
3. How should the user interpret it safely?

---

## 11. Empty, Loading, Error, and Stale States

AlphaVeda should treat non-happy paths as first-class design states.

### 11.1 Empty State

```text
No data yet
We are still setting up this data source. Check back soon.
```

Use for instruments or pages where no rows exist yet.

### 11.2 Stale State

```text
Data last updated 2 days ago
Signals may be limited until the next successful ingest.
```

Use when ingest is delayed or missing.

### 11.3 Cold-Start State

```text
Just getting started
This segment needs 30 graded results before AlphaVeda shows stronger confidence.
```

Use when model history is insufficient.

### 11.4 No-Call State

```text
No opinion today
AlphaVeda does not see enough evidence for a useful signal right now.
```

Use when arbitration suppresses weak or conflicting signals.

### 11.5 Error State

```text
Something did not load
Please try again later. AlphaVeda is not showing a signal until the data is available.
```

Avoid exposing operator instructions such as “run ingest pipeline” to public users.

---

## 12. Compliance and Copy Rules

AlphaVeda should follow strict public-language rules.

### 12.1 Avoid

- “Buy”
- “Sell”
- “Hold”
- “You should invest”
- “Guaranteed”
- “Sure return”
- “Recommended for you”
- Any copy that implies personalized advice

### 12.2 Prefer

- “Research signal”
- “Looks positive”
- “Looks negative”
- “No opinion today”
- “Confidence based on past grading”
- “Research only”
- “Not investment advice”
- “Consult a SEBI-registered adviser”

### 12.3 Compliance Infographic

```text
Signal generated
      │
      ▼
Language filter
(no advice verbs, no personalized instruction)
      │
      ▼
Research-only framing
      │
      ▼
SEBI disclaimer visible
      │
      ▼
User interprets independently
```

---

## 13. Visual Design Direction

### 13.1 Tone

AlphaVeda should feel:

- calm,
- premium,
- analytical,
- transparent,
- restrained,
- and compliance-aware.

It should not feel:

- urgent,
- gamified,
- speculative,
- broker-like,
- or tip-driven.

### 13.2 Visual Hierarchy

Recommended hierarchy:

```text
1. Page title
2. Plain-language purpose line
3. Data-quality or compliance banner
4. Main signal/data/accuracy surface
5. Supporting explanation
6. Footer disclaimer
```

### 13.3 Component Style

| Component | Suggested Feel |
|---|---|
| Signal cards | Large, calm, high-contrast, minimal noise |
| Confidence bars | Thin and precise, not flashy |
| Status pills | Clear color and text, always accessible |
| Tables | Dense but readable, mono font for numbers |
| Banners | Informative, not alarming unless data is unsafe |
| Glossary modals | Short, human, educational |
| Disclaimer | Persistent, legible, non-dismissable |

---

## 14. Suggested Implementation Priorities

### Priority 1 — Public Trust Baseline

- Ensure every page shows a SEBI-safe research-only frame.
- Show data freshness prominently.
- Make no-call and cold-start states clear.
- Ensure public users never see operator-facing backend language.

### Priority 2 — Core Page Coherence

- Market Data verifies inputs.
- Signals explains current output.
- Path provides risk/sizing context.
- Accuracy proves or challenges trust.

### Priority 3 — Interaction Continuity

- Preserve selected instrument across pages.
- Link from each page to the next logical page.
- Use consistent terms across Simple and Pro modes.

### Priority 4 — Evidence Before Monetization

- Do not push paid conversion until the accuracy ledger has enough visible graded outcomes.
- Use public performance history as the basis for any premium feature positioning.

---

## 15. One-Page Blueprint Summary

```text
┌──────────────────────────────────────────────────────────────┐
│                         AlphaVeda                           │
│      Transparent Indian equity research. Not advice.         │
├──────────────────────────────────────────────────────────────┤
│ NAV: Market Data | Signals | Path | Accuracy | Simple/Pro    │
├──────────────────────────────────────────────────────────────┤
│ Market Data                                                  │
│ Shows raw OHLCV, circuit flags, and ingest freshness.         │
├──────────────────────────────────────────────────────────────┤
│ Signals                                                      │
│ Shows current research signal, confidence, context, and       │
│ no-call/cold-start states.                                   │
├──────────────────────────────────────────────────────────────┤
│ Path                                                         │
│ Shows risk-aware sizing context and exit-rule framing, with   │
│ strict compliance guardrails.                                │
├──────────────────────────────────────────────────────────────┤
│ Accuracy                                                     │
│ Shows public grading, hit rates, observation counts, and      │
│ model-review status.                                         │
├──────────────────────────────────────────────────────────────┤
│ GLOBAL: SEBI disclaimer, glossary, plain-language mode,       │
│ data-quality warnings, research-only copy.                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 16. Closing Design Principle

AlphaVeda should be designed as a trust engine, not a prediction billboard.

Every screen should answer one of four questions:

1. **What data are we using?** — Market Data
2. **What does the model currently see?** — Signals
3. **What is the risk-aware context?** — Path
4. **How well has this worked before?** — Accuracy

If a design element does not support one of those questions, it should be reconsidered.

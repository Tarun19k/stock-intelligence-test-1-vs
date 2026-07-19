# AlphaVeda MVP — UX Options, Page Inventory, and Data Audit

**Prepared:** 2026-07-19  
**Purpose:** Establish a repository-evidenced starting point for choosing an AlphaVeda MVP UX direction. This is a product/design decision brief, not a production implementation plan.  
**Evidence rule:** “Confirmed” means directly evidenced by the current repository. “Reported” means a dated status document reports it; it has not been independently re-verified against the deployed site in this review. “Recommendation” is a proposed next step.

## 1. Executive decision

### Recommended direction: **Option A — Verified Research Loop**

Use the existing four-page research flow as the primary MVP, with the current per-instrument page retained as a **soft-launch, non-primary** drill-down surface:

```text
Market Data → Signals → Path → Accuracy
                     ↘
                 Instrument detail (soft-launch)
```

This option is the lowest-risk fit because it uses the data already read by the Next.js pages, makes evidence/freshness visible before interpretation, preserves AlphaVeda’s research-only framing, and does not pretend that unavailable fundamentals, macro, news, or attribution data exist. It matches the established product flow of verify data → inspect signal → understand risk context → inspect historical record → decide independently.

**Do not choose a news-led or “newspaper” primary design for the MVP.** The gap register says the necessary fundamentals and macro layers are not live, and flags screenshot/hot-tip psychology risk. A news-led layout can be revisited only after the staged data prerequisites are met.

## 2. What this review examined

### Governing/current sources reviewed

1. Current Next.js routes, global layout, navigation, shared components, Supabase data access, and current CSS under `alphaveda/web/`.
2. AlphaVeda’s MVP specification, design overview, gap register, revenue roadmap, background briefing, and status resume log.
3. The recent `G20` implementation commit, which added the instrument route.
4. Existing web test coverage for the four primary navigation routes.

### Important source reconciliation

Some older status documents conflict with later code and later status notes. For example, the 2026-07-13 background briefing says live signal data was absent, while the later status resume reports a deployed frontend with instrument and signal data, and current pages read these tables directly. This brief therefore treats **current code** as the best evidence of what the UI can render, treats the **gap register** as the canonical known-gap list, and labels deployment claims as reported rather than independently verified.

## 3. Confirmed MVP page inventory

| Surface | Route | Navigation status | Confirmed current purpose | MVP disposition |
|---|---|---:|---|---|
| Market Data | `/` | Primary | Displays active instruments, latest EOD OHLCV, circuit marker, and ingest freshness state. | Keep primary. Entry point for data verification. |
| Signals | `/signals` | Primary | Displays recent stored predictions, confidence framing when evidence is mature, class/regime context, and active/proposed signal weights. | Keep primary. Core research interpretation surface. |
| Path | `/path` | Primary | Displays research-mode position band, confidence, target/downside fields, and controlled sizing visibility. | Keep primary, but position it as risk context—not an instruction. |
| Accuracy | `/accuracy` | Primary | Displays resolved outcomes, historical success percentage/returns, review status, and past-performance warning. | Keep primary. The trust/proof surface. |
| Instrument detail | `/instrument/[ticker]` | Not in primary nav | Displays exactly five soft-launch elements: latest non-circuit price, current signal, Lynch class, per-instrument resolved-count note, and an aggregate weekly strip. | Retain as soft-launch only until its stated promotion conditions are met. |
| Landing / waitlist / privacy | Not present as a Next.js route in the inspected navigation | Not present | Required commercial/onboarding surfaces are tracked as open work. | Not part of the currently implemented MVP navigation. |

### Why the instrument detail page must remain constrained

The `G20` decision allows a narrow detail MVP but requires a mandatory aggregate/watchlist strip, no primary-navigation promotion before landing/waitlist work, and no external promotion. Its current code matches the narrow five-element intent. Any UX redesign must preserve those structural safeguards before it adds richer content.

## 4. Confirmed data currently presented

### 4.1 Shared data properties

- The Next.js pages read Supabase server-side using `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`; the service key is intentionally never sent to client components.
- All inspected primary data pages declare `revalidate = 3600`, so the current rendering contract is cached/revalidated hourly—not real-time streaming.
- EOD market facts should be named **“latest EOD”** or shown with their actual trade date. Do not call them “live” or “real-time” in UX copy.
- The global layout renders primary navigation, a language-mode provider, glossary provider/modal, and a non-dismissible SEBI disclaimer on every route.

### 4.2 Page-to-data contract

| Page | Supabase tables read | Displayed fields / calculations | Honest UI state already supported |
|---|---|---|---|
| Market Data | `instruments`, `ohlcv`, `ingest_status` | Ticker; classification; latest date; open/high/low/close; volume; circuit flag; instrument count; stale-day calculation. | No data; data not yet available for an instrument; stale ingest warning. |
| Signals | `accuracy_predictions`, `instruments`, `signal_weights` | Direction; confidence; emitted date; Lynch class; regime; active weight; proposed-weight count; segment observation count. | No signals; proposed weights pending review; “too early” confidence state below 30 observations. |
| Path | `accuracy_predictions`, `instruments`, `signal_weights`, `waitlist` | Position band from confidence/magnitude/downside; target; stop/downside; emitted date; proposed-weight count; optional personal-context rupee amount. | No positions; weight update pending; deliberate rupee suppression for public/research mode. |
| Accuracy | `accuracy_outcomes`, `accuracy_predictions`, `instruments`, `signal_weights` | Total resolved; historical success percentage; average resolved return; pending review count; ticker; direction; confidence; hit/miss; return; resolved date. | No results; past-performance warning; overdue active-weight review. |
| Instrument detail | `instruments`, `ohlcv`, `accuracy_predictions`, `accuracy_outcomes` | Latest non-circuit close + trade date; latest direction; classification; per-instrument resolved count; active-instrument count; weekly aggregate bullish count. | No price; no signal; insufficient graded evidence. |

### 4.3 Data that must **not** be designed as present

| Data / feature | Evidence of status | Required UX treatment now |
|---|---|---|
| Fundamentals (five-year trend, ROE/ROCE, debt, promoter pledge, FCF-vs-profit) | `fundamentals` is empty / ingest is unscheduled (G1). | Omit from MVP detail pages; do not show zeros or mock scores. |
| Fresh macro regime | `macro_regime` is reported stale (G13). | Do not score or summarise macro context; label unavailable if a future placeholder is needed. |
| Per-signal attribution / root-cause analysis | `prediction_components` is missing (G5). | Do not claim “why the model decided” beyond the fields currently stored/displayed. |
| Warm calibration | G7 remains open; Signals uses a cold-start display guard. | Display “too early” / insufficient evidence rather than a precise-looking confidence percentage. |
| Real-time prices | MVP specification states EOD only. | Show trade date and freshness; never present as intra-day/live data. |
| User accounts / portfolio management / trade execution / alerts / comparison | Explicitly out of MVP scope in the MVP specification. | Do not imply these capabilities in navigation or CTA copy. |
| Landing, waitlist, and privacy policy | Still open gaps (G4/G8/G10/NG-5). | Do not treat commercial/onboarding flow as shipped. |

## 5. Capability status — confirmed, reported, and unresolved

| Capability | Current assessment | Evidence and limitation |
|---|---|---|
| EOD OHLCV visibility | **Confirmed in code** | Market Data reads instruments/OHLCV/ingest status and exposes stale/no-data states. |
| Stored signal display | **Confirmed in code** | Signals reads `accuracy_predictions`; it does not compute a signal in the page. |
| Cold-start restraint | **Confirmed in code; integrity issue open** | UI suppresses percentage display below its 30-observation segment threshold; G19 documents a denominator mismatch with engine-side readiness. |
| Position/risk band | **Confirmed in code** | Path calculates a capped quarter-Kelly band from stored values; public rupee values fail closed. The underlying hard-coded portfolio value remains an open architecture gap. |
| Historical accuracy ledger | **Confirmed in code** | Accuracy joins outcomes to predictions and shows historical data with a warning. Meaningful evidence depends on outcomes accumulating. |
| SEBI and research-only guardrails | **Confirmed in code/tests** | Root layout includes the fixed disclaimer; current test suite covers the four primary routes. |
| Simple/Pro language and glossary | **Confirmed in code, but documentation is stale** | Current layout wraps language/glossary providers; the gap register’s older “unwired” wording conflicts with the inspected code and its closure summary. |
| Instrument detail page | **Confirmed in code; promotion gated** | The route exists but is absent from primary nav, consistent with G20’s soft-launch restriction. |
| Landing/waitlist/privacy | **Open** | No inspected primary-nav route; gaps remain open. |
| Fresh fundamentals/macro/attribution | **Open** | Data prerequisites are not available; no rich “all data” view should be designed around them. |

## 6. UX principles that every option must preserve

1. **Evidence before interpretation.** A user can reach the data source/trade date and the accuracy record without scrolling through promotional copy.
2. **Research, not instruction.** Use BULL/BEAR/no-call research labels only with the fixed disclaimer. Never use personalised “buy,” “sell,” or “what you should do next” language.
3. **Freshness is a first-class state.** The date shown with EOD data is part of the content, not hidden metadata.
4. **Uncertainty is a valid outcome.** Cold-start, no-signal, no-price, stale-data, and suppressed-sizing states must have intentional designs—not blank regions.
5. **One display value, one source.** Do not recalculate the same market metric in multiple UI components or silently combine fresh and stale sources.
6. **A detail page is not a screenshotable call.** Preserve the aggregate strip and show uncertainty/counterevidence at the same visual weight as the current directional label.
7. **Progressive disclosure, not missing-data theatre.** Hide deferred layers entirely or state “unavailable”; do not use empty KPI cards or fabricated estimates.

## 7. UX options

### Option A — Verified Research Loop (**recommended for MVP**)

**Concept:** Make the four current routes a deliberate, linear research workflow. The user begins with source/freshness, sees stored signals, checks risk context, and closes the loop with the ledger. Instrument detail is a secondary drill-down.

```text
1. Market Data          “What did the system receive?”
2. Signals              “What did the system record?”
3. Path                 “What risk context is available?”
4. Accuracy             “How has this type of output resolved?”
5. Instrument detail    “How does one instrument sit in the whole set?”
```

**Page hierarchy**

- **Market Data:** freshness/status strip → search/filter → compact latest-EOD table → per-row access to instrument detail when G20 promotion permits.
- **Signals:** cold-start or weight-review state first → recent predictions table → active weights as a secondary audit panel.
- **Path:** research-mode suppression state first → position-vs-band table → method/risk note; no giant directional callout.
- **Accuracy:** past-performance warning → resolved count → accuracy/return evidence → detailed outcomes table.
- **Instrument detail:** retain exactly the current five components, adding no fundamentals/news/macro cards until their data gates clear.

**Why it fits:** It is directly supported by present route/data contracts and reinforces the stated trust moat: the accuracy ledger.

**Risk:** It may feel less exciting than a news-led product. Mitigation: improve scanability, hierarchy, and language—not speculative data density.

### Option B — Evidence Ledger First

**Concept:** Make `/accuracy` the landing surface once a landing route exists. It starts with “what AlphaVeda has been right/wrong about,” then users navigate to Signals and Market Data for auditability.

**Best for:** Data-curious experimenters and the trust-first monetisation thesis.

**Information order**

```text
Ledger evidence → current signal list → raw market inputs → risk/sizing context
```

**Strength:** The product differentiator becomes visible immediately; it avoids the appearance of a tip sheet.

**Constraint:** It is premature if resolved outcomes remain sparse. Before the proof-window threshold, this option needs a strong honest-empty state rather than a metric-heavy hero.

### Option C — Guided Research Brief

**Concept:** Add a future onboarding/landing layer that asks the user to choose a ticker, then guides them through a short checklist: freshness → current research signal → evidence maturity → risk context → historical record.

**Best for:** First-time retail users after the landing/waitlist/privacy work is completed.

**Strength:** Converts the current collection of pages into a comprehensible workflow without adding new investment calls.

**Constraint:** This is not a substitute for the missing onboarding and privacy work. It must be built after those gates, and it should link to existing surfaces rather than duplicate their calculations.

### Option D — Newspaper/Policy Brief (**defer**)

**Concept:** Editorial, one-page instrument narrative with macro, fundamentals, policy context, and a few sourced news items.

**Why defer:** G21 explicitly says two required layers do not yet exist, and requires guardrails against hot-tip psychology. It would create a misleading hierarchy today by making sparse/absent supporting data look complete.

**Permitted early fragment:** A small Lynch-style “What the company does” / classification explainer and a self-verification checklist can be added to the soft-launch detail page because it reuses existing fields. It must remain subordinate to data freshness and the aggregate strip.

## 8. Recommended MVP information architecture

### Navigation now

```text
AlphaVeda
├── Market Data       primary: verify inputs
├── Signals           primary: inspect current stored output
├── Path              primary: inspect risk/position context
├── Accuracy          primary: inspect historical record
└── Instrument detail hidden/soft-launch: per-ticker context
```

### Navigation after the landing/waitlist gates

```text
Start here (trust story) → Market Data → Signals → Path → Accuracy
                                      ↘
                              Instrument detail (only after G20 graduation)
```

### What is deliberately absent

- No portfolio execution, broker action, or generic action cards.
- No real-time/intraday promise.
- No cross-ticker comparison or alerts.
- No data-rich fundamentals/macro/news module until data availability and freshness gates are satisfied.

## 9. Design system and implementation constraints

### Existing visual foundation to retain

The web app already uses Fraunces for display, DM Sans for body copy, DM Mono for numeric data, an ivory/surface palette, and indigo/gold/emerald/terra status tokens. The layout is currently table- and card-oriented, with responsive grid primitives and a fixed regulatory footer. UX work should extend these components rather than introduce a parallel theme.

### Dynamic-data interface requirements

For any future component, bind and display at minimum:

| Component type | Required fields | Required failure state |
|---|---|---|
| EOD market metric | value, trade date, source/ingest freshness, circuit flag where applicable | “No data yet” or stale banner; never a fake current value. |
| Signal | direction/no-call, emitted date, class/regime, evidence-readiness state | “Too early” / no signal; no bare percentage below evidence threshold. |
| Path/risk | band, target/downside inputs, method label, personal-context eligibility | research-mode suppression; no public rupee figure. |
| Accuracy | outcome count, calculation window, historical warning, resolved date | an honest empty ledger, not a performance claim. |
| Detail aggregate strip | active tracked count, same-period aggregate signal count, period start | unavailable state if the weekly query fails. |

### Accessibility and comprehension criteria

- Retain the language-mode toggle and glossary access from the global shell.
- Keep table headers, visible status labels, and text equivalents for color states.
- Test the primary screen at narrow mobile and standard desktop widths before visual migration.
- Treat the fixed footer as reserved viewport space so it does not obscure table rows or primary controls.

## 10. Decisions and gates before visual migration

### Decisions needed from product owner

1. Confirm **Option A** as the MVP default, or explicitly select B/C/D.
2. Confirm whether the G20 instrument route remains preview-only; do not add it to navigation without its documented graduation evidence.
3. Decide whether the initial landing page is an evidence-led trust story (recommended) or a guided research checklist.
4. Run the previously requested phone walkthrough and five-second recall test before choosing a high-fidelity visual direction.

### Engineering/data gates

1. Resolve G19 before presenting any “warm” confidence state as model readiness.
2. Preserve public sizing suppression; do not expose the hard-coded personal portfolio value.
3. Build landing, waitlist, and privacy surfaces together before collecting signups.
4. Do not add macro, fundamentals, or source-attribution cards until G1/G13/G5 respectively provide valid data.
5. Add an error-visible data-fetch state before presenting production health as solved; current page code falls back to empty arrays on Supabase responses.

## 11. Suggested next deliverable

After an option is selected, create one **code-adjacent, data-bound screen specification** for the chosen surface—not a broad redesign:

- component inventory;
- exact existing data fields and source table;
- loading, no-data, stale, cold-start, and error states;
- copy in Simple and Pro modes;
- screenshot/mobile acceptance criteria;
- SEBI and algorithmic-label placement;
- Playwright assertions for the new route/surface.

That small, reversible deliverable will convert the direction decision into an implementation plan while respecting AlphaVeda’s current data and compliance boundaries.

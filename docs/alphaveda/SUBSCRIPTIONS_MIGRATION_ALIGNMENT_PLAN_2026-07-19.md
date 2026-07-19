# AlphaVeda Subscriptions, GSI Gap Map, and Migration-Alignment Plan

**Prepared:** 2026-07-19  
**Status:** Decision-support brief; no product, data-governance, provider, or deployment change is approved by this document.  
**Evidence labels:** **Confirmed** = current repository code or configuration. **Reported** = dated repository status record, not independently re-verified against production in this review. **Recommendation** = proposed plan. **Estimate** = planning range, not a delivery commitment.

---

## 1. Executive summary

### The subscription opportunity

A daily, weekly, or monthly research-update subscription fits AlphaVeda **only** if it is treated as an opt-in, evidence-led **research digest**, not a stock-call or execution service. The first version should let a signed-in user follow a small **research list** of selected instruments. “Portfolio updates” should initially mean a user-curated set of tickers, not broker-connected holdings or personalised allocation advice.

The subscription product should deliver four facts together:

1. what changed in the stored EOD data;
2. whether AlphaVeda recorded a new, changed, or no signal;
3. the evidence-readiness and freshness state; and
4. a direct link to the public accuracy record and fixed research-only/SEBI framing.

No email should say “buy,” “sell,” “act now,” or present a generated message as personal advice.

### The migration finding

The April 2026 GSI Vercel plan was a migration of a **broad, multi-market Streamlit dashboard**. AlphaVeda is not that migration in code or scope: its own background briefing says it is a separate, smaller India-equities product with a different trust model. The observed “drift” is therefore partly a deliberate strategic pivot—not merely late delivery.

However, there is a real alignment problem: old plans, inventory files, gap records, and deployed code do not all describe the same current state. The immediate corrective action is to designate a current architecture/status source of truth and measure work against AlphaVeda’s current proof-window goals, rather than against the old GSI full-migration plan.

---

## 2. Confirmed current state relevant to subscriptions

### 2.1 What exists today

| Area | Confirmed / reported state | Subscription relevance |
|---|---|---|
| Public AlphaVeda research pages | Four primary Next.js routes: Market Data, Signals, Path, Accuracy; a non-primary instrument detail route also exists. | Provides the data and landing surfaces a digest can link back to. |
| Data refresh model | Primary Next.js pages use `revalidate = 3600`; market data is latest EOD, not streaming intraday data. | A “daily” update must be described as a post-ingest EOD digest, never as live alerts. |
| Signal persistence | Pages read stored `accuracy_predictions`, `accuracy_outcomes`, and `signal_weights`. | Enables change detection and later outcome summaries without recomputing signals in the email worker. |
| Existing commercial marker | `waitlist.converted_at` is used to derive commercial state; `waitlist_signup.py` is a standalone Streamlit form, not a current Next.js customer route. | A waitlist does not supply account identity, consent lifecycle, preferences, or delivery capability. |
| Authentication | Current web code treats visitors as anonymous; public rupee sizing is fail-closed/suppressed. | Auth is a prerequisite for durable per-user subscriptions and private portfolios. |
| Scheduled work | Ingest runs on weekdays; a watchdog validates that the scheduled ingest fired. | A digest job should run only after a successful, fresh ingest—not at a blind fixed time. |
| Notification provider | No email, push, SMS, or webhook provider is configured in inspected code. | Delivery infrastructure is a new, separately approved dependency. |

### 2.2 What does not exist today

- A Next.js landing, signup, privacy, or authenticated account route.
- User-to-instrument subscription preferences.
- Portfolio ownership/holdings storage.
- Verified email-consent lifecycle, unsubscribe workflow, or notification delivery provider.
- A tested post-ingest change-detection/digest pipeline.
- A licensed commercial market-data decision for distributing market facts to subscribers.

These absences are material. A notification feature should not be approximated through a public form or an unauthenticated URL parameter.

---

## 3. Product model: research subscriptions, not stock alerts

### 3.1 Recommended vocabulary

| Avoid | Use instead | Reason |
|---|---|---|
| Stock alert | Research update / evidence update | Avoids urgency and implicit action framing. |
| Buy/sell notification | New recorded signal / signal changed / no new recorded signal | Keeps output descriptive and algorithmically labeled. |
| Portfolio recommendation | Research-list summary | The initial product has no verified holdings, suitability assessment, or execution context. |
| Real-time alert | Post-ingest daily update | Current product uses EOD data and hourly page revalidation. |

### 3.2 Subscription tiers by cadence

| Cadence | User value | Data included | Recommended eligibility | Delivery rule |
|---|---|---|---|---|
| Daily | Short post-ingest record of material changes. | Latest EOD date, signal status/change, data freshness, cold-start state, link to detail/accuracy. | Signed-in, email-verified user; explicit per-ticker opt-in. | Send only after the target day’s ingest status is OK and a material-change rule fires. |
| Weekly | Calm research recap. | Weekly signal-change summary, aggregate research-list context, new resolved outcomes, data-quality exceptions. | Same as daily. | One scheduled digest after the final validated trading-day ingest. |
| Monthly | Long-horizon evidence review. | Accuracy record change, maturity progress, stale-data incidents, weight-review status. | Same as daily. | Calendar-month rollup; no “monthly stock call.” |

### 3.3 Material-change rule for v1

A daily message should not be sent simply because a clock ticked. It should send only when at least one of these **stored-data** events occurs:

- a new prediction was emitted for a followed instrument;
- the stored direction changed from the prior emitted prediction;
- a prediction became resolved and its outcome was recorded;
- data freshness crossed into a stale/failed state; or
- a selected instrument has no new signal, but the user opted into an explicit weekly/monthly “no material change” recap.

**Recommendation:** Do not include a calculated price percentage in v1 unless its calculation is shared with the on-page canonical calculation and the digest stores the data-as-of timestamp. The first version can remain useful without price-performance copy.

---

## 4. Suggested data and workflow architecture

### 4.1 Minimum new entities (conceptual only)

These names are proposed contracts, not approved migrations.

| Entity | Purpose | Key fields | Critical safeguards |
|---|---|---|---|
| `user_profiles` | Link authenticated user to consent and display preferences. | `user_id`, `email_verified_at`, `locale`, `created_at`. | User identity comes from auth; do not duplicate secrets or passwords. |
| `research_lists` | A user-named list of tracked instruments. | `id`, `user_id`, `name`, `created_at`. | Start with self-curated lists; no broker account connection. |
| `research_list_items` | Instruments in a research list. | `list_id`, `instrument_id`, `created_at`. | Enforce ownership through row-level security. |
| `digest_preferences` | Cadence/channel/consent settings. | `user_id`, `cadence`, `email_enabled`, `consented_at`, `unsubscribed_at`. | Default off; explicit consent and one-click unsubscribe required. |
| `digest_deliveries` | Immutable operational record of what was sent. | `id`, `user_id`, `cadence`, `as_of_date`, `status`, `idempotency_key`, `sent_at`. | No signal recomputation; prevent duplicate delivery and provide audit trail. |
| `digest_items` | Source snapshot for each delivered claim. | `delivery_id`, `instrument_id`, `prediction_id`, `outcome_id`, `ingest_status_id`, `source_as_of`. | Every displayed claim is traceable to stored data/date. |

### 4.2 Event-driven flow

```text
NSE/BSE EOD ingest
  → validate ingest_status for target date
  → stored predictions / outcomes available
  → material-change query (read-only)
  → build immutable digest snapshot
  → compliance copy + source/as-of labels
  → approved notification provider sends email
  → record delivery / bounce / unsubscribe status
  → user follows link to AlphaVeda detail and Accuracy pages
```

**Hard rule:** the notification worker must run **after** target-date ingest validation. The existing ingest watchdog proves that “scheduled job ran” and “fresh usable data exists” are different operational questions.

### 4.3 Why a research list should precede a portfolio feature

A portfolio implies holdings, cost basis, allocation, investor suitability, and potentially advice-like interpretation. None of those are currently available or in scope. A research list provides most of the user value—“keep me informed about these instruments”—without claiming possession, calculating personal exposure, or asking users to disclose sensitive financial data.

A later portfolio phase may be considered only after authentication, privacy/DPDP treatment, data governance, and a separately scoped research-only framing are approved.

---

## 5. Compliance, privacy, and data-licensing gates

### 5.1 Required before collecting or emailing users

1. **Authentication and verified ownership** — subscriptions need a durable authenticated identity, not only an email field.
2. **Privacy/DPDP policy and consent record** — the gap register already identifies privacy as required before the waitlist gathers email data.
3. **Unsubscribe and preference management** — change cadence, pause, delete list, and stop delivery without support intervention.
4. **SEBI-safe copy templates** — disclaimer, algorithmic label, and no personalised action language in every digest.
5. **Commercial data-licensing decision** — GSI product documentation identifies Yahoo Finance’s redistribution restriction; a paid/licensed source may be needed before commercial distribution.
6. **Source/as-of disclosure** — every factual market or signal statement needs a date and source/pipeline reference.
7. **Delivery-provider security review** — a provider must be selected and approved; credentials must remain server-side.

### 5.2 Digest template contract

Every sent update should contain:

```text
Research update — not investment advice
As of: [target trading date] · Data: [EOD / status]

[Instrument]
Recorded state: [positive / negative / no call]
Evidence readiness: [too early / mature only when valid]
What changed: [stored event description]
Verification: [link to instrument / signal / accuracy record]

Algorithmic-label and SEBI text
Manage preferences | Unsubscribe
```

No signal section should omit the fixed financial-research framing merely because it is delivered by email rather than rendered in the application.

---

## 6. Subscription roadmap and planning estimates

### Estimation method

These are **implementation effort bands**, not dates or commitments. They assume one experienced full-stack engineer, no paid provider procurement delay, and no discovered schema/security blocker. “Week” means a sequenced planning week, not a calendar promise. Security/legal/data-licensing approval can extend any phase.

| Band | Meaning |
|---|---|
| XS | Up to 1 focused engineering day. |
| S | 2–4 focused engineering days. |
| M | 1–2 focused engineering weeks. |
| L | 2–4 focused engineering weeks. |

### Phase 0 — Product and governance decision (XS–S)

**Goal:** freeze the first subscription promise before building.

- Select email-only v1; exclude push/SMS/webhooks.
- Select research-list-only v1; exclude broker-linked portfolios.
- Approve cadence semantics and material-change rules.
- Approve provider selection process, privacy language, licensing decision owner, and success metrics.
- Define a digest-specific compliance test matrix.

**Exit evidence:** approved product one-pager, data-flow diagram, copy template, and explicit authorization for any schema/provider work.

### Phase 1 — Trust and identity foundation (M)

**Goal:** make user subscriptions safely addressable.

- Deliver landing, waitlist, privacy/DPDP, auth, and preference-management surfaces as a coherent workstream.
- Establish verified user identity and user-owned research lists.
- Add consent/unsubscribe audit fields and RLS policy tests.

**Exit evidence:** a user can sign in, create/delete a research list, choose cadence, withdraw consent, and see no other user’s preferences.

### Phase 2 — Ingest-to-digest data path (M)

**Goal:** produce a dry-run, traceable digest after valid ingest.

- Build stored-event/material-change query.
- Build immutable digest snapshots keyed to ingest/prediction/outcome records.
- Add idempotency, retry, failure logging, and stale-ingest suppression.
- Add no-send state when no material change occurs.

**Exit evidence:** test fixtures demonstrate new prediction, changed signal, resolved outcome, stale data, duplicate-run, and no-change scenarios.

### Phase 3 — Email delivery and user control (S–M)

**Goal:** send a limited internal/pilot email safely.

- Integrate one approved delivery provider.
- Use transactional/template sending; keep provider credentials server-side.
- Render source/as-of labels, algorithmic wording, legal disclaimer, preference, and unsubscribe links.
- Record delivery, error, bounce, and unsubscribe status.

**Exit evidence:** controlled pilot delivery to test accounts, with delivery logs and unsubscribe test evidence.

### Phase 4 — Pilot, measurement, and controlled expansion (M)

**Goal:** validate usefulness without expanding scope.

- Pilot daily and weekly updates with a small consented group.
- Measure delivery success, unsubscribe rate, link-through to verification pages, stale-data suppression rate, and user-reported clarity.
- Add monthly digest only after daily/weekly reliability is demonstrated.

**Exit evidence:** review with measured results and a decision to continue, modify, or stop.

### What is intentionally deferred

- Push notifications, SMS, WhatsApp, and third-party social distribution.
- Broker connections, holdings imports, transaction data, cost basis, P&L, and execution.
- Personalised allocation or “what you should do” summaries.
- Live/intraday alerts and price-trigger automation.

---

## 7. GSI Dashboard and AlphaVeda: capability gap map

### 7.1 Product position and scope

| Dimension | GSI Dashboard | AlphaVeda | Gap / implication |
|---|---|---|---|
| Market scope | 9 markets, 559 tickers, 38 groups. | India equities focus with a deliberately constrained instrument universe. | AlphaVeda rejects breadth to restore reliability; do not score it against GSI’s coverage count. |
| Frontend | Streamlit monolith with sidebar-driven routing. | Next.js App Router with four primary research pages. | A technical migration of the GSI UI was not completed; AlphaVeda is a separate build. |
| Core analysis | Weinstein/Elder technical frameworks, multiple dashboard tabs, market/group views. | Stored momentum-led signal pipeline, risk band, and public accuracy ledger. | AlphaVeda has less analytic breadth but stronger outcome-accountability intent. |
| Portfolio | Mean-CVaR allocator and related portfolio computation. | Kelly-style position band; public rupee amount is suppressed. | Neither is ready for authenticated personal portfolio tracking. |
| Global intelligence | Global intelligence, news/RSS, impact chains, council review. | No equivalent global/news surface in primary MVP. | This is a deliberate non-goal until fresh macro/news data can be safely presented. |
| Data freshness | yfinance/RSS with rate limits and past trust failures. | NSE/BSE EOD ingest, stored DB records, watchdog. | AlphaVeda currently has a simpler data model but still needs clean-run proof. |
| Accuracy evidence | Forecast history was session-state based / persistence unresolved in the old plan. | Public prediction/outcome ledger is a central concept. | AlphaVeda’s key strategic differentiator; still constrained by sample size and calibration gaps. |
| Accounts / alerts | GSI roadmap listed alerts as post-MVP requiring auth/backend. | Auth, waitlist route, preferences, delivery are not implemented. | Subscription updates are a future shared capability gap, not a small UI addition. |
| Monetisation | Earlier GSI roadmap deferred paid tier pending traction and licensing. | Proof-window roadmap expects waitlist/ledger evidence before a paid ask. | Both products depend on licensing, user identity, and trust; AlphaVeda is more explicit about measurable proof. |

### 7.2 Page-level comparison

| GSI surface | Closest AlphaVeda surface | What carries over conceptually | What does not carry over now |
|---|---|---|---|
| Home / ticker bar | Market Data + future landing | Discovery and high-level status. | Global, multi-market ticker stream and top-mover breadth. |
| Stock Dashboard | Instrument detail + Signals + Path | Per-instrument research. | GSI’s four-tab charts, forecast, comparison, and broad technical panel. |
| Week Summary / market/group views | No primary equivalent | Aggregate context can inform future research-list summaries. | Cross-sector / cross-market overview is out of AlphaVeda MVP scope. |
| Global Intelligence | Deferred policy/news brief | Cited context and data freshness principles. | Global RSS, geopolitical impact chains, stock watchlists. |
| Council Review | Detail-page context only | Educational framework framing. | Multi-lens stock verdict synthesis should not silently become a new AlphaVeda scoring engine. |
| Portfolio Allocator | Path | Risk/sizing context. | Multi-asset optimisation, portfolio entry, and persistent holdings. |
| Observability | Ingest status/watchdog, no public equivalent | Data-health discipline. | Full operator observability UI is not currently a public AlphaVeda surface. |

---

## 8. Migration-plan drift: baseline versus reality

### 8.1 Baseline plan

The April GSI migration plan proposed porting the broad Streamlit product to Next.js/Vercel, preserving its multi-market pages and Python services. The planned destination included Home, Dashboard, Week Summary, Global Intelligence, and Observability, with Redis, Vercel Python functions/workflows, Supabase forecast persistence, and eventually a cutover from Streamlit.

### 8.2 Current observed trajectory

The AlphaVeda documents describe a separate product created after the April plan: India-only, one-signal, accuracy-led, and independently deployed. Current code uses Next.js and server-side Supabase queries directly. FastAPI route code exists, but the current frontend does not use it as its data path; the old Railway/Fly architectural briefs are therefore not reliable evidence of the live runtime path.

### 8.3 Drift table

| Planned / assumed in earlier migration material | Observed current state | Drift classification | Likely reason, evidenced or inferred |
|---|---|---|---|
| Port GSI’s broad multi-market dashboard to Vercel. | Separate, constrained AlphaVeda product with four research pages. | **Deliberate strategic pivot.** | GSI’s data-freshness/trust constraint led to a smaller promise. |
| Retain GSI dashboard pages: Home, Dashboard, Week Summary, Global Intelligence, Observability. | AlphaVeda offers Market Data, Signals, Path, Accuracy; instrument detail is gated. | **Scope replacement.** | The accuracy ledger and research workflow became the product centre. |
| Use Railway/FastAPI as frontend data source. | Current Next.js pages directly query Supabase server-side; FastAPI exists but is not in the inspected web path. | **Architecture divergence.** | Later design decisions explicitly deferred FastAPI deployment; direct Supabase reduced initial transport scope. |
| Add auth and commercial gate in Session C. | Waitlist table/standalone form and commercial marker exist, but current web users are anonymous and lack a signup route. | **Incomplete planned milestone.** | Landing, privacy, and auth were deferred behind trust/compliance hardening and proof-window sequencing. |
| Introduce persistent forecasts / broad data migration. | AlphaVeda prioritises stored signal outcomes; fundamentals, macro, attribution remain incomplete. | **Prioritisation drift.** | Trust instrumentation was prioritised over breadth and richer context. |
| Complete a 9–10 week GSI cutover. | No evidence of a GSI cutover; root GSI remains Streamlit. | **Not started / superseded for now.** | AlphaVeda is not a technical successor/migration of GSI. |

### 8.4 Drift is not all failure

**Confirmed strategic improvement:** A narrow, auditable EOD signal system with a public ledger is more aligned to the stated trust problem than migrating a broad interface without solving data reliability.

**Real delivery cost:** The repository now contains multiple plans with inconsistent assumptions: shared versus separate Supabase descriptions, Railway/Fly versus direct-Supabase frontend paths, and stale inventory/gap language. That makes it difficult to determine which plan governs new work and increases the risk of implementing the wrong architecture.

---

## 9. Alignment plan

### 9.1 Choose the governing product charter

**Recommendation:** Adopt the following as the current charter until explicitly replaced:

> AlphaVeda is a research-only Indian-equities product. Its MVP proves trustworthy EOD ingest, honest stored signals, visible cold-start restraint, and a public accuracy ledger before it broadens coverage, personalises content, or monetises alerts.

This charter aligns the background briefing, current page design, gap register, and revenue proof window. It does **not** say AlphaVeda is a migration of GSI.

### 9.2 Establish a single current-state scorecard

Maintain one short, dated status document with these rows:

| Area | Required status fields |
|---|---|
| Runtime architecture | deployed frontend, data path, database project, background jobs, current environment. |
| Public pages | route, audience, data tables, required disclaimer, test coverage. |
| Trust gates | ingest freshness, prediction count, resolved outcome count, calibration readiness, stale data. |
| Commercial gates | landing, privacy, auth, waitlist, licensing, delivery provider. |
| Deferred capabilities | fundamentals, macro, attribution, news, portfolios, alerts. |
| Decision log | owner, decision, date, evidence, expiry/review date. |

Any plan older than this scorecard should be marked historical rather than silently treated as implementation guidance.

### 9.3 Measure alignment with outcomes, not feature count

Use a simple scorecard each week:

| Objective | Leading measure | Evidence needed |
|---|---|---|
| Data integrity | consecutive valid trading-day ingests; stale/failed suppressions work. | ingest-status records + tests. |
| Signal honesty | predictions with correct cold-start/no-call handling. | stored records + UI/Playwright checks. |
| Trust | resolved outcomes visible with warning and source/as-of context. | ledger data + rendered-page checks. |
| Subscription readiness | authenticated consented user can manage a research list. | RLS/auth/preference tests. |
| Digest reliability | no duplicate sends; every claim traceable to snapshot. | delivery log + idempotency tests. |
| Product clarity | user can explain “what it is” and “what it is not.” | moderated five-second recall / task test. |

### 9.4 Stop-doing list for alignment

Until the above gates are green, do not:

- expand AlphaVeda to GSI’s nine-market scope;
- add a second scoring framework merely for richer storytelling;
- ship price-trigger or intraday alerts;
- add a portfolio-import claim;
- publish a news-first “daily stock call” page;
- use a waitlist email as though it were a verified subscriber identity;
- start a full GSI migration under the assumption AlphaVeda already completed it.

---

## 10. Decisions requested

1. Approve or reject **research-list email updates** as the subscription v1 scope.
2. Choose whether daily sends should be material-change-only (recommended) or include an explicit no-change digest.
3. Confirm that “portfolio” means a user-curated research list in v1, not connected holdings.
4. Name the accountable owner for privacy/DPDP and commercial data-licensing review.
5. Choose the governing architecture/status document and mark conflicting historic plans accordingly.
6. Decide whether GSI remains an independently maintained Streamlit product or receives a separately funded migration plan.

---

## 11. Recommended immediate next step

Before implementing email or authentication, run one compact design-and-governance session that produces:

- the approved v1 subscription one-pager;
- a privacy/consent and unsubscribe flow diagram;
- the exact event schema and material-change rules;
- current architecture source-of-truth decision;
- a redlined list of historic documents that are superseded, still-active, or uncertain.

That resolves the present ambiguity without committing to irreversible schema, provider, or commercial-data decisions.

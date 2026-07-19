# AlphaVeda — Claude Code Handoff Briefing

**Purpose:** Give Claude Code a safe, evidence-led starting point for AlphaVeda product, UX, and engineering work in this repository.

## 1. Start here

Read these files in order before proposing or changing AlphaVeda work:

1. `AGENTS.md` — repository-wide rules and mandatory regression check.
2. `GSI_GOVERNANCE.md` — data integrity, compliance, freshness, and architecture policy.
3. `alphaveda/web/AGENTS.md` — mandatory Next.js guidance for files under `alphaveda/web/`.
4. `docs/alphaveda/MVP_UX_OPTIONS_AND_DATA_AUDIT_2026-07-19.md` — current page/data inventory and recommended MVP UX direction.
5. `docs/alphaveda/SUBSCRIPTIONS_MIGRATION_ALIGNMENT_PLAN_2026-07-19.md` — proposed research-update subscription model, GSI gap map, drift analysis, and decision gates.
6. `alphaveda/docs/GAP_REGISTER.md` — canonical known gaps and red flags.
7. `alphaveda/docs/MVP_SPEC.md` and `alphaveda/docs/ALPHAVEDA_DESIGN_OVERVIEW.md` — product scope and design intent.
8. `alphaveda/docs/REVENUE_ROADMAP.md` — current proof-window/monetisation sequencing.

Treat older migration briefs and historic session logs as context, not automatically as current implementation authority. Where documents conflict, inspect the current code and state the conflict explicitly.

## 2. Current product framing

AlphaVeda is a research-only Indian-equities product. Its intended MVP is a trust-first research loop:

```text
Market Data → Signals → Path → Accuracy
                     ↘
                Instrument detail (soft-launch)
```

The product should show EOD inputs, stored signal state, risk/position context, and historical outcome evidence. It must not behave like a tip sheet, broker, execution tool, or personalised advice service.

## 3. Current frontend and data boundaries

- Runtime frontend: `alphaveda/web/` (Next.js).
- Primary routes: `/`, `/signals`, `/path`, `/accuracy`.
- Per-instrument route: `/instrument/[ticker]`; it is soft-launch/non-primary and has promotion constraints recorded in G20.
- Current pages use server-side Supabase reads. Do not assume FastAPI/Railway is the live frontend data path without checking current code.
- Market data is EOD-oriented. Do not label it “real-time” or “live” without verified intraday data and timestamps.
- Signal output is stored/read; do not move signal computation into the frontend.

## 4. Non-negotiable safeguards

1. Every signal/action-like surface needs the required SEBI disclaimer and algorithmic-output label.
2. Do not use BUY/SELL/personalised action language.
3. Preserve cold-start/no-call/stale/no-data states; never manufacture certainty with placeholders.
4. Do not present fundamentals, fresh macro, attribution, or a news-led detail view as available while their data gates remain open.
5. Do not expose public rupee sizing; the current Path surface deliberately suppresses it for anonymous/research users.
6. Do not move or duplicate data calculations without maintaining canonical source and freshness disclosure.
7. Do not add personal portfolios, broker connections, price-trigger alerts, or email delivery without explicit product/data-governance approval.

## 5. Subscription work: approved discussion scope versus unapproved implementation

The subscription plan is **decision support only**. The recommended v1 concept is an opt-in email research digest for a user-curated research list, triggered by validated post-ingest material changes. It is not yet an approved schema, provider choice, or delivery implementation.

Before implementing any subscription delivery, require explicit approval for:

- authentication and verified identity;
- privacy/DPDP policy and consent/unsubscribe lifecycle;
- schema migrations and row-level security;
- notification provider and credential handling;
- commercial data-licensing review;
- compliance copy and automated tests.

## 6. Design materials

- `docs/detail-page-layouts/` contains static HTML/CSS prototypes. They are documentation/reference artefacts, not wired application code.
- `docs/india-policy-investment-alphaVeda-design-2026-07-13.md` contains policy-context and detail-page research guidance. It is not a source of live market facts.
- The recommended current direction is “Verified Research Loop.” A newspaper/news-led design is deferred until necessary fundamentals, macro, and attribution data are live and compliant.

## 7. Requested working style

For every task:

1. State the inspected evidence and any conflicts.
2. Separate confirmed facts, recommendations, assumptions, and unresolved questions.
3. Prefer a small reversible change with tests over a broad redesign.
4. Keep new UI bound to actual source fields and show honest failure/freshness states.
5. Before a commit, run `python3 regression.py` and the applicable AlphaVeda/web checks.
6. Do not weaken existing tests merely to pass a change.

## 8. Suggested first prompt for Claude Code

> Read `AGENTS.md`, `GSI_GOVERNANCE.md`, `alphaveda/web/AGENTS.md`, `docs/alphaveda/CLAUDE_CODE_BRIEFING.md`, `docs/alphaveda/MVP_UX_OPTIONS_AND_DATA_AUDIT_2026-07-19.md`, `docs/alphaveda/SUBSCRIPTIONS_MIGRATION_ALIGNMENT_PLAN_2026-07-19.md`, and `alphaveda/docs/GAP_REGISTER.md`. Summarise the current AlphaVeda runtime, its primary routes and data sources, the open data/compliance gates, and the smallest safe next implementation step. Do not modify code until you identify conflicts between current code and historical plans.

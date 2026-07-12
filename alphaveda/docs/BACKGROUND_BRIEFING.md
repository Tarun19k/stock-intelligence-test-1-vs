# AlphaVeda — Background Briefing

Drafted 2026-07-13 by chief-of-staff (Krishna), with commercial framing from the
Wealth & Revenue Strategist doctrine-panel seat. Grounded in this repo's actual git
history and documentation — not an assumed narrative. Where a claim isn't backed by a
file or commit, it's marked as positioning rather than fact.

## Where GSI Dashboard came from

GSI Dashboard is the older of the two products — first commit 2026-03-13. It's a broad
Streamlit screener: 9 markets, 559 tickers, 38 groups, a 4-tab dashboard. The intent,
per `GSI_SPRINT.md`'s own CEO sign-offs (2026-04-01), was a general-purpose global
intelligence tool heading toward a ₹399/month subscription (GSI Standard), positioned
as a flanking play against Screener.in (₹600-1200/month).

That subscription path has never converted, and the sprint history shows why: `v5.41 —
Trust Restoration` (2026-05-17) exists because the live app was showing wrong data —
crude WTI at ~$99 when the real price was ~$60, among other data-freshness defects. The
product's constraint hasn't primarily been breadth or feature count. It's been keeping
559 tickers across 9 markets accurate enough, continuously, for a stranger to trust
enough to pay. `OPEN-003` (Supabase persistence, still blocking the subscription
gateway) compounds this, but isn't the root constraint — the root constraint is trust.

## Why AlphaVeda exists

AlphaVeda's first commit (2026-06-23) describes itself as a deliberately separate
build: its own `alphaveda/` subdirectory, explicitly planned to "extract to standalone
repo at first subscriber." It does not share GSI's codebase, database, or frontend.
Nothing in this repo's ADR log (`GSI_DECISIONS.md`) formally connects the two products.

What AlphaVeda changes, concretely:
- **One market, one signal** — India equities only, a single momentum signal, instead of
  9 markets and dozens of indicators
- **A public, permanent accuracy ledger** — every call is recorded and graded against
  real outcomes, visible to anyone, with an honest past-performance disclaimer
- **SEBI-safe language throughout**, dual disclaimer (plain-language + legal) on every
  page, cold-start honesty (won't display a confidence figure until it's earned)
- **Its own infrastructure** — separate Supabase project, separate Vercel deployment —
  so GSI's existing technical debt (OPEN-003, the trust-restoration backlog) doesn't
  carry over by default

This is the strategic core of it, confirmed by the Wealth & Revenue Strategist review:
GSI's problem was never really "not enough breadth" — it was that a 559-ticker surface
gives a stranger 559 chances to catch you being wrong, and that happened. AlphaVeda
shrinks the promise to something small enough to keep, and makes the keeping of it
publicly verifiable by design. Prove trustworthiness at small scope before asking
anyone to pay for breadth again.

## What "successor" honestly means here — and what it doesn't

**Accurate framing:** same founder, same underlying market thesis (retail India
investors underserved by both free tools and expensive advisors), a deliberately
smaller and stricter second attempt at earning trust after the first attempt's
data-accuracy problems.

**Not accurate, and should not be claimed:** that AlphaVeda is a technical upgrade or
migration of GSI's code, that existing GSI users automatically become AlphaVeda users,
or that AlphaVeda shortens GSI's own path to revenue. The two products share no
infrastructure, no user base, and no code lineage. "Successor" is a strategic and
narrative choice, not a technical one — the briefing exists to state that plainly
rather than let the two get conflated.

## Current state (as of this session)

AlphaVeda is live at `https://stock-intelligence-test-1-vs.vercel.app` (4 routes: `/`,
`/signals`, `/path`, `/accuracy`), SEBI-compliant, retail-language-ready (33/33 CI
tests passing), but currently showing no live signal data — the daily ingest pipeline
has had reliability problems since 2026-07-01, being actively fixed this session
(two real defects found and closed: no horizon-maturity gate, no missed-run alert).
GSI remains blocked on `OPEN-003` with no active sprint (`v5.42 — Planning`, target
date TBD).

Per Tarun's own framing (2026-07-12): this isn't a race against a literal 21-day
revenue deadline — it's the start of a council-planned revenue roadmap that AlphaVeda's
MVP-then-UAT path is meant to anchor. That roadmap has not been drafted yet (tracked
separately).

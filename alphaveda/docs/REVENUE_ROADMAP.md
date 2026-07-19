# AlphaVeda — Revenue Roadmap

Council-synthesized 2026-07-13. Signed off by Tarun same day. 5 seats ran (Buffett,
Munger, Lynch, Wealth & Revenue Strategist, Constraint Enforcer). Synthesis Chair was
deliberately skipped — the council converged with no real disagreement to arbitrate,
per Constraint Enforcer's own trim recommendation (avoid an Opus-tier pass with nothing
to resolve).

## ⚠ AMENDMENT — 2026-07-17: both tracks confirmed, sequenced

This document's public waitlist → proof-window → paid-subscriber funnel was written by
the financial council without ever being told about a second, coexisting model: AlphaVeda
also becomes a **private freelance-client dashboard** — Tarun uses it personally first,
then shows it to his own consulting clients (Stream C) — separate from the public
subscriber funnel below (Stream D). Both are real; found genuinely inconsistent with
zero prior written record of the private track until Tarun stated it directly on
2026-07-17. Root cause + investigation: see `agentic-operations/graphify-out/SESSION_RESUME.md`
2026-07-17 entry.

**Confirmed, Tarun's own words, 2026-07-17:**
1. **Sequencing: private first.** Tarun uses AlphaVeda personally, builds trust, then
   shows consulting clients. The public waitlist track below is **PAUSED**, not
   cancelled — resumes once the private trust gate (below) closes.
2. **Commercial trigger: unchanged.** `is_commercial()` stays tied solely to
   `waitlist.converted_at` — a consulting client viewing a demo does NOT trigger
   commercial=True. Tarun controls what a client sees directly, same as the operator
   view. No code change needed.
3. **Landing page (NG-5/G8): PAUSED.** Not the near-term build priority. Revisit once
   the private trust gate closes.
4. **Private trust gate — BOTH conditions, whichever takes longer:**
   - The existing proof-window criteria (10 consecutive clean ingest days, ≥15 resolved
     signals) — already defined below, unchanged
   - Tarun's own subjective confidence in the tool, independent of the ledger stats

**What this means for near-term build priority:** ingest reliability (Task D) and
signal-quality trust items (Wilson CI display, methodology log) now matter MORE, not
less — they're what the private trust gate is actually measured against. The landing
page items (NG-5, G8) drop out of the near-term sequence entirely until the gate closes.

## Day 0 = 2026-07-13

## The proof window (the core mechanism)

**3 calendar weeks from Day 0, OR 15 resolved signals on `/accuracy` — whichever comes
first.** Exit requires all 4 criteria, no partial credit:

1. Zero data-integrity bugs across 10 consecutive trading days of GHA ingest runs. Any
   bug found resets *this counter only* (not the calendar window). Max 2 resets — on
   the 3rd bug-triggered reset, hard stop: ship the paid tier anyway with a visible
   "ledger still building" disclaimer rather than pushing the date again.
2. ≥15 signals reach resolution status (win or loss recorded) on `/accuracy`.
3. Ledger publishes as-is, regardless of win rate — the gate is transparency + volume,
   never a minimum win rate. Do not add a profitability condition later; that reopens
   the infinite goalpost this whole mechanism exists to prevent.
4. Landing page + waitlist are live and capturing signups before the window closes.

When the gate clears (or the hard stop triggers): launch the first paid ask that same
week, at a price-anchor locked now — entry tier at/below GSI's ₹399/month reference
point, Pro tier at 2-3x entry. The range is decided today and not renegotiated
reactively once real ledger numbers are in (same discipline applied to price as to the
launch date itself).

## PENALTY — 2026-07-14: +72 hours added to all commercial gates

**Cause:** the `ingest.yml` scheduled trigger (`schedule:` cron) has a 100% late/no-show
rate across all 9 recorded runs (2026-07-01 → 07-13) — every scheduled fire was 2-3
hours late, and 2026-07-14 produced zero run record at all as of 13:59 UTC. This was
not caught proactively — it surfaced only when Tarun asked directly why today's ingest
hadn't shown up. There was also no fallback mechanism (no external trigger, no
timing-alert) to catch a late/missing scheduled run independent of the watchdog, which
itself only checks 2 hours after the intended fire time.

**Tarun's ruling:** this is a real system miss — caught late, no fallback existed. +72
hours added to all commercial gates in this roadmap (the proof window's calendar
deadline and any gate depending on it) as a standing penalty, separate from and
additional to the existing "max 2 resets" mechanic in the proof window above. This does
NOT reset the 10-consecutive-clean-days counter itself (that mechanic is unchanged) — it
extends the calendar-side deadline only.

**Required going forward:** a genuine fallback for trigger-timing failures, not just
data-integrity failures — see the hybrid-fix action plan (strategic-analysis, 2026-07-14)
for the concrete fix. Do not consider this penalty closed until that fallback is live
and observed working for real, not just designed.

## Why this exists (Buffett + Munger, converging from different angles)

Buffett: the public accuracy ledger is AlphaVeda's only real moat-seed today, and it's
currently empty — no live signal data has accumulated yet. A moat has to be *proven*,
not asserted; an open-ended "prove trust" period doesn't prove anything by itself.

Munger: "prove trust before monetizing" has no natural stopping condition for a solo
operator — there's always one more bug to fix, one more day to wait. This is the exact
pattern that left GSI subscription-blocked for months. The only fix is a stopping
condition decided *before* anyone knows whether the numbers will look good — which is
what the 4 criteria above are.

## What was trimmed (Constraint Enforcer)

- Munger also flagged the single-founder/single-signal/single-market setup as a
  structural risk, and proposed adding a non-Tarun verification step (e.g. automated
  second-source price reconciliation) to reduce it. **Deferred to v2** — do not let it
  push back Day 0 of the clean-run counter above.
- 4 parallel Sonnet-tier council seats + this synthesis for what is ultimately a
  one-page decision was flagged as borderline overbuilt. Noted for future roadmap
  work: a single strategic pass + one lightweight constraint check likely suffices
  when the council is expected to converge rather than conflict.
- Synthesis Chair skipped — see above.

## Customer persona (Lynch — stated as an informed guess, not researched)

First customer: the existing DIY Zerodha/Groww retail trader who already pays for
other research tools (Tijori, TradingView, tip Telegram channels) and is burned by
influencer calls with no track record. Their pain isn't lack of information — it's not
knowing whose information to trust. This has not been validated with real users yet.

AlphaVeda classifies as a "stalwart-in-waiting," not a "fast grower" — slow, trust-first
pacing is correct; racing to add markets/signals/discounts would repeat GSI's failure
mode. The Simple/Pro language toggle is table-stakes now (most fintech has this), not
the real differentiator — the accuracy ledger is the actual edge, and should be the
entire pitch once it has something to show.

## Sequencing decision (Tarun, 2026-07-13)

Landing page (NG-5) and waitlist route (G8) — needed to start the proof-window clock —
were flagged by Constraint Enforcer as directly competing with Stream A (Agentic Ops
digital product, already overdue) for the same calendar hours, even though they don't
compete for the same revenue line. **Tarun's call: AlphaVeda first, this week.** Stream
A remains overdue a while longer by explicit choice, not oversight.

## This week's actions

1. Build landing page (NG-5) + waitlist route (G8) — starts the proof-window clock for
   real once live and capturing signups.
2. Nothing else on the AlphaVeda roadmap is time-critical this week — the 10-day clean
   ingest counter and 15-signal accumulation run on their own schedule once the
   pipeline (already live-tested this session) keeps working.

## Explicitly not in scope for the 21-day window

AlphaVeda produces ₹0 by design inside the literal 21-day period — the Wealth & Revenue
Strategist review was explicit about this: it's pipeline, not cash. Streams A and C
remain the only things that can produce real revenue inside that window. This roadmap
governs when AlphaVeda's OWN monetization clock starts, which by design lands at or
after day 21, not before.

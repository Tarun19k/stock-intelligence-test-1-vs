# ADR-002: OHY UI Sequencing Gate — No Screens Before the Ledger

**Status:** Accepted (2026-07-30)
**Related commits:** `febd9a5` (holdings migration), `dd460f1` (build-checklist dashboard)

## Context

Two independent reviews in one session (a retail-UX/compliance council pass and a Dronacharya
skill-gap audit) converged on the same finding: OHY UI mockups (Portfolio Health, Trigger
Explanation) were built against portfolio data that had no schema to back it — no
`holdings`/`positions` table existed anywhere in AlphaVeda's database. Root cause, in Trimurti
terms: Brahma (creation) ran ahead of Vishnu (integration/preservation check) and Shiva
(adversarial verification) — the exact anti-pattern the framework in `docs/trimurti/framework.md`
exists to prevent.

## Decision

No further OHY UI screens (Screen 2 onward, per the source's 9-screen plan) are built until:
1. The `holdings` table exists with real schema (done, migration `20260730132148_holdings_ledger.sql`).
2. Real portfolio data is populated (open — blocked on Tarun's real holdings values).
3. A reconciliation test (Shiva pass) confirms the ledger matches reality.

Existing mockups (Screens 1 and 4) remain explicitly labeled "MOCKUP — illustrative" and are not
treated as Phase D diagnostics until this gate clears.

## Consequences

- OHY product work this session redirected from "more screens" to "close the data gap" —
  `financial-data-viz/SKILL.md`'s Portfolio Ledger Distinction section (added 2026-07-30) now
  enforces this check for future dispatches.
- This ADR is itself an instance of the source material's own Phase C gate: "Synthetic golden
  portfolios reconcile exactly to approved expected outputs" must pass before Phase D.

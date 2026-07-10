# AlphaVeda — Gap Register
# Canonical, durable list of known gaps and red flags. Update in place as items close.
# Source: converged loop-engineered audit (2026-07-09) + Fable-tier round table (2026-07-10)
# Do not let this file go stale — it is the single source of truth for "what's known broken/missing."

Status legend: `OPEN` · `IN PROGRESS` · `CLOSED` (with commit/date)

---

## Red Flags (RF) — financial/compliance correctness

| ID | Description | Status | Note |
|---|---|---|---|
| RF-A | Marketing copy ("seven doctrines, one calibrated signal") overstates actual single-signal capability | CLOSED — non-issue | Confirmed: overclaiming text only exists in the design catalog mock, never shipped to the live site. Real deployed copy is honest. |
| RF-B | `emit_signal()` confidence floor produced incoherent sub-50% directional verdicts | **CLOSED 2026-07-10** | Fixed (`edb8d01`), verified live in production: 10 real predictions, natural confidence 18–50%, no floor artifacts |
| RF-C | Kelly sizing appeared "dead" at low confidence | CLOSED — was never a bug | Zero-sizing on low-confidence signals is correct Kelly discipline; root cause was RF-B, now fixed |
| RF-D | SEBI disclaimer text disagreed across 3 documents | **OPEN — now 4-way, sharpened** | See NG-4 below — disclaimer sourced from a Vercel env var, mutable without code review |
| RF-E | Hardcoded Nifty 22000/20000 fabricating `cycle_phase` on every prediction | OPEN | Not yet addressed |
| RF-F | `horizon_days=1` vs council's T+5 ruling — undocumented deviation | OPEN | MVP-acceptable, needs explicit documentation as a conscious deviation |

## Gaps (G) — structural/infrastructure

| ID | Description | Status | Note |
|---|---|---|---|
| G1 | `fundamentals` table empty — BSE XBRL parser built, never scheduled | OPEN | Tier 5, A19 |
| G2 | `macro_regime` — was 0 rows, now 1 manual row | OPEN — stale | Already stale by system's own 3-day rule; see G13 |
| G3 | Simple/Pro language layer, glossary, lexicon exist only in design catalog — zero wired into build | OPEN — Tier 3 core work | A10–A14; direction-agnostic, doesn't need design pick first |
| G4 | Landing page + waitlist signup — catalog mock only, no route exists | OPEN | Tier 2, A7–A9 |
| G5 | Attribution schema (`prediction_components`) missing — blocks per-signal RCA | OPEN | Needed before Loop 3 |
| G6 | Kelly sizing runs on hardcoded `PORTFOLIO_VALUE=725000`, not real holdings | OPEN | Also NG-2 (public display issue) |
| G7 | Warm calibration (Platt scaling) is placeholder — cold-start path only | OPEN — bridged by A4 | COLD-gating (A4) is the honest interim; A21 is the real fix, deferred to Loop 3 window |
| G8 | Commercial gate (`waitlist.converted_at`) structurally unreachable — no waitlist route | OPEN | Tier 2, A7 |
| G9 | Designed product ≠ deployed product (design catalog, direction, Simple/Pro all unwired) | OPEN | A0c (Tarun) + A10–A15 |
| G10 | No privacy/DPDP policy — required before any waitlist collects emails | OPEN | Tier 2, A8, ships with A7 not after |
| G11 | No missed-run watchdog for silent GHA cron failures | **CLOSED 2026-07-10** | `ingest-watchdog.yml` built and committed (`83355fe`) |
| G12 | Jul 2→9 ingest health unverified | **CLOSED 2026-07-10** | Root cause found (24 unpushed commits) and resolved; RF-B live-verified |
| G13 | `macro_regime` stale by the system's own `REGIME_STALENESS_DAYS=3` rule | OPEN | Tier 5, A18 |
| G14 | Cold-start segment threshold (30 obs) has no scheduled backfill path | OPEN | Blocked behind G5 (attribution migration) |
| G15 | Two presentation layers coexist (Streamlit `src/pages/` + Next.js) — dead weight | OPEN | Needs formal deprecation marker |
| G16 | Zero production observability — no error monitoring, uptime check, or analytics | OPEN | Not yet tiered |
| G17 | Governance promises uncoded (Rule D/E, GraphRAG-first enforcement) | OPEN | Tier 5, A22 |

## New Gaps (NG) — found by the 2026-07-10 round table, not in the original G1–G17 list

| ID | Description | Status | Note |
|---|---|---|---|
| NG-1 | Accuracy page lacks past-performance disclaimer; downside metrics lack risk note | OPEN | Tier 1, A3 |
| NG-2 | Public unauthenticated Path page shows Tarun's personal ₹ Kelly amounts (from hardcoded `PORTFOLIO_VALUE`) | OPEN | Tier 1, A5 — confirmed via direct code read, `path/page.tsx:134` |
| NG-3 | Operator-facing language leaks into public empty/error states (e.g. "Run the daily ingest pipeline") | OPEN | Tier 1, A6 |
| NG-4 | SEBI disclaimer sourced from `process.env.SEBI_DISCLAIMER` — mutable via a Vercel env edit with zero code review, violating the documented hardcoding standard | OPEN | Tier 1, A2 — confirmed via direct code read, `SebiDisclaimer.tsx:5` |
| NG-5 | No what/why/trust story exists anywhere for a first-time visitor — landing is a raw data table | OPEN | Tier 2, A9 |

---

## Closure summary (2026-07-10)

- **6 of 23 items now CLOSED**: RF-A (non-issue), RF-B (fixed + live-verified), RF-C (was never a bug), G11 (watchdog built), G12 (root cause resolved)
- **17 OPEN**, prioritized into Tiers 1–5 — see `alphaveda/docs/plans/LOOP_ENGINEERED_ROADMAP.md` Progress Log and `graphify-out/SESSION_RESUME.md` for the full tiered action plan and round-table synthesis
- Update this file directly as items close — do not let findings live only in session transcripts again

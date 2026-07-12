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
| G4 | Landing page + waitlist signup — catalog mock only, no route exists | **IN PROGRESS 2026-07-13** | Tier 2, A7–A9. Same as G8/NG-5 — now gated by REVENUE_ROADMAP.md's proof window (Day 0 = 2026-07-13); Tarun explicitly sequenced this ahead of Stream A this week |
| G5 | Attribution schema (`prediction_components`) missing — blocks per-signal RCA | OPEN | Needed before Loop 3 |
| G6 | Kelly sizing runs on hardcoded `PORTFOLIO_VALUE=725000`, not real holdings | OPEN | Also NG-2 (public display issue) |
| G7 | Warm calibration (Platt scaling) is placeholder — cold-start path only | OPEN — bridged by A4 | COLD-gating (A4) is the honest interim; A21 is the real fix, deferred to Loop 3 window |
| G8 | Commercial gate (`waitlist.converted_at`) structurally unreachable — no waitlist route | OPEN | Tier 2, A7 |
| G9 | Designed product ≠ deployed product (design catalog, direction, Simple/Pro all unwired) | OPEN | A0c (Tarun) + A10–A15 |
| G10 | No privacy/DPDP policy — required before any waitlist collects emails | OPEN | Tier 2, A8, ships with A7 not after |
| G11 | No missed-run watchdog for silent GHA cron failures | **CLOSED 2026-07-10, alert-wiring added 2026-07-12** | `ingest-watchdog.yml` built and committed (`83355fe`). SRE council review 2026-07-12 found the watchdog detected misses but produced no human-reaching alert (only a failed job in the Actions tab) — this repo has no email/Slack secrets configured (`gh secret list` confirms only SUPABASE_URL/SUPABASE_SERVICE_KEY exist). Fixed by opening a GitHub Issue on failure via `actions/github-script` (no new secret needed, GITHUB_TOKEN is automatic). |
| G12 | Jul 2→9 ingest health unverified | **CLOSED 2026-07-10** | Root cause found (24 unpushed commits) and resolved; RF-B live-verified |
| G13 | `macro_regime` stale by the system's own `REGIME_STALENESS_DAYS=3` rule | OPEN | Tier 5, A18 |
| G14 | Cold-start segment threshold (30 obs) has no scheduled backfill path | OPEN | Blocked behind G5 (attribution migration) |
| G15 | Two presentation layers coexist (Streamlit `src/pages/` + Next.js) — dead weight | OPEN | Needs formal deprecation marker |
| G16 | Zero production observability — no error monitoring, uptime check, or analytics | OPEN | Not yet tiered |
| G17 | Governance promises uncoded (Rule D/E, GraphRAG-first enforcement) | OPEN | Tier 5, A22 |

## New Gaps (G18-G20)

| ID | Description | Status | Note |
|---|---|---|---|
| G20 | No per-instrument "stock detail" page — all 4 live routes (/, /signals, /path, /accuracy) are flat lists across every tracked instrument; nothing lets a user drill into ONE stock's consolidated signal/sizing/accuracy view. Codex's independent design doc also missed this page type. | **IN PROGRESS 2026-07-13 — MVP via Codex, soft-launch only** | Full page still gated (see original gate below). MVP round 2 council (Buffett/Munger/SRE/Constraint Enforcer/Lynch + Synthesis Chair) approved a narrower MVP: live price + current signal + lynch_class badge + live-computed "X of 20 signals graded" note + a mandatory non-removable watchlist/aggregate strip (Munger's structural safeguard against standalone-screenshot misuse — resolves his dissent by design, not by launch-gating alone). Conditions: preview/branch link only, NOT linked from primary nav, NOT merged to production nav until landing page/waitlist ships, not promoted externally, read-only build isolated from ingest, scope locked to exactly 5 elements before Codex starts. Munger's residual-risk note preserved: if the MVP is ever screenshotted/forwarded as a standalone call even in soft-launch, his original NO becomes binding and it reverts to password-gated preview or full defer. Graduation to promoted/linked page requires the ORIGINAL gate (≥20 resolved signals/2 categories or 7 days clean ingest) AND ≥1 week of the watchlist-strip element live with no misuse incident. |

## New Gaps (G18-G19) — found by calibration-integrity council review, 2026-07-12 (forecast model solidification plan)

| ID | Description | Status | Note |
|---|---|---|---|
| G18 | No horizon-maturity gate — `ingest.py` Step 5 resolves ALL open predictions against the current run's OHLCV regardless of elapsed time since `emitted_at`, with no check that `horizon_days` has actually elapsed. Additionally, no terminal-resolution check existed at all: `accuracy_outcomes`' unique constraint is on `(prediction_id, resolved_at)` not `prediction_id` alone, so every ingest run re-resolved every open prediction, appending a new outcome row each day with that day's price — a prediction could accumulate a different hit/miss verdict on different days indefinitely. | **CLOSED 2026-07-12** | Fixed directly in `ingest.py` Step 5: added a horizon-maturity filter (`target_date >= emitted_at + horizon_days`) and a terminal-exclusion filter (skip any prediction_id already present in `accuracy_outcomes`). Syntax-verified (`py_compile`); not yet exercised against a real ingest run — that verification rides with the existing ingest-reliability verification already tracked. |
| G19 | Cold-start denominator mismatch — `engine.py` computes `segment_obs` (which gates `calibrate_confidence()`) **per instrument_id**; the UI's cold-start banner (`signals/page.tsx`, `OBSERVATION_THRESHOLD=30`) gates display on counts pooled by `(lynch_class, regime)` across many tickers. A pooled segment can cross 30 observations (UI shows "warm") while any individual instrument inside it is still near-zero in the actual per-instrument calibration math. Users see a false "no longer cold start" signal. | OPEN | P1 — either compute `segment_obs` in `engine.py` per `(lynch_class, regime)` to match the UI's own promise, or change the UI to show per-instrument readiness instead |

## New Gaps (NG) — found by the 2026-07-10 round table, not in the original G1–G17 list

| ID | Description | Status | Note |
|---|---|---|---|
| NG-1 | Accuracy page lacks past-performance disclaimer; downside metrics lack risk note | **CLOSED 2026-07-12** | `593394c` (A3) |
| NG-2 | Public unauthenticated Path page shows Tarun's personal ₹ Kelly amounts (from hardcoded `PORTFOLIO_VALUE`) | **CLOSED 2026-07-12** | `cb51449` (A5) — fail-closed `isPersonalContext()` gate |
| NG-3 | Operator-facing language leaks into public empty/error states (e.g. "Run the daily ingest pipeline") | **CLOSED 2026-07-12** | `b0e0c07` (A6) |
| NG-4 | SEBI disclaimer sourced from `process.env.SEBI_DISCLAIMER` — mutable via a Vercel env edit with zero code review, violating the documented hardcoding standard | **CLOSED 2026-07-12** | `f307967` (A2) — now generated from `constants.py` at build time, CI drift test added |
| NG-5 | No what/why/trust story exists anywhere for a first-time visitor — landing is a raw data table | OPEN | Tier 2, A9 — not yet built |
| NG-6 | (found by A12's CI suite) SEBI_PLAIN dual-disclaimer line exported but never rendered — R11's "dual SEBI in both modes" requirement unmet | **CLOSED 2026-07-12** | `6c7ed11` |
| NG-7 | (found by A12's CI suite) 4 hardcoded jargon leaks in Simple mode: "Accuracy Ledger"/"Hit Rate" (Accuracy), "Kelly-based"/"Quarter Kelly" (Path), "COLD START"/"Bayesian prior weights" (Signals), "hit rate" inside the NG-1 disclaimer text | **CLOSED 2026-07-12** | `6c7ed11` — all wired through the A10 lexicon |

## Tier 3 (A10–A14) — CLOSED 2026-07-12

Full plain-language persona layer built, verified, and CI-guarded: lexicon string architecture (A10), tap-to-learn glossary (A11), language test suite ported into CI — `alphaveda/web/tests/language.spec.ts`, 33/33 passing (A12), held-position directive-reading fix (A13), anchoring counter (A14). See `graphify-out/SESSION_RESUME.md` for the full build history including one recovered crashed-agent commit (A14) and one caught+fixed false-positive test bug.

---

## Closure summary (2026-07-10)

- **6 of 23 items now CLOSED**: RF-A (non-issue), RF-B (fixed + live-verified), RF-C (was never a bug), G11 (watchdog built), G12 (root cause resolved)
- **17 OPEN**, prioritized into Tiers 1–5 — see `alphaveda/docs/plans/LOOP_ENGINEERED_ROADMAP.md` Progress Log and `graphify-out/SESSION_RESUME.md` for the full tiered action plan and round-table synthesis
- Update this file directly as items close — do not let findings live only in session transcripts again

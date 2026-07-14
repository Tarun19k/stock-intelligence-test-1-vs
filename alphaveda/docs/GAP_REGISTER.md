# AlphaVeda — Gap Register
# Canonical, durable list of known gaps and red flags. Update in place as items close.
# Source: converged loop-engineered audit (2026-07-09) + Fable-tier round table (2026-07-10)
# Do not let this file go stale — it is the single source of truth for "what's known broken/missing."

Status legend: `OPEN` · `IN PROGRESS` · `CLOSED` (with commit/date)

---

## G22 (new, closed same-day) — the real ingest blocker

| ID | Description | Status | Note |
|---|---|---|---|
| G22 | `accuracy_outcomes` has 3 live NOT NULL columns (`outcome_date`, `actual_direction`, `is_correct`) that Step 6's upsert never populated — every real scheduled ingest run since G18 shipped failed on the first resolved-outcome row, resetting `REVENUE_ROADMAP.md`'s clean-run counter to 0 each time. Confirmed via `information_schema` query 2026-07-13, not assumption. | **CLOSED 2026-07-13** | `e251359` — `resolve_outcomes_from_ohlcv()` now returns `actual_direction`; `ingest.py` Step 6 upserts `outcome_date`/`is_correct`/`actual_return` alongside existing fields. No schema change — columns already existed live. Verified end-to-end: re-triggered ingest for 2026-07-13, confirmed `status: OK`, `outcomes_resolved: 10`, zero errors (run `29273458980`). **This is Day 1 of the clean-run counter, not Day 0 — today's first scheduled run failed before this fix landed.** |
| G23 | `ingest.yml`'s native GHA `schedule:` trigger has a 100% late/no-show rate: all 9 recorded scheduled runs (2026-07-01→07-13) fired 2-3 hours late, and 2026-07-14 produced ZERO run record at all as of 14:20 UTC (81 min past the intended 13:00 UTC fire time). Root cause per SRE review: too large/consistent a delay to be normal GHA queue jitter; cron fires at `:00`, GitHub's own documented worst-case minute, but that alone doesn't explain a multi-hour pattern. No fallback existed to catch a late/missing scheduled run independent of the watchdog (which itself only checks 2h after the intended time). | **OPEN — penalized (+72h, `REVENUE_ROADMAP.md`), fix designed not yet built** | Hybrid fix approved in principle (external trigger — evaluating claude.ai `RemoteTrigger`/Routines over cron-job.com — as primary, GHA `schedule:` demoted to backup, idempotency guard added to `ingest.py`). **Blocked on the new Layer 1.5 Pre-Execution Scrutiny Gate — requires variational test evidence (happy path + ≥2 failure scenarios, real output shown) before this can be built, per Tarun's 2026-07-14 governance mandate.** |

---

## Red Flags (RF) — financial/compliance correctness

| ID | Description | Status | Note |
|---|---|---|---|
| RF-A | Marketing copy ("seven doctrines, one calibrated signal") overstates actual single-signal capability | CLOSED — non-issue | Confirmed: overclaiming text only exists in the design catalog mock, never shipped to the live site. Real deployed copy is honest. |
| RF-B | `emit_signal()` confidence floor produced incoherent sub-50% directional verdicts | **CLOSED 2026-07-10** | Fixed (`edb8d01`), verified live in production: 10 real predictions, natural confidence 18–50%, no floor artifacts |
| RF-C | Kelly sizing appeared "dead" at low confidence | CLOSED — was never a bug | Zero-sizing on low-confidence signals is correct Kelly discipline; root cause was RF-B, now fixed |
| RF-D | SEBI disclaimer text disagreed across 3 documents | **OPEN — now 4-way, sharpened** | See NG-4 below — disclaimer sourced from a Vercel env var, mutable without code review |
| RF-E | Hardcoded Nifty 22000/20000 fabricating `cycle_phase` on every prediction | OPEN — corrected scope 2026-07-13 | **Was NOT "wire existing data" as earlier assumed — verified live: `macro_regime` table has no `nifty_close`/`nifty_200ma` columns (real schema: id/regime_date/regime/rbi_rate/usd_inr/nifty_vix/fii_flow_cr/notes/updated_at), and no Nifty index ingest path exists anywhere in `src/ingest/`. `derive_cycle_phase()` (src/accuracy/cycle_phase.py) only needs ONE boolean (`nifty_close > nifty_200ma`) — not precise values. Correct fix: add a manually-maintained `above_200ma` boolean to `macro_regime`, same manual-seed pattern already used for `regime`/`nifty_vix`/`notes` — not a new automated ingest pipeline. Claude-owned (needs a live market fact + a schema decision, not Codex-dispatchable with the old premise).** |
| RF-F | `horizon_days=1` vs council's T+5 ruling | **CLOSED 2026-07-13 — documented as a conscious deviation, not fixed** | Confirmed still hardcoded at `engine.py:228`. Kept at T+1 for MVP: the council's original T+5 ruling assumed a mature multi-signal system; the live single-momentum-signal engine (RF-B/RF-C fixed) tests directional edge on the *shortest* honest horizon first — T+1 is the strictest test of whether the signal has any real edge at all before extending the claim to T+5. Revisit alongside G7 (real calibration) and G5 (attribution schema) once ≥30 obs/segment exist — extending horizon prematurely would let a same-day-noise signal claim a 5-day track record it hasn't earned. G18's horizon-maturity gate (closed 2026-07-12) already respects whatever `horizon_days` is set to, so widening it later needs no pipeline change, only this constant. |

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
| G15 | Two presentation layers coexist (Streamlit `src/pages/` + Next.js) — dead weight | **CLOSED 2026-07-13** | Added prominent deprecation markers to every file in `alphaveda/src/pages/`, identifying `alphaveda/web/` as the canonical production presentation layer. Files were **not deleted** and are retained for reference/rollback only. |
| G16 | Zero production observability — no error monitoring, uptime check, or analytics | OPEN | Not yet tiered |
| G17 | Governance promises uncoded (Rule D/E, GraphRAG-first enforcement) | OPEN | Tier 5, A22 |

## New Gaps (G18-G21)

| ID | Description | Status | Note |
|---|---|---|---|
| G21 | "Newspaper-style" one-page infographic expansion of the instrument page (all data + global/non-global news, daily-updating) — requested by Tarun 2026-07-13. 4-seat financial council (Buffett, Munger, Dalio, Lynch, all Rule-A-compliant per COUNCIL_RULES.md) converged: the ask is sound in concept but **cannot honestly ship as "all data, daily" today** — two of its four data layers don't exist yet. | **OPEN — staged, not started** | **Convergent finding across seats:** Dalio directly verified `macro_regime` table exists in schema but is empty (`src/data/regime.py`/`tests/test_regime.py` confirm no seed rows) — same root cause as G13. Buffett's fundamentals layer (5yr trend, ROE/ROCE, debt, promoter pledge, FCF-vs-profit) depends on G1 (BSE XBRL parser built, never scheduled) — also empty. Munger flags a NEW psychological risk distinct from G20's aggregate-strip safeguard: bold newspaper-style headline typography creates hot-tip psychology even with disclaimers present (authority + recency + halo bias reinforcing) — needs its own guardrails (news subordinate position always, cap to 3 items ranked by relevance not recency, no headline stronger than source). Lynch's content (plain-English company description, retail-relabeled `lynch_class` story, 3-question self-verification checklist, news include/exclude filter) is the ONE layer buildable today with zero new data pipeline — reuses existing fields, no ingest dependency. **Recommended stage order: (1) Lynch content layer first — real value, zero new infra; (2) Munger's guardrails apply structurally as soon as any news section exists, not deferred; (3) Buffett's fundamentals layer waits on G1; (4) Dalio's macro layer waits on macro_regime ingest (G13) — label as "Coming — pending live data feed" rather than faking freshness on a null table, per Dalio's explicit hedge.** No Synthesis Chair dispatched — 4 seats agreed on substance, disagreement was staging only, resolved above. |
| G20 | No per-instrument "stock detail" page — all 4 live routes (/, /signals, /path, /accuracy) are flat lists across every tracked instrument; nothing lets a user drill into ONE stock's consolidated signal/sizing/accuracy view. Codex's independent design doc also missed this page type. | **IN PROGRESS 2026-07-13 — MVP via Codex, soft-launch only** | Full page still gated (see original gate below). MVP round 2 council (Buffett/Munger/SRE/Constraint Enforcer/Lynch + Synthesis Chair) approved a narrower MVP: live price + current signal + lynch_class badge + live-computed "X of 20 signals graded" note + a mandatory non-removable watchlist/aggregate strip (Munger's structural safeguard against standalone-screenshot misuse — resolves his dissent by design, not by launch-gating alone). Conditions: preview/branch link only, NOT linked from primary nav, NOT merged to production nav until landing page/waitlist ships, not promoted externally, read-only build isolated from ingest, scope locked to exactly 5 elements before Codex starts. Munger's residual-risk note preserved: if the MVP is ever screenshotted/forwarded as a standalone call even in soft-launch, his original NO becomes binding and it reverts to password-gated preview or full defer. Graduation to promoted/linked page requires the ORIGINAL gate (≥20 resolved signals/2 categories or 7 days clean ingest) AND ≥1 week of the watchlist-strip element live with no misuse incident. |

## New Gaps (G18-G19) — found by calibration-integrity council review, 2026-07-12 (forecast model solidification plan)

| ID | Description | Status | Note |
|---|---|---|---|
| G18 | No horizon-maturity gate — `ingest.py` Step 5 resolves ALL open predictions against the current run's OHLCV regardless of elapsed time since `emitted_at`, with no check that `horizon_days` has actually elapsed. Additionally, no terminal-resolution check existed at all: `accuracy_outcomes`' unique constraint is on `(prediction_id, resolved_at)` not `prediction_id` alone, so every ingest run re-resolved every open prediction, appending a new outcome row each day with that day's price — a prediction could accumulate a different hit/miss verdict on different days indefinitely. | **CLOSED 2026-07-12** | Fixed directly in `ingest.py` Step 5: added a horizon-maturity filter (`target_date >= emitted_at + horizon_days`) and a terminal-exclusion filter (skip any prediction_id already present in `accuracy_outcomes`). Syntax-verified (`py_compile`); not yet exercised against a real ingest run — that verification rides with the existing ingest-reliability verification already tracked. |
| G19 | Cold-start denominator mismatch — `engine.py` computes `segment_obs` (which gates `calibrate_confidence()`) **per instrument_id**; the UI's cold-start banner (`signals/page.tsx`, `OBSERVATION_THRESHOLD=30`) gates display on counts pooled by `(lynch_class, regime)` across many tickers. A pooled segment can cross 30 observations (UI shows "warm") while any individual instrument inside it is still near-zero in the actual per-instrument calibration math. Users see a false "no longer cold start" signal. | **CLOSED 2026-07-13** | Fixed the UI side (lower-risk than touching live calibration math): `segmentObs()` now counts strictly per-`instrument_id`, matching `engine.py` exactly. `isColdStart` and the banner text now reflect the real number of stocks still below `OBSERVATION_THRESHOLD` of their OWN results, not a pooled cohort count. `segmentKey()` removed as dead code. `tsc --noEmit` clean. |

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

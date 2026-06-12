# GAP_REGISTER.md — Pre-Build Audit (v1.1)

**Audited:** SPEC v1.0 · handover package v1.0 · BUILD_PLAN · ADR-001..005 · conversation decisions.
**Severity:** P0 blocks session 1/G0 · P1 blocks the tagged phase · P2 recorded-not-lost.
**Owners:** TARUN · CC (Claude Code, build-time) · DONE (remediated in this session, shipped in v1.1).
**F-trace result (D4):** every SPEC requirement F1–F8 and acceptance item §9.1–9.6 maps to a BUILD_PLAN item; the single orphan found (§9.6 chaos test) is closed as GAP-17.

| ID | Sev | Gap | Rationale (what breaks) | Solution | Status / Next step |
|---|---|---|---|---|---|
| GAP-01 | P0 | Sweep tools referenced by CI but didn't exist | CI red from first commit; Invariants 1/9/11 unenforced | Working `tools/hardcode_sweep.py` + `purity_check.py`, self-tested | **DONE** — CC wires into CI at 0.1 |
| GAP-02 | P0 | Donor code unavailable in new repo; equivalence tests had no baseline | Phase 0.3 ports unverifiable → silent behavior drift from GSI | Vendored `donor_reference/` (6 modules) + `tools/gen_donor_fixtures.py` **already run**: fixtures committed (`donor_indicators_fixture.json`, `synth_ohlcv.parquet`) | **DONE** — CC asserts against fixtures at 0.3 |
| GAP-03 | P0 | Synthesis prompt templates referenced but unwritten | Phase 4.6 had no prompt contract; injection guard undefined | `synthesis/prompts/relevance.md` + `synthesize.md` with data-not-instructions guard | **DONE** |
| GAP-04 | P1·P3 | No NIFTY 50 TRI source — alpha thresholds unmeasurable (yfinance ^NSEI is price index, not TRI) | Spec §2 alpha gates can't be computed; accuracy ledger incomplete | `niftyindices` source + `benchmark.primary` config + BUILD_PLAN 3.6 | **DONE** — CC verifies CSV endpoint at 3.6 |
| GAP-05 | P1·P4 | RSS feed lists were empty placeholders | Phase 4.1 had no inputs; synthesis layer starves | Official-first allowlist filled (RBI×2, SEBI, PIB, 3 financial); exchanges covered via filings poller (no stable public RSS) | **DONE** — TARUN/CC verify URLs live at 4.1 |
| GAP-06 | P1·P2 | No corporate-actions model — splits/bonuses/dividends/IDCW unhandled | **Silent P&L corruption**: a 1:1 bonus halves price overnight; returns/forecasts/signals all poisoned | Migration `0002`: corporate_actions + price_adjustments (raw prices stay bhavcopy-true, adjusted derived — ADR-009) + BUILD_PLAN 2.8 | **DONE (schema/plan)** — CC builds at 2.8 |
| GAP-07 | P1·P2 | No market calendar/holiday source; "market hours only" had no mechanism | Quote jobs fire on holidays; staleness logic lies on weekends | market_calendar table (0002) + nse_calendar source + donor MARKET_SESSIONS ported to `sessions` config + BUILD_PLAN 2.9 | **DONE (schema/plan)** — CC at 2.9 |
| GAP-08 | P1·P2 | FX handling for US holdings unspecified | INR-consolidated P&L wrong for US positions | FRED DEXINUS already seeded; rule added: views consolidate via macro_series fx — note in SCHEMA conventions | **DONE (note)** — CC implements in v_portfolio_positions |
| GAP-09 | P1·P0 | QA_STANDARDS deferred but Phase 0 CI needs test conventions | Test style decided ad-hoc; network assertion (the Invariant-3 proof) undefined | `docs/QA_STANDARDS.md`: pyramid, fixtures policy, Playwright route-guard snippet, gate coverage map, QA-brief format | **DONE** |
| GAP-10 | P1·P1 | Scheduler ambiguity (pg_cron vs APScheduler appeared in different docs) | Two scheduling truths = missed/duplicate jobs | ADR-006: APScheduler in-worker is the single scheduler; pg_cron unused for jobs | **DONE** |
| GAP-11 | P1·P4 | Embedding model was a "local-768" placeholder | Phase 4.3 blocked on an undecided dependency; schema dim already fixed at 768 | ADR-008: sentence-transformers/all-mpnet-base-v2 (768-dim, local, $0) | **DONE** |
| GAP-12 | P1·P4 | Dependency-graph seed format/file absent | Phase 4.4 "starter graph" had nothing to start from | `config/dependency_graph.seed.json` — 6 edges incl. the mining acceptance-test path | **DONE** — CC extends for held sectors at 4.4 |
| GAP-13 | P1·P1 | No failure visibility until Phase 7 | Six phases of silent ingestion failures during the period that matters most | Daily run-health digest + optional webhook; `alerts.*` config; BUILD_PLAN 1.7 | **DONE (plan)** — CC at 1.7 |
| GAP-14 | P1·P3 | No backup strategy; Supabase free tier has no PITR | Accuracy ledger + forecast history loss = the credibility asset gone | Nightly pg_dump → Storage, 30-day rotation, restore drill; BUILD_PLAN 3.7 | **DONE (plan)** — CC at 3.7 |
| GAP-15 | P1·P7 | yfinance ToS-gray for anything beyond personal use | Public exposure on unofficial source = legal + reliability risk | COMPLIANCE_NOTES: personal-use position documented; licensed replacement (EODHD) is a hard pre-public gate | **DONE (doc)** — TARUN decision at Phase 7+ |
| GAP-16 | P1·P2 | CAS PDF parsing risk underestimated (password-protected, format drift, NSDL≠CDSL) | Phase 2.5 could burn a sprint hand-rolling | Evaluate `casparser` (MIT) first — purpose-built; BUILD_PLAN 2.9 note | **DONE (note)** — TARUN supplies redacted fixture |
| GAP-17 | P1·P7 | SPEC §9.6 chaos test (kill an upstream) absent from plan | Acceptance criterion with no executing item — the F-trace's one orphan | BUILD_PLAN 7.5 | **DONE** |
| GAP-18 | P0 | GSI's fate undecided → attention-split risk + stale Project Files | Two active codebases share Tarun's usage limits; this Claude Project still carries GSI v5.32 docs | ADR-007: GSI **frozen at v5.41**, app stays deployed untouched, retired at Phase 5 parity; the GSI restructure plan is formally **SUPERSEDED** | **DONE (ADR)** — TARUN: mark GSI README, stop GSI sprints, swap this Project's files for the new platform docs |
| GAP-19 | P0 | Tarun-owned prerequisites scattered across docs | Session 1 stalls on a missing key or fixture | Consolidated checklist below | **TARUN** — before/at Phase 0 |
| GAP-20 | P2 | Web error tracking absent | Family-user bug reports will be "it broke" | Sentry free tier at Phase 6/7 | CC backlog |
| GAP-21 | P2 | Anthropic Batches API + prompt caching unexploited in v1.0 docs | Leaving ~50% of LLM spend on the table | `llm.use_batch_api` config + COMPLIANCE_NOTES playbook §1–2 | **DONE (config/doc)** — CC implements at 4.6 |
| GAP-22 | P2 | Future asset classes (bonds/gold/FD/real-estate) need enum migration path | Spec future-state; avoid schema rework | `instruments.kind` extension is a 1-line migration; valuation engines are the real work — backlog | Recorded |
| GAP-23 | P2 (D8) | Business/strategy: name undecided (blocks brand/domain), trademark/MCA search not run, monetization posture unset, guidebook-synergy unexplored, public-product compliance track unscoped | None of it blocks the build; all of it blocks a launch | NAMING.md decision before Phase 6 → trademark/domain check → monetization + compliance as a separate planning exercise post-G5 | **TARUN** — calendar it at G5 |

## TARUN Checklist (GAP-19 consolidated — the only human-blocking items)
1. ENV_SETUP accounts: Supabase (ap-south-1), Vercel, Railway/Fly, Anthropic key (+spend limit), GitHub repo. — *before session 1*
2. Fixtures: redacted broker CSV + CAS PDF → `worker/tests/fixtures/`. — *before Phase 2*
3. Verify RSS URLs live (5-minute check) or leave to CC at 4.1. — *Phase 4*
4. Design references for DESIGN_BRIEF. — *before Phase 6*
5. Name decision + MCA/trademark/domain check. — *before Phase 6*
6. GSI: README freeze note; stop GSI sprints; swap Claude Project Files to platform docs. — *now*

## Residual Risks (audited, accepted, no action)
- Single-writer WIP.md assumes one developer — true for this program.
- Supabase free-tier limits — monitored via COMPLIANCE_NOTES §9 math; first trigger is years out.
- 3Y horizon is scenario-based by design — not a gap, a documented stance.
- mpnet worker image weight (~500MB) — accepted in ADR-008, revisit only if RAM-constrained.

# SESSION_RESUME.md — AlphaVeda Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-06-22 (council review gate + Block 0-2 + Supabase live)
**Previous session:** 2026-06-21 (design doc complete, HTML artifact, expert skills gate)
**Workspace:** stock-intelligence-test-1-vs (GSI → AlphaVeda MVP build)

---

## DO NOT REDO — Session 2026-06-22 (updated post-council)

### 1. Council Review Gate — ALL 4 QUESTIONS VOTED

11-seat council (7 investor + 4 doctrine) voted on all 4 HTML Tab 6 questions:

| Question | Verdict | Key action |
|---|---|---|
| Q1 — 9 migrations | REVISE | 4 migration fixes (B1-B4) |
| Q2 — Cold-start weights | APPROVE | 2 conditions tracked |
| Q3 — EXIT trigger E2 | REVISE | Bucket-aware thresholds + confidence floor |
| Q4 — Review banner | APPROVE | 3 additions required |

Council also produced sequenced action plan (Block 0–8).

### 2. Block 0 — Design Doc v0.3 COMPLETE (commit 0fe54b0)

All council REVISE verdicts applied to `docs/superpowers/specs/2026-06-21-alphaveda-mvp-design.md`:
- B1: outcome_id FK removed from 0007_accuracy_predictions; added via ALTER TABLE at end of 0008
- B2: UNIQUE(regime) removed from 0004_macro_regime — time-series table, same regime repeats daily
- B3: exit_trigger CHAR(2) E1-E4 added to 0006_trade_outcomes
- B4: 0010_ingest_status.sql added as new migration spec
- E2 EXIT trigger now bucket-aware: near_term=3, medium_term=5, long_term=7 consecutive BEAR signals
- E2 confidence floor ≥ 50 added (E2_CONFIDENCE_FLOOR = 50 in constants.py)
- Weight proposal banner added to pages/path.py spec
- WEIGHT_REVIEW_PROCESS.md spec added inline (quarterly, backstop 90 days, obs≥30 + delta≥3%)
- Section 1.5 (non-goals, 9 items) added by R2b
- SLAs subsection in Section 8 added by R2b (7 rows, realistic free-tier targets)

### 3. Block 2 — ALL 3 AGENTS COMPLETE (commit 252b8ac + 0fe54b0 + 8ff0364)

| Agent | Output | Commit |
|---|---|---|
| R2a (Opus) | 9 expert personas → `docs/experts/` (9 files, 366–504 words each) | 252b8ac |
| R2b (Sonnet) | Section 1.5 non-goals + SLAs added to design doc | 0fe54b0 |
| R2c (Sonnet) | `DESIGN.md` at repo root (232 lines, 15 brand tokens, 8 sections) | 8ff0364 |

### 4. Critical Schema Defect Found and Fixed (commit 252b8ac)

Found by R2a expert Deepak Nair (schema-design persona):
- **Bug:** Council B0.1 fix added UNIQUE(regime) to macro_regime to allow FK reference from accuracy_predictions. But macro_regime is a time-series table — UNIQUE(regime) caps it at exactly 4 rows total, making all ingest beyond the 4th row fail silently.
- **Fix:** UNIQUE(regime) removed. accuracy_predictions.regime_tag changed from FK to CHECK-only. Enum validation via CHECK is correct; referential integrity to a time-series table was architecturally wrong.

### 5. Supabase LIVE — alphaveda-prod ap-south-1 (commit 69e943e)

- Project: **alphaveda-prod** | Ref: **kowlkczswaglbmabygtl** | Region: ap-south-1 (Mumbai)
- Org: ferhzizogqwgdoxymgiy (Tarun19k's Org) | Plan: Free tier
- All 11 migrations applied to remote DB (verified via Supabase dashboard)
- Credentials: `.env` at workspace root (gitignored — NEVER commit)
- Credentials inventory: `docs/supabase/CREDENTIALS.md` (committed, no secrets)
- Recovery instructions: curl management API (see CREDENTIALS.md)
- Memory: `~/.claude/projects/.../memory/project_alphaveda_supabase.md`

### 6. Supabase Documentation Complete (commit 8ff0364)

| File | Lines | Contents |
|---|---|---|
| `supabase/migrations/20260621100001_instruments.sql` | — | Lynch classification NOT NULL, 6-value CHECK |
| `supabase/migrations/20260621100002_ohlcv.sql` | — | UNIQUE(instrument_id, trade_date) |
| `supabase/migrations/20260621100003_fundamentals.sql` | — | UNIQUE(instrument_id, period_end) |
| `supabase/migrations/20260621100004_macro_regime.sql` | — | regime CHECK only, NO UNIQUE (time-series) |
| `supabase/migrations/20260621100005_portfolio_buckets.sql` | — | 4 seed rows included |
| `supabase/migrations/20260621100006_trade_outcomes.sql` | — | exit_trigger CHAR(2) E1-E4, nullable |
| `supabase/migrations/20260621100007_accuracy_predictions.sql` | — | regime_tag CHECK only; no outcome_id |
| `supabase/migrations/20260621100008_accuracy_outcomes.sql` | — | ends with ALTER TABLE adding outcome_id FK |
| `supabase/migrations/20260621100009_signal_weights.sql` | — | UNIQUE(lynch_class, regime, signal_name, status) |
| `supabase/migrations/20260621100010_ingest_status.sql` | — | staleness badge backing table |
| `supabase/migrations/20260621100011_waitlist.sql` | — | price_feedback + referred_by columns |
| `docs/supabase/SCHEMA.md` | 595 | Full ERD + 11 table refs + FK map + index recommendations |
| `docs/supabase/GSI-OVERLAP.md` | — | No conflicts; only other project is Claude Observability (Tokyo) |
| `DESIGN.md` | 232 | Developer onboarding doc, 15 brand tokens, page map, data flow |

### 7. R2a Expert Findings — 5 Design Issues (input for R1)

Found while writing expert personas — not yet actioned, mandatory challenge targets for Block 3:

| # | Expert | Finding | Severity |
|---|---|---|---|
| F2 | portfolio-theory (Prof. Sanjay Iyer) | `magnitude_target` used as Kelly odds `b` is dimensionally wrong — loss leg unmodelled | P1 |
| F3 | behavioral-finance (Dr. Kavya Menon) | `STREAK_DISCOUNT_FACTOR=0.7` discounts ledger accuracy only, not live emitted confidence | P1 |
| F4 | signal-engineering (Dr. Anika Reddy) | `confidence` fed to Kelly with no calibration map; `arbitration.py` completely unspecified | P1 |
| F5 | systems-reliability (Imran Sheikh) | GHA cron + Supabase free-tier both auto-pause on inactivity; missed ingest run = silent failure | P2 |
| Q2-C2 | schema-design (Deepak Nair) | macro_regime referenced as FK when it is a time-series — structural misuse of FK semantics | FIXED |

### 8. Block 3 — R1 Red Team COMPLETE (commit a23eb6f)

- Verdict: **REVISE** — 18 gaps (P0:4, P1:9, P2:5)
- Report: `docs/reviews/R1-red-team.md`
- Core finding: Kelly formula (`b = magnitude_target`) is dimensionally wrong — floors to "1% in everything" for all realistic inputs. Invalidates Layer 4.
- 4 P0 gaps: GAP-001 (Kelly), GAP-002 (calibration), GAP-003 (arbitration void), GAP-006 (silent pipeline pause)
- All 6 mandatory targets confirmed (F2, F3, F4, F5, E2, Shakuni)

### 9. Block 4 — R3 Full Council COMPLETE (commit a23eb6f)

- Council: 20 voices (7 investor + 4 doctrine + 9 expert)
- Verdict: **CONDITIONAL GO**
- Report: `docs/reviews/R3-council-strategic-assessment.md`
- 14 missing actions identified — Block 3.1 was under-scoped
- Synthesis Chair re-classified GAP-009 as P0 (live migration defect)
- Soros and Druckenmiller **withdrew prior approvals** — GAP-004/005 promoted into Block 3.1
- Block 3.1 re-scoped: "produce v0.4 + migrations 0011/0012 + commercial-gate binding, in dependency order, reconciled against live migrations"

### 10. Session 2026-06-22 Commits (in order)

| Commit | Description |
|---|---|
| 0fe54b0 | design doc v0.3 — council amendments + non-goals + SLAs |
| 252b8ac | schema defect fix + R2a expert personas + supabase init |
| 8ff0364 | 11 migration SQL files + SCHEMA.md + GSI-OVERLAP.md + DESIGN.md |
| 69e943e | Supabase cloud live + credentials inventory + .env.example |
| 402a06c | housekeeping checkpoint — SESSION_RESUME + graphify-out |
| a23eb6f | R1 red team + R3 council strategic assessment |

---

## EXACT RESUME POINT — UPDATED 2026-06-22 (post-council)

**NEXT ACTION: G-MIG gate → Phase 2 Data Layer**

Phase 1 is COMPLETE (1ae8e37). G-MIG gate is blocked on Supabase MCP auth.
After Supabase auth completes: apply migrations 0012+0013, re-run G-MIG, then start Phase 2.

Design doc v0.6 is the approved build spec. R4 CONDITIONAL GO is in force. Build sequence:

| Phase | Content | Day |
|---|---|---|
| Phase 1 (Foundation) | Create repo, apply 13 migrations, constants.py, .claude/rules/, seed 10 instruments | Day 1 |
| Phase 2 (Data layer) | config.py, regime.py, provider.py, cycle_phase.py | Day 1–2 |
| Phase 3 (Signal layer) | ledger.py, downside.py, arbitration.py, weights.py, engine.py | Day 2–3 |
| Phase 4 (Portfolio layer) | buckets.py, optimizer.py with Kelly + E1-E4 | Day 3 |
| Phase 5 (Presentation) | app.py + 4 pages (data_viewer, signals, path, accuracy) | Day 4 |
| Phase 6 (GHA ingest) | 5 ingest scripts + resolve_outcomes.py + ingest.yml | Day 4–5 |

**Pre-G1 tracked items (not blocking build):**
- GAP-006: keepalive strategy for GHA + Supabase free tier (before first billing)
- calibration.py interface spec (before G1 regression suite)
- approve_signal_weight RLS caller-identity check (before G2)

---

## TARUN P0 ACTIONS — Still Pending

| Action | Status | Blocks |
|---|---|---|
| T1: Supabase project creation | ✓ COMPLETE (done this session) | — |
| T2: `pip install supabase postgrest pandas_market_calendars streamlit plotly pytest` | PENDING confirmation | G0 smoke tests |
| T3: WhatsApp 3 NSE investors pricing signal ("₹999/month for confidence-scored signals?") | PENDING | R4 Synthesis (≥1 response needed) |
| T4: Confirm UI label "Signal weights: using priors (N observations)" — G0 scope or G1? | PENDING | Determines test_smoke.py spec |
| Stream C: 3 consulting outreach targets | OVERDUE | Revenue |
| Stream A Gate 6: Gumroad listing sign-off | SEPARATE SESSION | Revenue |

---

## 7 PRE-BUILD CONDITIONS — ALL RESOLVED ✓

| # | Condition | Status |
|---|---|---|
| 1 | Data source architecture | ✓ Bhavcopy + yfinance + BSE + FMP three-tier |
| 2 | Stock classification schema | ✓ Lynch 6-enum + is_psu BOOLEAN |
| 3 | Bucket architecture | ✓ 4-bucket ₹17L design |
| 4 | Fundamental data layer | ✓ 9 fields, Munger ceiling, BSE as primary source |
| 5 | Macro regime classifier | ✓ PMI + RBI/CPI semi-manual, current: RISK_ON |
| 6 | SEBI compliance | ✓ Analytics framing, RIA at first payment |
| 7 | Position sizing | ✓ Quarter Kelly, portfolio_value = ₹7.25L |

---

## OPEN DECISIONS (Tarun-owned)

| Decision | Default if no answer | Needed by |
|---|---|---|
| T4: UI label "using priors" — G0 smoke test or G1? | Assume G0 (required) | Before writing test_smoke.py |
| Pricing validation: WhatsApp 3 contacts | ₹999/mo assumed if no response | Before R4 (needs ≥1 real signal) |
| Stream C: 3 consulting outreach targets | OVERDUE — no default | TODAY |
| AlphaVeda pricing: ₹999/mo single tier or tiered? | ₹999/mo single tier | Sprint G2 |
| Custom domain? (alphaveda.in?) | Streamlit subdomain | Sprint G2 |
| Stream A Gate 6: final Gumroad listing sign-off | Required before publishing | Separate session |

---

## COMMERCIAL STATE — Updated 2026-06-22

- **Stream A (Gumroad Governance Pack):** LATE — separate session. Gates 2+6 Tarun-owned.
- **Stream C (Financial consulting):** OVERDUE. 3 targets needed immediately.
- **Stream D (AlphaVeda):** Supabase live ✓. R1→R4 in progress. G0 pending T2 + pytest.
- **Stream B (YarnZoo / StitchFlow):** Deferred — out of 21-day scope.
- **Revenue clock:** 21-day goal, started 2026-06-21. AlphaVeda is highest-leverage stream in progress.

---

## BLOCK SEQUENCE — STATUS

| Block | Description | Status |
|---|---|---|
| Block 0 | Design doc v0.3 amendments | ✓ COMPLETE |
| Block 1 | Tarun actions (T1-T4) | T1 ✓, T2/T3/T4 pending |
| Block 2 | R2a + R2b + R2c parallel agents | ✓ COMPLETE |
| Block 3 | R1 Red Team (REVISE, 18 gaps) | ✓ COMPLETE |
| Block 4 | R3 Full Council (CONDITIONAL GO, 14 MAs) | ✓ COMPLETE |
| Block 3.1 | v0.4 + migrations 0011/0012 + gates (7 steps) | ✓ COMPLETE (73c242f) |
| pre-R4 council | 21-voice readiness check → CONDITIONAL READY (82917e5) | ✓ COMPLETE |
| v0.5 corrective | C-1..C-4 closed: 0013 migration + downside.py + pipeline order + G0 gate | ✓ COMPLETE (7c9ec93) |
| Block 5 (R4) | 21-voice synthesis → CONDITIONAL GO, BC-1..BC-8 applied, design doc v0.6 | ✓ COMPLETE (b7baaa3) |
| Block 6 Phase 1 | alphaveda/ scaffold: constants, rules, TDD suite, waitlist page | ✓ COMPLETE (1ae8e37) |
| G-MIG gate | 11/13 tables PASS; migrations 0012+0013 NOT applied (400) | ⏳ BLOCKED: Supabase auth |
| Block 6 Phase 2 | Data layer: config.py, regime.py, provider.py, cycle_phase.py | ⏳ AFTER G-MIG PASS |
| Block 7 | G0 gate (10 criteria: 9 tests + 1 seed) | After Block 6 + T2 |
| Block 8 | Post-G0 (G1, auth, GHA cron) | Future sessions |

---

## SECURITY RULES — PERMANENT (never modify)

- `.env` is gitignored — NEVER commit
- `SUPABASE_SERVICE_KEY` for ingest scripts only — never in Streamlit app/client code
- `ALPHAVEDA_COMMERCIAL=false` must remain false until first non-self subscriber (triggers FMP/paid data gate)
- yfinance blocked when `ALPHAVEDA_COMMERCIAL=true` via CommercialLicenseError
- SEBI disclaimer must appear on every page — never remove or conditionalize
- No signal_weights status change PROPOSED → ACTIVE without `approved_by='tarun'` — automation cannot approve weights

---

## DO NOT REDO — Prior Sessions (preserved)

### 2026-06-21 MVP DESIGN — ALL 9 SECTIONS COMPLETE (817 lines)
- 7/7 council unanimous: Option C feedback loop, Approach 2 MVP scope
- 9 migrations fully specified (original 9 → now 11 with ingest_status + waitlist)
- 13 council conditions traced to file + artifact + test (Section 9 trace matrix)
- 6 mandatory accuracy guards locked
- HTML artifact committed: `docs/artifacts/2026-06-21/alphaveda-mvp-spec.html` (`397d5fc`)
- Council ownership map: 7 investor + 4 doctrine + 9 expert domain gaps

### 2026-06-21 PHASE B COUNCIL + ARCHITECTURE
- Lynch (Condition 2): Lynch 6-enum classification
- Buffett + Munger (Condition 4): 9-field fundamental layer
- All 7 conditions resolved
- Q2 CHANGED: Cloud-only confirmed. Docker not installed. Supabase cloud ap-south-1 only.

### 2026-06-21 PRODUCT NAME + BRAND
- Product name: AlphaVeda (Alpha = excess returns; Veda = Sanskrit "to know")
- Colors: Deep Indigo #1A1F3C + Warm Ivory #F5F3EC + Saffron Gold #E8A020
- Typography: Fraunces (headings) + DM Mono (data) + Inter (prose)
- Brand brief: `docs/brand/alphaveda-brand-brief.md`

### 2026-06-19→20 INFRASTRUCTURE + PHASE A COUNCIL
- RAG gateway live, council complete, GSI bucket architecture confirmed
- Q1 (ingest): GHA cron 5:45 PM IST weekdays + lazy fallback
- Q3 (historical depth): OHLCV 3yr · Fundamentals 5yr · Macro 5yr

### 2026-06-16→18 PRIOR WORK (do not re-run)
- 7-seat full council: 7 REVISE verdicts (do not re-run)
- 28-requirement inventory: complete (do not rebuild)
- Strategic analysis: CONSOLIDATE posture (still valid)
- RAG gateway: live (commit 4eb2188)

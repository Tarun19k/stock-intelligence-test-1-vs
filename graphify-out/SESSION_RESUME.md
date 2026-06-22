# SESSION_RESUME.md — AlphaVeda Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-06-22 (council review gate + Block 0-2 + Supabase live)
**Previous session:** 2026-06-21 (design doc complete, HTML artifact, expert skills gate)
**Workspace:** stock-intelligence-test-1-vs (GSI → AlphaVeda MVP build)

---

## DO NOT REDO — Session 2026-06-22

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

### 8. Session 2026-06-22 Commits (in order)

| Commit | Description |
|---|---|
| 0fe54b0 | design doc v0.3 — council amendments + non-goals + SLAs |
| 252b8ac | schema defect fix + R2a expert personas + supabase init |
| 8ff0364 | 11 migration SQL files + SCHEMA.md + GSI-OVERLAP.md + DESIGN.md |
| 69e943e | Supabase cloud live + credentials inventory + .env.example |

---

## EXACT RESUME POINT — UPDATED 2026-06-22

**NEXT ACTION: Block 3 — R1 Red Team (Opus)**

All inputs are available:
- Design doc v0.3: `docs/superpowers/specs/2026-06-21-alphaveda-mvp-design.md`
- 9 expert personas: `docs/experts/` (9 files)
- 11 migration SQL files: `supabase/migrations/`
- DESIGN.md at repo root
- Supabase cloud live with all 11 tables

R1 mandate:
- ≥ 12 adversarial gaps, each with severity P0/P1/P2 + affected section
- **Mandatory challenge targets:** F2 (Kelly odds dimensionally wrong), F3 (streak discount timing), F4 (confidence calibration/arbitration.py unspecified), F5 (silent inactivity pause), Shakuni's macro_regime-as-context concern, E2 confidence floor edge cases
- Output: `docs/reviews/R1-red-team.md`

**Sequence after Block 3:**
- Block 4: R3 Full Council (20 voices: 7 investor + 4 doctrine + 9 expert personas)
- Block 5: R4 Synthesis — needs R3 complete AND T3 (≥1 pricing signal response from real contact)
- Block 6: Pre-build implementation parallel (P1-P5) — starts only after R4 GO
- Block 7: G0 gate (pytest 6/6 + 10 seed instruments + ingest_status populated)

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
| Block 3 | R1 Red Team (Opus, ≥12 gaps) | ⏳ NEXT |
| Block 4 | R3 Full Council (20 voices) | Waiting on Block 3 |
| Block 5 | R4 Synthesis (GO/HOLD/REVISE) | Waiting on Block 4 + T3 |
| Block 6 | Pre-build implementation (parallel) | Waiting on R4 GO |
| Block 7 | G0 gate (pytest 6/6 + seeds) | Waiting on Block 6 + T2 |
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

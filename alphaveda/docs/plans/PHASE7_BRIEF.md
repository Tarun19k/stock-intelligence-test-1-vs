# AlphaVeda Phase 7 — Hybrid Architecture Brief
# STATUS: DRAFT — no build without Tarun approval
# Council: Synthesis Chair + SRA + Constraint Enforcer + Revenue Strategist
# Date: 2026-06-27

> **DRAFT — no build without Tarun approval.**
> This is a planning document only. No code, no architectural writes, no migration has begun.
> Phase 7 build does NOT start until BOTH gates clear:
> (1) G0 live DB seed passes (`python3 scripts/ingest.py` against live Supabase, 3 FAIL tests → PASS), AND
> (2) Tarun explicitly states **"PHASE7_BRIEF APPROVED"** in chat.

---

## 0. Why this brief exists

AlphaVeda Phases 1–6 are complete: 179 PASS / 1 SKIP / 3 FAIL (the 3 FAILs are intentional G0 seed gates).
Current architecture is Streamlit on Python. Council (prior session) approved migration to a **hybrid**:

- **Next.js (App Router, TypeScript) on Vercel** — frontend shell, the 4 pages (Market Data, Signals, Path, Accuracy), auth UI, SEBI disclaimer.
- **FastAPI on Railway** — backend API serving signal data, portfolio/Kelly sizing, accuracy ledger, ingest orchestration.

**Why not stay on Streamlit + Vercel:** incompatible by construction.
- Streamlit needs a **persistent server process**; Vercel is **serverless-only** (functions, no long-lived process).
- Vercel Python bundle limit is **~10 MB compressed**; AlphaVeda deps (supabase, pandas, pandas-market-calendars, plotly, postgrest) are **~17 MB**.
- The hybrid split is the only viable path: stateless Next.js on Vercel, stateful/heavy Python on Railway (no bundle ceiling, persistent process).

This is a **frontend + transport rewrite, not a logic rewrite.** The Python signal/portfolio/accuracy/ingest logic in `src/` is reused as-is behind FastAPI. The DO NOT UNDO surface is the *business logic*, which does not move.

---

## 1. Phase 7 sprint structure

Three sessions, sequential. Each session ends with a commit and a green test gate. No session begins until the prior session's Definition of Done is met.

### Session A — Backend extraction (FastAPI on Railway)
**Goal:** wrap existing `src/` logic in a FastAPI app and deploy to Railway. No logic changes.
**Builds:**
- `api/main.py` — FastAPI app, CORS locked to the Vercel domain only.
- Route handlers that import and call existing `src/signals`, `src/portfolio`, `src/accuracy`, `src/data` functions. Thin adapters, no reimplementation.
- Endpoints (read-only to client): `GET /signals`, `GET /market-data`, `GET /path` (Kelly sizing), `GET /accuracy`, `GET /health`.
- `railway.toml` (3 lines — already AlphaVeda-compatible per prior council note).
- Pydantic response models that **carry the SEBI framing fields** (signal labels, not advice; disclaimer string in every payload envelope).
- Commercial-gate logic (`is_commercial()` from `COMMERCIAL_GATE.md`) preserved server-side, including **fail-closed → commercial=True** and rupee suppression. This stays on the backend — the client never decides commercial state.
**Milestone A:** Railway service live, `/health` green, all endpoints return seeded data, backend test suite green. SEBI substance test ported to API-response level (no BUY/SELL/invest in any payload).

### Session B — Frontend shell (Next.js on Vercel) + SEBI enforcement
**Goal:** Next.js App Router shell rendering the 4 pages from the FastAPI API, with the disclaimer enforced structurally.
**Builds:**
- Next.js App Router scaffold (TypeScript), 4 routes mapped to the 4 current pages.
- A **root layout** `app/layout.tsx` that renders `<SebiDisclaimer />` outside the page slot, so it cannot be removed per-page (see Section 4).
- Server-side data fetching from FastAPI (Server Components / route handlers), not client-side keys.
- Staleness / cold-start / empty states ported from UI-1 design system tokens.
- No business logic in the frontend. The frontend renders what the API returns; it does not compute signals or sizing.
**Milestone B:** 4 pages render live from Railway API on a Vercel preview URL. Disclaimer present on every route (automated test). SEBI substance test green at the rendered-DOM level.

### Session C — Auth layer + commercial gate + hardening
**Goal:** Supabase Auth gates subscriber-only surfaces; production cutover readiness.
**Builds:**
- Supabase Auth wired in Next.js (`@supabase/ssr`), session via cookies, middleware guarding subscriber routes.
- Auth state → backend: signed request context so FastAPI knows whether the caller is a converted subscriber (drives commercial=True data-source switch).
- Rupee-suppression UX as a **designed state** (per `COMMERCIAL_GATE.md` — "BULLISH signal" not "₹72,500 position"), not a degraded fallback.
- Production env wiring (Vercel env vars, Railway env vars), domain, rollback runbook.
**Milestone C:** A test subscriber can sign up, authenticate, and reach gated content; non-subscribers see public surfaces only; commercial data-source switch verified; rollback runbook tested once (tabletop).

**Token-light buffer:** if Session C overruns, auth (the revenue gate) takes priority over hardening polish; hardening can spill to a short Session C′.

---

## 2. Risk register (top 5)

| # | Risk | Sev | Detection | Root cause | Mitigation |
|---|---|---|---|---|---|
| R1 | **CORS / origin leak** — backend accepts requests from any origin, API becomes a public data tap | P2 | delayed | default-permissive CORS in FastAPI | Lock `allow_origins` to the exact Vercel prod + preview domains; deny `*`; assert in a backend test. |
| R2 | **SEBI disclaimer missing on a route** — new Next.js per-page rendering drops the pinned disclaimer that Streamlit injected globally | P1 (compliance) | silent | disclaimer was a Streamlit global; Next.js renders per-route | Render disclaimer in **root layout outside the page slot**; add a Playwright test asserting disclaimer text on every route; CI-block on failure (Section 4). |
| R3 | **Railway cold-start / sleep** — free-tier dyno sleeps, first request after idle times out, frontend shows empty/error | P2 | delayed | Railway idles inactive services | Health-check ping (keep-warm) or paid always-on tier; frontend renders a defined loading/stale state, never a blank crash; circuit-breaker timeout on fetch. |
| R4 | **Commercial gate bypass** — frontend trusts a client flag and shows rupee amounts to a commercial subscriber, violating yfinance ToS / SEBI suppression | P1 | silent | gate logic moved client-side or duplicated | `is_commercial()` stays **server-side only**, fail-closed to commercial=True; client never computes it; rupee suppression enforced in API payload, not the UI. |
| R5 | **G0 false-green / partial seed** — Phase 7 build starts against an empty or partially-seeded DB; endpoints return [], looks "working" but is hollow | P1 | delayed | build gate read as "tests pass" not "data present" | Hard gate: Phase 7 Session A cannot start until `scripts/ingest.py` writes a real `ingest_status` OK row AND the 3 G0-gate tests flip to PASS. Verify row count, not just exit code. |

Secondary (tracked, not top-5): Vercel/Next version drift; Supabase Auth cookie/SSR misconfig (`getUser` vs `getSession`); circuit_flag exclusion still a pre-G1 gate (do not start accuracy-ledger writes until wired — carried from `DATA_SOURCES.md`).

---

## 3. Token budget

Prior estimate (council 2026-06-27): **8–12 hours, 2–3 sessions, ~55,000 Sonnet tokens.** This brief keeps that envelope and routes by tier.

| Session | Work | Tier | Est. tokens |
|---|---|---|---|
| A — Backend extraction | FastAPI wrappers, routes, railway.toml, response models | **T2 Sonnet** (multi-file, transport design) | ~22,000 |
| B — Frontend shell | Next.js scaffold, 4 routes, layout, disclaimer wiring | **T2 Sonnet** | ~20,000 |
| C — Auth + gate | Supabase Auth, middleware, commercial switch, rollback runbook | **T2 Sonnet** | ~10,000 |
| Mechanical (all sessions) | env var entry, file moves, dependency pins, commits | **T1 Haiku** | ~3,000 |
| Planning/review checkpoints | this brief, per-session review gates, synthesis | **T3 Opus** (already largely spent on this brief) | (sunk) |

**Total build estimate: ~55,000 tokens.** Routing rule (Constraint Enforcer): keep Haiku ≥20% of mechanical work; do not route file-move/env-entry/commit tasks through Sonnet. Opus is reserved for this brief and per-session review gates only — not for implementation.

---

## 4. SEBI compliance wiring plan for Next.js

**The hard requirement:** the SEBI disclaimer must appear on EVERY page. In Streamlit this was a single global injection in `app.py` (`get_disclaimer_html()` → fixed-bottom, before any page content). Next.js renders per-route, so a naive port risks dropping it on a new page (Risk R2). New implementation is required.

**Enforcement (defence in depth — three layers):**

1. **Structural (cannot be removed per-page):** render `<SebiDisclaimer />` in `app/layout.tsx`, **outside** the `{children}` slot. Every route inherits the root layout, so the disclaimer is present by construction, not by per-page discipline. Fixed-position footer, not collapsible, not dismissable — mirrors the Streamlit `av-sebi-footer` contract.

2. **Source of truth:** the disclaimer text is served by the **FastAPI backend** (single source = the Python `SEBI_DISCLAIMER` in `constants.py`), returned in every API response envelope. The frontend renders the backend-provided string. This prevents the text drifting between Streamlit and Next.js and keeps one canonical version.

3. **CI gate (port `test_sebi_substance`):** a Playwright test that, for every route, asserts:
   - disclaimer text is present in the rendered DOM,
   - it contains "research purposes only" and "not investment advice,"
   - no rendered output contains imperative language (BUY / SELL / invest / put money / "you should"),
   - signal labels read "signal" not "recommendation"/"advice."
   This test **blocks merge/deploy** on failure, exactly as the current `tests/test_app.py::test_sebi_substance` does. Backend gets a mirror test at the payload level (no prohibited language in any API response).

**Commercial-state framing stays SEBI-safe:** when commercial=True, rupee amounts are suppressed (direction + confidence only). This is enforced server-side in the API payload, so the frontend physically cannot render a suppressed figure. Disclaimer is unchanged across commercial states.

---

## 5. Definition of Phase 7 complete (measurable gates)

Phase 7 is complete when ALL of the following hold:

- [ ] **G1.** FastAPI deployed on Railway; `GET /health` returns 200; all data endpoints return seeded rows (verified by row count, not just 200).
- [ ] **G2.** Next.js deployed on Vercel; all 4 routes (Market Data, Signals, Path, Accuracy) render live data from the Railway API on a production URL.
- [ ] **G3.** SEBI disclaimer present on **every** route — Playwright gate green; backend payload SEBI test green; no prohibited language anywhere.
- [ ] **G4.** CORS locked to the Vercel domain(s); `*` origin denied; asserted by test.
- [ ] **G5.** Supabase Auth live; a test subscriber can sign up, authenticate, and reach gated content; non-subscribers blocked from gated routes.
- [ ] **G6.** Commercial gate verified: converted subscriber triggers commercial=True data path server-side; rupee suppression confirmed; fail-closed behaviour confirmed (Supabase unreachable → commercial=True).
- [ ] **G7.** Full test suite green on the new architecture (backend + frontend), with the 3 prior G0-gate tests now PASS (because G0 seed is a precondition).
- [ ] **G8.** Rollback runbook exists and has been dry-run once (revert to Streamlit or to prior Vercel deploy); RTO documented.
- [ ] **G9.** No GSI DO NOT UNDO rule violated (business logic in `src/` unchanged; provenance/licence/circuit-flag rules intact).

Phase 7 is NOT complete on "it deploys." It is complete on all nine gates.

---

## 6. Dependency map — what must be done before Phase 7 can start

```
                    ┌─────────────────────────────┐
   PRECONDITION 1 → │ G0 live DB seed PASSES       │
                    │ python3 scripts/ingest.py     │
                    │ → ingest_status OK row written│
                    │ → 3 G0-gate tests flip to PASS│
                    └──────────────┬──────────────┘
                                   │
   PRECONDITION 2 → ┌──────────────┴──────────────┐
                    │ Tarun: "PHASE7_BRIEF APPROVED"│
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
   ENABLERS (not blockers, but needed before each session):
   - Railway account + project (Session A)
   - Vercel project linked to GSI repo (Session B)
   - Supabase Auth enabled on project kowlkczswaglbmabygtl (Session C)
   - ALPHAVEDA_FMP_KEY decision (only relevant once first subscriber converts)
                    └─────────────────────────────┘
                                   │
                    Session A → Session B → Session C
```

**Hard blockers (Phase 7 cannot begin):**
1. G0 seed PASS — live DB, verified by data presence, not exit code.
2. Tarun explicit "PHASE7_BRIEF APPROVED."

**Carried pre-G1 gate (do not violate during Phase 7):** circuit_flag exclusion in `resolve_outcomes.py` is still unimplemented — do not start accuracy-ledger writes until it is wired (`DATA_SOURCES.md`). Phase 7 serves the existing accuracy ledger read-only; it must not trigger new outcome scoring.

**Not on the critical path:** FMP activation (only at first conversion), Vercel custom domain (can use preview URL through Session B).

---

## 7. Council seat verdicts + mandatory changes

### Synthesis Chair (Opus) — structural design / session plan
**Verdict: PROCEED (DRAFT).**
**Synthesis:** The three named tensions resolve cleanly. (a) *Velocity vs reliability* (Revenue wants the auth gate fast; SRA wants hardening) — resolved by sequencing auth ahead of polish in Session C so the revenue gate ships even if hardening spills. (b) *Logic-move risk vs scope* (Constraint Enforcer fears a full rewrite) — resolved by the load-bearing decision that Phase 7 is a **transport + frontend rewrite only**; `src/` business logic is wrapped, not rewritten, which collapses both the risk surface and the token budget. (c) *Disclaimer portability* (Constraint/SEBI) — resolved by making the backend the single source of disclaimer text and the root layout the single render point.
**Load-bearing variable:** whether business logic moves. It does not. Everything downstream (risk, budget, DO NOT UNDO exposure) follows from that.
**Mandatory change:** the brief must state explicitly that `src/` logic is reused unchanged (done — Section 0, Session A, G9).
**Minority view (preserved):** SRA holds that a 3-session estimate is optimistic if Railway cold-start or Supabase SSR auth misconfigures — these are the two most likely overruns. This view is not dismissed; it becomes the primary trigger to split Session C if either consumes more than half a session.

### SRA / Reliability Architect (Sonnet) — migration risk, failure modes, Railway stability
**Verdict: CONDITIONAL — fix FM-01, FM-02, FM-05 before build.**
- FM-01 (P2, delayed): Railway cold-start → frontend blank. Recovery: keep-warm health ping + defined loading state. **Required before Session B sign-off.**
- FM-02 (P1, silent): disclaimer drop on a new route. Recovery: root-layout render + CI Playwright gate. **Required before Session B sign-off — non-negotiable.**
- FM-05 (P1, delayed): build against empty DB. Recovery: G0 verified by row presence, not exit code. **Required before Session A start.**
**Blast radius:** bounded (single product, AlphaVeda) — no cross-system ripple into GSI main dashboard because business logic and DB are isolated. Acceptable.
**Observability requirement:** `/health` endpoint + Vercel/Railway deploy logs = Yellow→Green; add output validation (endpoints return non-empty seeded data) to reach Green before production cutover.
**Confidence: 78/100** — reliability confidence conditional on the three FMs above and on Railway tier choice (free-tier sleep is the largest residual risk).

### Constraint Enforcer (Sonnet) — SEBI, security, GSI DO NOT UNDO preservation, scope
**Verdict: TRIM-then-PROCEED.**
- **Scope discipline:** approved ONLY as a transport+frontend rewrite. Any "while we're here" logic refactor of `src/` is out of scope and displaces the 21-day revenue clock — flag and reject if it appears.
- **Governance gates:** this brief is documentation-only → no premortem-log required for the brief itself. Phase 7 *build* touches no architectural trigger files (CLAUDE.md/settings/skills), so no premortem gate on the build — but the build IS gated on Tarun's explicit data-governance approval because it touches GSI source + Supabase (Data Governance Approval Gate).
- **DO NOT UNDO (GSI parent, 18 rules):** preserved by construction — `cache_buster` args, data-as-of disclosure, provenance (source/ingested_at/licence_class), circuit_flag exclusion rule all live in unchanged Python. **Mandatory:** G9 must assert no DO NOT UNDO rule is touched (done — Section 5).
- **Security:** CORS lock (R1/FM-01) and server-side-only commercial gate (R4) are mandatory, not optional.
- **Feasibility:** Executable but **Tight** — 3 sessions leave no slack. **Mandatory change:** auth (revenue gate) prioritised over hardening in Session C (done — Section 1).
**Constraint verdict: PROCEED on the trimmed scope only.**

### Wealth & Revenue Strategist (Sonnet) — commercial impact, subscriber readiness, auth revenue gate
**Verdict: HIGH VALUE — conditional on auth landing in Session C.**
**Revenue path:** `[Phase 7 ships auth + gated content] → [subscriber can sign up + pay-gate exists] → [GSI/AlphaVeda subscription becomes chargeable] → [MRR]`. The unproven step is payment-gateway wiring, which is downstream of (not within) Phase 7 — flag: Phase 7 makes the product *subscriber-ready*, it does not by itself collect money. Do not let the brief imply revenue lands at G9; it lands when the payment gateway is wired post-Phase 7.
**Leverage:** IP/Platform — a hosted, auth-gated research tool is leveraged recurring revenue, not time-for-money. Correct shape for the 21-day window's compounding criterion.
**Mandatory change:** Definition of Complete must include a **working auth + gated surface** (G5) so Phase 7 measurably advances subscriber readiness, not just a prettier frontend (done — Section 5, G5/G6).
**Commercial-gate caution:** rupee suppression at commercial=True must be presented as a designed state — a subscriber seeing "BULLISH signal" instead of "₹72,500" must not read as a downgrade. UX copy is a revenue-retention detail, not a compliance afterthought.
**Top revenue note:** Phase 7 is necessary but NOT sufficient for first subscriber revenue — payment gateway is the next gate after it. Sequence accordingly; do not let Phase 7 absorb the whole revenue window.

---

## Council summary line

**Synthesis Chair: PROCEED (draft) · SRA: CONDITIONAL (fix FM-01/02/05) · Constraint Enforcer: TRIM-then-PROCEED · Revenue: HIGH VALUE (auth-conditional).**
All four conditional approvals are folded into Sections 1–6. No seat blocks. No seat approved with zero modifications (false-consensus check: passed — each seat imposed at least one mandatory change).

**This document is a DRAFT. No build begins until G0 seed passes AND Tarun states "PHASE7_BRIEF APPROVED."**

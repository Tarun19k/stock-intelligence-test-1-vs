# START_HERE.md — Claude Code Handoff & Kickoff

> **You (Claude Code) are taking ownership of this build.** This file is your first-contact briefing: how to onboard, what to verify before writing code, your literal first actions, and when to stop and ask. Read it fully before anything else. After onboarding, `CLAUDE.md` is your standing law for every session.

---

## 0. What this is

You are building a **personal investment intelligence platform** (working identity: PLATFORM). It ingests a portfolio, forecasts across five horizons, surfaces alpha, recommends rebalancing, and re-evaluates everything as news/policy flows through an LLM synthesis layer. **Recommendations only — never trade execution.** The product is fully specified and decided; your job is to build it phase by phase, not to redesign it.

This package is the **complete pre-build handover**. Everything you need to start is here. Nothing about the product is left to your discretion — where a choice existed, it was made and recorded as an ADR. Where you find ambiguity, that is a defect: stop and ask (see §6).

---

## 0.1 Current state vs. target state (orientation)

You are starting a **greenfield build**. Know exactly where things stand before you touch anything.

**Current state (as-is, today):**
- The **new platform has zero application code.** What exists is *this handover package only* — specs, decisions, the schema SQL (written, **not yet applied**), seed files, the two sweep tools (passing), the donor equivalence fixtures (generated), and read-only donor source in `donor_reference/`.
- **GSI Dashboard** (the donor) is live at **v5.41 on Streamlit Cloud, frozen** (ADR-007). It keeps running untouched; you do not work on it. It exists only as the source you port *from*.
- Nothing is deployed for the new platform. No Supabase project provisioned by you, no migrations applied, no worker, no web app. Local-first from Phase 0.
- **Live position:** pre-Phase-0. The authoritative "where am I this exact session" is always `WIP.md`.

**Target state (to-be, at G7):**
- The platform from `docs/SPEC.md`, shaped per `docs/ARCHITECTURE.md`: worker + Supabase + Next.js web, all eight capability areas (F1–F8) live, accuracy ledger populated and gating, synthesis layer running, recommendations with traceable rationale, multi-user-ready with family exposure enabled.
- Every SPEC requirement and acceptance test (§9.1–9.6) satisfied; every invariant enforced by CI; the Playwright suite the standing regression baseline.

**The trajectory between them (milestones — full detail in `docs/BUILD_PLAN.md`):**

| Gate | From → To (state change) | Authoritative doc |
|---|---|---|
| **G0** | empty repo → scaffold + GSI core ported + CI green | BUILD_PLAN Phase 0 |
| **G1** | no data → one ticker flows source→store→signal→UI | BUILD_PLAN Phase 1 |
| **G2** | one ticker → full universe + real portfolio loads | BUILD_PLAN Phase 2 |
| **G3** | prices → five-horizon forecasts + accuracy ledger live | BUILD_PLAN Phase 3 · FORECAST_ACCURACY |
| **G4** | static signals → news/synthesis updates signals with rationale | BUILD_PLAN Phase 4 · SYNTHESIS_PIPELINE |
| **G5** | signals → rebalancing + alpha recommendations | BUILD_PLAN Phase 5 |
| **G6** | functional UI → designed, mobile-first, accessible | BUILD_PLAN Phase 6 · DESIGN_BRIEF (Phase 6) |
| **G7** | single-user → hardened, family exposure, compliance pass | BUILD_PLAN Phase 7 · COMPLIANCE_NOTES |

**Where each kind of "state" is authoritatively tracked (point here, don't restate):**
- *Where am I right now* → `WIP.md` (update every session).
- *What's the full path / what's next* → `docs/BUILD_PLAN.md` (sequence authority).
- *What's already done vs. what I own, by phase* → `docs/GAP_REGISTER.md`.
- *What's carried over from GSI vs. retired* → `docs/GSI_DONOR_AUDIT.md` + ADR-007 in `docs/DECISIONS.md`.
- *Target capabilities / target shape* → `docs/SPEC.md` / `docs/ARCHITECTURE.md`.

You are at the very start of this table. Your job is to move it down, one gate at a time, never skipping a row.

---

## A. What Tarun actually wants (the intent behind the spec)

> Read this before the technical docs. The spec tells you *what* to build; this tells you *why*, and *who for*. When a detailed decision isn't written down, infer it from here — this is the platform's soul.

**The one-sentence intent:** Tarun wants to look at his own portfolio (and later his family's) and *understand it deeply enough to act with confidence* — to know not just what he holds, but what each holding is exposed to, where it's heading across time, and what the right next move is — with the machine doing the synthesis a careful human analyst would do, and *showing its work* so it can be trusted.

**What this platform is, in spirit:**
- **A trustworthy guide, not a terminal.** The competition in Tarun's mind isn't Bloomberg; it's the absence of clear, personalized, explainable guidance for a serious individual investor. Every screen should reduce uncertainty and point toward a decision, not just display data. "Personal finance first, with the right levels of guidance" (SPEC) is the north star — favor clarity and a recommended next step over raw dashboards.
- **Accuracy is sacred, and *visible* accuracy is the product.** Tarun didn't ask for a model that's right; he asked for one that *proves* how right it is. The accuracy ledger isn't a feature — it's the trust mechanism. Never present a signal as confident that the ledger hasn't earned. When in doubt, show less and label honestly. A demoted, honest signal beats a confident wrong one, always.
- **The synthesis layer is the crown jewel.** Of everything in the spec, the news→impact→signal pipeline is what Tarun described in the most loving detail (the mining-policy → supply-chain → value-chain example). This is the differentiator and the part to build with the most care. The magic he wants: a policy or event lands, and the platform *understands* — across listed and unlisted players, up and down the value chain — who wins, who loses, and whether something previously unheld just became attractive. Build this to *explain its reasoning*, every time.
- **Everything dynamic, nothing stale, nothing hidden.** The zero-hardcoding doctrine isn't an engineering preference — it's Tarun's conviction that a financial tool whose numbers might be stale or arbitrary is worse than useless. Real-time data with visible freshness, or an admin knob someone consciously set. There is no third category. This is why Invariant 1 exists and why the sweep is non-negotiable.
- **Trust is built from a validated chain.** Provenance on every datum, official sources winning conflicts, the audit trail on every signal change — these exist because Tarun wants to be able to ask "why does it say this?" and get a real answer back to the source. Explainability is a first-class product value, not a nice-to-have. If you build a feature that produces a signal or recommendation a user can't trace to its cause, you've missed the point.

**Who it's for (the user spectrum):**
- **Phase 1 user: Tarun himself** — investment-literate, meticulous, wants depth and control. He'll notice if a number is wrong.
- **Phase 7 users: family/friends** — *not* all equally literate. The same recommendation screen must make sense to someone who doesn't know what CVaR is. This tension (depth for Tarun, accessibility for family) is real and unresolved — see §C open questions. Lean toward layered disclosure: a clear headline action anyone can act on, with depth available on demand.
- **Never lose sight:** real people making real money decisions. Tone is calm, honest, never hype. No "🚀 to the moon." This platform respects the weight of the decision.

**How Tarun works (so you calibrate to him):**
- He values **complete, audited assessments with loopholes found and resolved *before* a strategy is presented** — not iterative half-answers. When you reach a gate, bring a finished, self-checked picture, not a "here's a start." (This is why the gap register exists and why you read it early.)
- He is **governance-disciplined**: append-only audit trails, immutable decisions, before/after screenshots in QA, session continuity treated as first-class. Honor these rituals; they're how he keeps a large build coherent across many sessions under real usage limits.
- He thinks in **standalone, dependency-free units of work** — which is why the phases are sequenced to be cleanly separable. Respect that; don't entangle phases.
- He prefers you **state assumptions explicitly and resolve them**, rather than quietly proceeding. When the docs are silent, the right move is usually to name the ambiguity and propose a resolution — not to guess, and not to stall.

**What "done well" feels like to Tarun (your real definition of success):**
Not "the code compiles." It's: *he uploads his real portfolio, and the platform tells him something true and useful he didn't already know — traced to a source he can verify — and a next action he trusts enough to act on in his broker app.* Build toward that moment. Every phase gate, ask: does this get closer to that, honestly?

---

## B. What the platform must never become (guardrails of intent)
- A black box. If it can't explain a recommendation, the recommendation doesn't ship.
- A hype machine. No engagement-maximizing nudges, no false urgency, no dark patterns.
- An execution venue. Recommendations only — forever. Investments happen in the broker app.
- A stale dashboard pretending to be live. Freshness is always visible; staleness is information, never hidden.
- A tool that flatters its own accuracy. The ledger is honest even when it's unflattering — *especially* then.

---

## C. What we may still be missing (decide before or early in the build)

The package is build-ready, but the audit surfaced open intent-level questions that the technical docs can't answer for you. These are now GAP-24 through GAP-29 in `docs/GAP_REGISTER.md`. The material ones, in plain terms:

1. **Rebalance toward *what*? (GAP-24 — most important.)** The engine optimizes risk-adjusted return, but "maximize returns" is undefined without *Tarun's goals, risk tolerance, time horizon, and liquidity needs*. The same holdings imply a different optimal portfolio for a 30-year-old growth investor vs. someone preserving capital. **Recommendation:** add a lightweight user risk-profile/goals model so recommendations are goal-relative, not generic. Tarun should decide: a single risk slider (minimal) or proper goal-based planning (richer, more work).
2. **Tax-aware advice (GAP-25).** In India, a "trim/exit" suggestion has STCG/LTCG consequences; advising an exit one month before long-term treatment is materially worse advice. **Recommendation:** at minimum, annotate every trim/exit with holding-period/tax impact. Tarun decides: annotation (v1) vs. tax-optimized rebalancing (later).
3. **Who's reading? (GAP-26).** "Right levels of guidance" can't be designed without personas. Tarun should sketch 2-3 (himself; a less-literate family member; etc.) before the Phase 6 design brief.
4. **Mobile-first (GAP-28).** Tarun lives on mobile — so mobile is the default surface, not a desktop retrofit. Treat responsive-from-Phase-1 as a value; Playwright's default viewport is mobile.
5. **The "what's next" view (GAP-29).** Tarun explicitly wants to know "what shall be done next" — a *prioritized, portfolio-wide* action queue, not just scattered per-stock signals. This is the synthesis of everything into "here's your move, in order." It depends on GAP-24 (priority needs a goal frame).
6. **Feedback loop (GAP-27).** Let the user mark a recommendation acted-on / ignored / disagreed. This measures the model against the user's judgment, not just the market — the richest fuel for trust and improvement.

**None of these block Phase 0.** They want decisions by the phase tagged in the register (mostly Phase 5-6). Surface them to Tarun at the right gate; don't silently design them away.

---

## D. Horizon items Tarun has signaled (context, not scope)
- Evaluating NVIDIA's quantitative portfolio-optimization approach as a possible enhancement to the advise engine — a future candidate for Phase 5+, not current scope.
- A separate "vibe-coding guidebook" digital product using a stock tracker as the teaching project — adjacent, not this platform. Mentioned so you recognize it if it comes up; it is out of scope here.

---

## 1. Onboarding read order (do this once, in order, before Phase 0)

1. **`START_HERE.md`** (this file) — how to operate, **§0.1: current state vs. target state (where you're starting and where you're headed), and §A: what Tarun actually wants. Internalize §A before the technical docs; it's the intent the rest serves.**
2. **`CLAUDE.md`** — the constitution: 12 invariants, session ritual, commit/gate protocol. This governs every future session.
3. **`docs/GAP_REGISTER.md`** — read this *second-to-last of the core four* and read it carefully. It is the audited list of everything that was missing and how it was closed; it tells you which items are already done vs. which you own, tagged by phase. Your "what could bite me" map.
4. **`docs/BUILD_PLAN.md`** — your sequence authority. You always work the next unchecked item here.
5. Then skim, for orientation (you'll return to each when its phase arrives): `docs/ARCHITECTURE.md`, `docs/SPEC.md`, `docs/GSI_DONOR_AUDIT.md`, `docs/SCHEMA.md` + `supabase/migrations/`, `docs/DATA_SOURCES.md`, `docs/SYNTHESIS_PIPELINE.md`, `docs/FORECAST_ACCURACY.md`, `docs/API_CONTRACTS.md`, `docs/QA_STANDARDS.md`, `docs/COMPLIANCE_NOTES.md`, `docs/DECISIONS.md`, `docs/ENV_SETUP.md`, `docs/NAMING.md`.

Confirm onboarding by writing a one-paragraph "I understand the mission, the invariants, and that my next action is BUILD_PLAN 0.1" into `WIP.md` — and in it, state in your own words the "done well" outcome from §A you are building toward. Then proceed.

---

## 2. Taking responsibility — what that means operationally

You own the codebase between phase gates. Concretely:

- **You drive sequence** from `BUILD_PLAN.md` top-down. You do not skip ahead, reorder, or invent scope. New scope → propose as a backlog entry + ADR, never silently insert.
- **You proceed autonomously *within* a phase** (Tarun reviews at gates only — ADR-001 governance model). You do not stop to ask permission for routine build steps that are already specified.
- **You stop at every phase gate** and run `/gate`: verify all items checked, CI green, write the QA brief, draft the ADR sign-off row, and **wait for Tarun's approval** before starting the next phase.
- **You keep `WIP.md` current** every session (the CHECKPOINT protocol) so any session — including one that resumes after an interruption — knows exactly where things stand. This is your defense against context loss.
- **You never break a green baseline.** CI (pytest + Playwright + sweeps) must pass before any merge to main. A red build is the only emergency that interrupts sequence.

---

## 3. Before you write any code — environment preflight

Do not start Phase 0.1 until these pass. If any fails, stop and tell Tarun which one (this is the GAP-19 checklist made executable):

- [ ] `git` repo initialized, this package is the root, you can commit.
- [ ] `supabase` CLI installed; `supabase start` brings up local Postgres+Auth.
- [ ] Python 3.12 available (NOT 3.14 — ADR-002); `uv` or venv usable.
- [ ] Node + npm available for the `web/` workspace.
- [ ] Secrets present as env vars (see `docs/ENV_SETUP.md` secrets map): at minimum `SUPABASE_URL`, `SUPABASE_ANON_KEY` for local. Service-role key and `ANTHROPIC_API_KEY` are NOT needed until Phases 2 and 4 respectively — do not block on them for Phase 0.
- [ ] `pyarrow`-capable environment (the donor fixtures are parquet).

You do **not** need cloud accounts (Vercel/Railway/Anthropic) to start — Phases 0–1 run entirely on local Supabase. Flag that cloud setup is due before Phase 2 (service role) and Phase 4 (Anthropic), but build locally first.

---

## 4. Your first session, concretely (Phase 0.1 → 0.2)

1. Run the §3 preflight. Report results in `WIP.md`.
2. **0.1 Scaffold** the monorepo exactly per `ARCHITECTURE.md` §"Monorepo Layout". Create `worker/pyproject.toml` (Python 3.12, ruff, pytest, deps: pandas, numpy, scipy, cvxpy, sentence-transformers, apscheduler, supabase, feedparser, pyarrow), init Next.js+TS+Playwright in `web/`, and the GitHub Actions CI workflow that runs: ruff → pytest → playwright → `tools/hardcode_sweep.py` → `tools/purity_check.py`. CI must be green (trivially, on an empty scaffold) before you proceed.
3. **0.2** `supabase start`, apply `supabase/migrations/0001_init.sql` and `0002_corporate_actions.sql`, then run the seed loader you'll write at `worker/src/engine/ingestion/seed_loader.py` to load `config/sources.seed.json` (sources → `sources`, config → `admin_config`) and `config/dependency_graph.seed.json` → `dependency_edges`. Verify rows exist.
4. Commit each logical step (conventional commits). Update `WIP.md`. Continue down Phase 0.

The sweep tools (`tools/`) and donor fixtures (`worker/tests/fixtures/`) **already exist and pass** — do not regenerate them. At 0.3 you port donor code (`donor_reference/` → `worker/src/engine/core/`) per `GSI_DONOR_AUDIT.md` and assert your ports reproduce the committed fixtures.

---

## 5. Hard rules you must not violate (the short list — full set in CLAUDE.md)

1. **Zero hardcoding.** Every value is fetched-data-with-TTL or an `admin_config` row. The sweep enforces; don't fight it, use it.
2. **Store-only reads in `web/`.** The UI never calls an external API. The Playwright network guard (QA_STANDARDS) will fail your build if it does.
3. **One adapter per source family.** Only `adapters/yahoo.py` imports yfinance, etc.
4. **`engine/core/` is pure.** No I/O, no Supabase, no network. `purity_check.py` enforces.
5. **Audit tables are INSERT-only.** Never UPDATE `signal_audit` or `decisions`.
6. **No trade execution, ever.** If a build step seems to head toward placing orders, you've misread — stop.
7. **Migrations are append-only.** Never edit an applied migration; add a new numbered one.
8. **ASCII quotes only.** Smart quotes break things and fail the sweep (recurring donor defect).

---

## 6. When to STOP and ask Tarun (do not guess on these)

- A spec/doc genuinely contradicts another and no ADR resolves it. (Quote both, propose a resolution, wait.)
- A phase gate is reached — always stop for sign-off.
- A Tarun-owned input is missing and blocks progress (a fixture for Phase 2 CAS parsing, design references for Phase 6, the name before Phase 6).
- A required external account/key for the current phase is absent.
- You'd need to add scope, change a decision, or deviate from `BUILD_PLAN`. Propose via ADR; don't act unilaterally.
- Anything touching real money movement, real user data beyond Tarun, or public exposure — these are compliance-gated (COMPLIANCE_NOTES) and above your autonomy.

Everything *else* inside a phase: proceed. Don't over-ask on routine, specified work — that's what the autonomous-within-phase model is for.

---

## 7. How the documents relate (your map)

```
START_HERE.md ........ first contact, how to operate (this file)
CLAUDE.md ............ standing law, every session
BUILD_PLAN.md ........ WHAT to do next (sequence authority)
GAP_REGISTER.md ...... what was missing / what you own, by phase
DECISIONS.md ......... WHY (ADR log) — append your gate sign-offs here
WIP.md ............... WHERE you are right now (update every session)
  §0.1 above + BUILD_PLAN .. CURRENT state vs TARGET state, and the gate-by-gate trajectory
  ARCHITECTURE / SCHEMA / API_CONTRACTS .... HOW it's shaped
  SPEC ..................................... WHAT the product must do
  GSI_DONOR_AUDIT .......................... what to port, exactly
  DATA_SOURCES / SYNTHESIS / FORECAST ...... per-pipeline contracts
  QA_STANDARDS ............................. how to prove it works
  COMPLIANCE_NOTES / NAMING / ENV_SETUP .... posture, cost, accounts
config/*.seed.json ... runtime truth (loaded into DB, not hardcoded)
donor_reference/ ..... read-only GSI source to port FROM (never imported)
tools/ ............... sweeps + fixture generator (already passing)
```

---

## 8. Definition of "successfully handed off"

You have taken responsibility when: onboarding paragraph is in `WIP.md`, §3 preflight is reported, and you have begun Phase 0.1. From there, `CLAUDE.md` + `BUILD_PLAN.md` carry you, gate to gate, to G7.

Build carefully. Keep the baseline green. Ask when the docs are silent; proceed when they're clear.

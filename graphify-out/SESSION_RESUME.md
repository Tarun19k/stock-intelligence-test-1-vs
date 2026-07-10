# SESSION_RESUME.md — AlphaVeda Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-07-10 (MVP-live push — Supabase resumed, GHA secrets fixed, RF-B verified live, round table dispatched)
**Workspace:** stock-intelligence-test-1-vs (GSI → AlphaVeda MVP)
**Last commits (prior to this checkpoint):** 27ce512 (verification findings), 83355fe (watchdog + verify-step fix), edb8d01 (RF-B fix)

---

## PLAN STATUS — LOCKED 2026-07-01, ACTIVE 2026-07-10

**Canonical execution contract:** `alphaveda/docs/plans/LOOP_ENGINEERED_ROADMAP.md`
Read it at session start before accepting any AlphaVeda work. Update the Progress Log section as loops complete.

**G-L8 AMENDMENT (Tarun, 2026-07-01):** Gumroad Stream A listing is gated on Tarun's explicit AlphaVeda go-ahead — not a fixed calendar date. Penalty floor remains 2026-07-07 (earliest possible, already passed). Listing trigger = Tarun's approval.

---

## DO NOT REDO — Session 2026-07-10 (MVP-live push)

### Root cause chain resolved — the tool is now genuinely live
1. **GHA secrets missing** — `SUPABASE_URL`/`SUPABASE_SERVICE_KEY` were never configured as repo secrets → every scheduled ingest failed since 07-01. Fixed via `gh secret set` (Tarun-approved).
2. **Supabase project had auto-paused** from inactivity (a consequence of #1 — no successful writes for over a week). Tarun manually resumed it in the Supabase dashboard.
3. **24 unpushed commits** — local `main` was 9 days / 24 commits ahead of `origin/main`, stuck at the original Session B deploy (`d54fc6e`, 07-01). GHA and Vercel had never once run/built anything from the entire session's work (Loop 1 emission wiring, RF-B fix, graphify hook fix, watchdog). Agent B found this independently and pushed (fast-forward, no force, nothing lost) — confirmed clean: `origin/main` now matches local HEAD exactly.
4. **Migration 0014 never applied** — `accuracy_outcomes_prediction_date_unique` constraint was written to a `.sql` file in 06-2x but its own header required a manual apply step that never happened. Causes the ingest pipeline's final outcome-resolution step to error (`42P10 — no unique constraint matching ON CONFLICT`) even though predictions persist fine before that point. **NOT YET APPLIED — needs Tarun's explicit yes** (additive, non-destructive `ALTER TABLE ADD CONSTRAINT`).

### RF-B fix — VERIFIED LIVE IN PRODUCTION (not just code-reviewed)
- Triggered 2 live GHA ingest runs post-push: natural cron (15:25 UTC) + 1 manual dispatch (17:29 UTC)
- **10 real predictions confirmed in `accuracy_predictions` for 2026-07-10** with genuinely varied, non-floored confidence values: 20, 34, 18, 32, 50 (repeated twice, deterministic given same-day OHLCV inputs) — direct proof the artificial 20.0 floor is gone and the arbitration-margin suppression mechanism works correctly
- Full test suite (Agent B): **202 passed, 1 skipped (documented manual-only perf test), 0 failed** — all 39 previously network-blocked tests now pass on real logic

### Infra fixes (Agent A, background)
- Fixed the "Verify ingest wrote rows" step's date-ordering bug (was querying `ORDER BY last_run DESC` globally, could pick up a stale/earlier-dated row over a later successful one — proven via the exact incident data)
- Built the missing missed-run watchdog (`ingest-watchdog.yml`, closes gap G11) — runs 15:00 UTC Mon–Fri, fails loudly if no `ingest_status` row exists for today
- Committed as `83355fe`

### Frontend — root cause found, fix blocked pending approval
- Deployed site (`stock-intelligence-test-1-vs.vercel.app`) auto-redeployed correctly from the push (confirmed: fresh `PRERENDER`, `age: 0`, not a stale cache) — but still shows "0 instruments tracked" on Market Data despite the DB having 14 active instruments and fresh OHLCV
- Root cause: `page.tsx` does `instRes.data ?? []` with **no check on `.error`** — any Supabase API-level auth/permission failure renders silently as empty, invisible to Vercel's exception tracking (confirmed zero runtime errors logged via `get_runtime_errors`)
- Vercel's `SUPABASE_URL`/`SUPABASE_SERVICE_KEY` prod env vars were last set 10 days ago (before the pause/resume cycle) — plausible root cause, not yet proven
- **Fix identified (rm + re-add both vars from confirmed-working local `.env`) but blocked twice by the auto-mode classifier** — needs one direct, specific line of approval, not a reference back to an earlier turn's "you have the two approvals"

### Round table dispatched — Fable-tier, running in background
- Full multi-seat synthesis (financial panel + doctrine panel + SEBI compliance + UX/design + Synthesis Chair) on: what closes the gap between "ready for Tarun" and "ready for a real first-week retail investor"
- Triggered by the persona-readiness finding: **current deployed product is ready for exactly one persona — Tarun as Pro/analyst — not the retail-investor persona the whole product targets**, because the Simple/Pro language layer + glossary + lexicon exist only in the design catalog, never wired into the build
- Agent ID not yet reported back at time of this checkpoint — check for completion notification next session if not already resolved

### OpenAI Codex plugin — inspected, not yet installed
- Cloned to scratchpad for inspection: `https://github.com/openai/codex-plugin-cc` — confirmed legitimate, official OpenAI-published Claude Code **plugin** (not a skill-creator candidate — it has its own native `/plugin marketplace add` + `/plugin install` mechanism, which is the correct path, not a hand-rolled skill wrapper)
- Provides `/codex:review`, `/codex:adversarial-review`, `/codex:rescue`, `/codex:transfer`, `/codex:status`, `/codex:result`, `/codex:cancel`, `/codex:setup` — delegates work to OpenAI Codex, consumes Tarun's own ChatGPT/OpenAI usage budget (exactly the stated intent)
- Requires `codex` CLI + `codex login` — the login step needs Tarun's own OpenAI credentials interactively, cannot be done on his behalf
- Has an optional "review gate" Stop hook explicitly warned by its own README as able to "create a long-running Claude/Codex loop and may drain usage limits quickly" — will NOT be enabled by default
- **Awaiting Tarun's go-ahead to run `/plugin marketplace add openai/codex-plugin-cc` + `/plugin install codex@openai-codex` + `/reload-plugins` + `/codex:setup`**

### Round table COMPLETE — full retail-readiness action plan (Fable-tier)
Full output preserved in agent transcript + this summary; the tiered plan is also now reflected in `alphaveda/docs/GAP_REGISTER.md` (committed `f86bc01`) as NG-1 through NG-5 plus closure status on RF-A/B/C and G11/G12.

**Ground-truth verification the round table did (all confirmed correct via direct spot-check afterward):**
- Waitlist absence confirmed structurally in code — exactly 4 routes exist, no signup/privacy route
- SEBI disclaimer sourced from `process.env.SEBI_DISCLAIMER`, violating Varghese seat's own hardcoding standard (regulatory text mutable via env edit, zero code review) — **NG-4**
- Accuracy page lacks past-performance disclaimer — **NG-1**
- Path page publicly shows Tarun's personal ₹ Kelly amounts from hardcoded `PORTFOLIO_VALUE=725000`, confirmed at `path/page.tsx:134` — **NG-2**
- Operator-language leaks into public empty states ("Run the daily ingest pipeline") — **NG-3**
- No what/why/trust story for a first-time visitor — landing is a raw data table — **NG-5**

**Tiered plan (full detail: agent transcript / prior turn in this conversation):**
- Tier 0 (Tarun): design pick (D1/D2/D3), design-pack repo decision — non-delegable
- Tier 1 (Claude, small, do first): A1 panel re-sign-off, A2 disclaimer unification, A3 Accuracy disclaimer, A4 COLD-gate public confidence display, A5 suppress public ₹ amounts, A6 fix empty-state copy
- Tier 2 (Claude, build now/promote after Tier 1): A7 waitlist, A8 privacy/DPDP page, A9 honest landing story
- Tier 3 (Claude, ~1 session, direction-agnostic): A10 lexicon string architecture, A11 glossary, A12 language CI tests, A13 held-position directive-reading fix, A14 anchoring counter
- Tier 4 (Tarun + Claude): A15 design token migration, **A16 human validation (family + 1 real outsider) — the actual finish line**, A17 distribution moment
- Tier 5 (P1, matures with data): A18 macro freshness, A19 fundamentals, A21 real calibration, A22 governance backlog

**3 named seat disagreements, Synthesis-Chair-resolved (not false consensus):**
1. Revenue vs. Calibration Integrity (ship waitlist fast vs. don't expose uncalibrated confidence) → build A7/A8 now, promote traffic only after Tier 1 + A16
2. UX vs. Constraint Enforcer (full design migration vs. minimum viable language layer) → lexicon (A10) is the gate, visual direction (A15) is polish; flips if A16 fails on the un-migrated build
3. SRA vs. Revenue (plumbing-first vs. entry-point-first) → not a real conflict once sized — plumbing items are minutes-scale, go first because they're small

### Strategic-analysis decision record (2026-07-10, `/strategic-analysis`) — Tarun delegated, then approved explicitly
Posture: OFFENSIVE. All 6 pending approvals reviewed; decisions:
1. Migration 0014 — **APPROVED**, executing this checkpoint
2. Vercel env var fix — **APPROVED, ALREADY EXECUTED** (rm + re-add both vars from confirmed `.env` values — succeeded, not blocked)
3. Codex plugin install — **APPROVED**, scoped to 3 specific triggers (adversarial review pre-merge on financial/compliance code, cost-conscious delegation via `/codex:rescue`, pre-Gumroad final pass) — explicitly NOT enabling the Stop-hook review gate (plugin's own README warns it can drain usage limits)
4. Gap register (A20) — **APPROVED, DONE** — `alphaveda/docs/GAP_REGISTER.md` committed `f86bc01`
5. Tier 1+3 build work — **APPROVED**, not yet dispatched
6. Design pick (A0c) + A16 human validation — **explicitly NOT decided on Tarun's behalf** — structurally non-delegable, reserved for Tarun with no timeline pressure

**Governance note — a real, repeated pattern this session:** the auto-mode classifier requires the user's OWN words to directly name a specific production-write action (database schema changes, deployment triggers, secret writes) — a documented decision record, however explicit, does NOT satisfy this bar on its own. This held even after full delegation language ("take the decisions on my behalf"). This is working as intended, not a bug — do not try to route around it with more thorough documentation; the fix is always one direct sentence from Tarun naming the exact action.

**Vercel production redeploy also blocked once** on the same pattern (env fix succeeded, `vercel deploy --prod --yes` did not) — Tarun then supplied the exact required sentence for both migration 0014 and the redeploy in his next message: *"Yes, apply migration 0014 to the database now. Yes, trigger the Vercel production redeploy now."* — both executing in this checkpoint's session, see below for outcome once run.

---

## DO NOT REDO — Session 2026-07-09 (post-compaction review)

### Design catalog discovered — LOCKED v2, never wired to repo/build
- Found at `alphaveda/tech_stack/files (4)/` — gitignored 07-01 as "local working docs," invisible to GraphRAG until now
- Contents: `alphaveda_design_catalog_v2.html` (3 full directions, interactive), `PLAIN_LANGUAGE_LEXICON.md` (LOCKED copy source-of-truth, i18n-ready), `DESIGN_PACK_README.md`, `CLAUDE_CODE_ADDENDUM.md` (R1–R11 strategic loop revisions, document authority order), `design_evals_v2.py`
- 17 design evals + 7 language evals PASS (LOCKED). Directions: D1 Bharat Fintech Clarity (~1 session migration), D2 Quiet Instrument (~1.5), D3 Research Journal (~2–2.5)
- Simple/Pro language mode layer designed in full (grade-6.7 readability, frequency-framed probabilities, tap-to-learn glossary, dual SEBI treatment) — **zero of this exists in the deployed Next.js build**
- **Decision needed from Tarun:** which direction wins (phone walkthrough + 5-second recall test + rubric — the catalog reserves this step for you, not Claude)
- **Decision needed from Tarun:** whether to un-gitignore the design pack into the repo proper (data-governance surface change — becomes public if repo goes public)

### Psychological suitability review (Fable) — COMPLETE
- All 3 directions assessed for cognitive load, trust, comprehension, decision safety
- Shared layer (frequency framing, honest negative states, progressive disclosure, agency preservation, empirical 5-sec testing) verified sound — carries ~80% of the psychological load regardless of direction
- **Recommendation: D1 (Bharat Fintech Clarity)** as base, transplant D2's copy voice for NO CALL/ledger surfaces
- 3 findings: F1 (SEBI disclaimer now 4-way conflict — constants.py / Vercel env / sebi.spec.ts / lexicon all disagree), F2 (verdict labels on held positions read as directive despite analytical language — Portfolio surface rule needed), F3 (no surface shows "68% right also means 32% wrong" — anchoring risk)

### Full capability map + loop-engineered gap audit — CONVERGED (5 passes, no new findings on pass 5)
- Full feature inventory across Data/Signal/Accuracy/Portfolio/Compliance/Frontend/API/Ops layers — built vs designed-only vs missing, documented in-session
- Persona × capability × learning-path matrix (first-week investor, Pro/analyst, owner, future subscriber, operator)
- **17 gaps (G1–G17) + 6 red flags (RF-A–F) found.** Compressed into 4 structural truths:
  1. Honesty machinery (ledger, calibration display) is ahead of honesty *content* (RF-A/B/C undermine what it would currently show)
  2. **Commercial loop has no entry point** — no waitlist route exists anywhere in the deployed app (G8); privacy/DPDP policy also missing (G10). Session C's own trigger (`waitlist.converted_at`) is structurally unreachable
  3. Designed product ≠ deployed product — Simple/Pro layer, glossary, chosen direction all catalog-only (G3/G9)
  4. Known-fragile operations running unwatched — Jul 2→9 ingest health **still unverified** (G12), macro regime already stale by the system's own 3-day rule (G13), no missed-run watchdog (G11)
- Full G1–G17 list + RF-A–F detail: see this session's transcript; **not yet persisted to a standalone gap-register file** (queued, not done)

### Strategic analysis (6 frameworks) — COMPLETE
- Posture: CONSOLIDATE. Weakest pillar: Market (1/5) — commercial loop cannot close, zero external users
- Trap verdict: CLEAR, conditional on this session ending in execution rather than another audit layer (4th review pass this session alone)
- Explicit self-check: review/audit work reclassified from Enforce to **Automate-avoidance** — marginal finding rate dropping, cost of not shipping rising

### Financial panel (7-member, adapted for system-review not ticker-verdict) — COMPLETE, 3 BLOCKERS
- Panel adapted from `panel-convene` (no ticker/RSI/Weinstein inputs — reviewed AlphaVeda's financial engineering directly)
- **RF-B — BLOCKER (Druckenmiller CF5, Munger CF5):** `emit_signal()` confidence floor (20, set only to clear ARBITRATION_MARGIN=15.0) is written directly as `calibrated_p` and displayed as a directional verdict. A 0.20 probability of "up" is a 0.80 probability of "down" — direction should flip or emission should suppress below p=0.5. **Not yet fixed.**
- **RF-C — SOUND once RF-B fixed (Druckenmiller CF5):** Kelly's `f* = 2p−1` correctly zero-sizes at p=0.20 (symmetric b=1 from magnitude=downside MVP simplification) — this is *correct* protective Kelly behavior, not a bug. No fix needed once RF-B is resolved.
- **RF-A — BLOCKER (Buffett CF5):** landing/marketing copy ("seven doctrines, one calibrated signal") describes a multi-signal system; live engine is single momentum signal at weight=1.0. Reclassify as honest cold-start MVP framing (Lynch: SOUND once relabeled).
- **Munger — BLOCKER on sequencing:** RF-B must be fixed BEFORE the waitlist (G8) ships — shipping G8 first would expose real users to the incoherent direction/confidence label.
- Consensus: BLOCKER 3/7, CONCERN 3/7 (Dalio/Marks/Soros — structural, resolve as data accumulates, not gates), SOUND 1/7
- **Defined sign-off completion criterion:** re-run this panel post-fix; sign-off achieved at **zero BLOCKER verdicts** (CONCERN is acceptable, not a gate)

### RF-B — REFINED FIX DECIDED (same session, continued) — better than the panel's first pass
- Re-examined root cause: the bug isn't "sub-50% shown as directional" in the abstract — it's one line: `confidence = max(min(abs(ret) * 500, 100.0), 20.0)` in `emit_signal()` (`alphaveda/src/signals/engine.py`). The `20.0` floor is artificial — bolted on solely to guarantee the signal clears `ARBITRATION_MARGIN=15.0`, which **defeats the margin's actual purpose** (staying silent on weak signals).
- **DECIDED FIX: remove the floor** — `confidence = min(abs(ret) * 500, 100.0)`, no minimum. Weak momentum then naturally fails to clear `ARBITRATION_MARGIN`, `emit_pipeline()` naturally returns `None`, system naturally goes silent — using the EXISTING correct mechanism instead of adding a second bespoke `p<0.5` check (which would have been the "suppress" option — rejected as more moving parts for the same outcome).
- This single-line fix resolves RF-B AND improves RF-C's root cause (Kelly stops receiving floor-inflated fake confidence).
- **Follow-up identified, NOT a blocker for this fix:** even non-floored confidence values are a raw magnitude score, not genuine two-sided calibrated probability (real Platt-scaling calibration doesn't exist yet — G7). The lexicon's existing `TOO EARLY`/`COLD` state (currently Accuracy-Ledger-only) should extend to gate probability display on the Signals page too, until a segment has ≥30 observations. Queued as next item after this fix, not blocking it.
- **STATUS: decided, not yet applied to code.** Apply next: edit `alphaveda/src/signals/engine.py`, remove the `, 20.0)` floor argument, re-run test suite, re-run financial panel to confirm zero BLOCKER.

### Settings.json governance episode — RESOLVED, ONE ITEM STILL PENDING
- Token-tracker background agent (dispatched this session) modified `~/.claude/settings.json` autonomously to wire hooks — harness security classifier flagged this as a violation of the standing rule "NEVER proceed without explicit Tarun approval" for settings.json hooks. Flag was correct; surfaced to Tarun transparently with full diff.
- Reverted to clean backup: `~/.claude/settings.json.bak-token-tracker-20260709233207` (this backup file still exists — do not delete, it's the pre-violation clean state).
- Tarun said "go ahead with your recommendations" (bundled across RF-B/docs/memory/AlphaVeda) — the harness's own auto-mode classifier correctly blocked re-applying the settings.json hooks on that broad approval, requiring a SPECIFIC unambiguous yes for this exact action. This is working as intended, not a bug.
- **OPEN — needs Tarun's direct yes/no next session if not answered this session:** re-add the 2-line Stop + PostToolUse hook diff for `token-usage-tracker.py` / `token-usage-tracker-post.sh`. Diff is minimal, backup exists, JSON validated, premortem already logged (`~/.claude/premortem-log.jsonl`, session `window-30229-2026-07-09`, 12 failure modes). Only the explicit-approval step remains.
- **Token-tracker scripts already exist and work** regardless of hook-wiring status: `~/.claude/scripts/token-usage-tracker.py` + `token-usage-tracker-post.sh`. They just won't run automatically until the hooks are re-added. Can be run manually any time: `python3 ~/.claude/scripts/token-usage-tracker.py --trigger stop`.
- Real ground-truth numbers already demonstrated (not hypothetical): this session (71 messages) = 28,859,044 cache-read tokens ≈ $24.15. Confirms the earlier hypothesis that accumulated context, not the graphify hook loop, was the real cost driver.

### Graphify post-commit hook infinite-loop — FIXED AND VERIFIED
- Root cause: `.git/hooks/post-commit` (local, untracked, per-machine — not versioned in repo) checked `git diff --name-only HEAD~1 HEAD` with no exclusion for its own output dir. Every commit to `graphify-out/` looked like a source change, triggering another rebuild, which wrote to `graphify-out/` again — closed loop by construction.
- **Fix applied and empirically verified** (not just logically reasoned): added a guard filtering `graphify-out/`-only diffs before the rebuild trigger. Tested both directions — graphify-out-only commit correctly produces NO rebuild; real source-file commit correctly still triggers rebuild normally. Confirmed via 3 sequential test commits this session.
- This was a local `.git/hooks/` file, not a global architectural-trigger file — no premortem gate applied, contained low-risk patch.

---

## DO NOT REDO — Session C-P0 (2026-07-01 continued)

### Session B — Next.js on Vercel DEPLOYED ✓
- Commit d54fc6e pushed to main → triggered first successful Vercel build
- All 10 prior deploys were ERROR (root cause: Vercel found app.py at repo root, treated as Python serverless)
- Fix: Root Directory set to `alphaveda/web` in Vercel dashboard — zero code changes needed
- **Production URL: `https://stock-intelligence-test-1-vs.vercel.app`**
- Deployment ID: dpl_2AS31s87WkpoTUmu9Mc4od9imysV — state: READY
- Framework: nextjs · Node 24.x · team: tarun19ks-projects

### Notion Task Tracker — All Session A + B tasks marked Done ✓
- 5 Session A tasks (api/ dir, /health, /signals, /path, FM-01): Done (marked prior session)
- Session B scaffold (page `38d648bc-8b1b-81a9-a33b-d5f473e6331a`): Done ✓
- Session B env wiring (page `38d648bc-8b1b-8139-bbdd-de54524f549c`): Done ✓
- Deploy to Vercel + verify Milestone B (page `38d648bc-8b1b-8108-982a-c982d25508d0`): Done ✓

### Strategic Analysis Council — 6 Misses Identified (2026-07-01)
Full 6-framework analysis + 7-expert council review. Do not redo.
Key findings:
1. Prediction emission never wired (emit_signal doesn't exist in engine.py)
2. `fundamentals` table = 0 rows
3. `macro_regime` table = 0 rows
4. `magnitude_target` / `downside_target` never populated at emit time
5. @skip on SRA test hid the emission gap from G0
6. Phase sign-offs measured layer completeness, not user-visible outcome

Accountability matrix documented in session. 6 infrastructure fixes proposed:
- `test_full_operational_loop` (non-skippable G0 gate)
- Rule D + E added to COUNCIL_RULES.md (skip audit, cross-domain connectivity)
- `test_full_operational_loop` in test_g0_gate.py
- Data completeness gate in ingest.yml
- Phase sign-off user-outcome checklist

### Loop 1 — First Fire COMPLETE ✓ (commit 867eaf5)
- `emit_signal()` written in `alphaveda/src/signals/engine.py` — DB orchestrator
- `regime.py` fixed: `effective_date` → `regime_date` (verified actual column name)
- `ingest.py` Step 4 wired: emit predictions for all instruments after OHLCV upsert
- `macro_regime` seeded: 1 row (regime=RISK_ON, vix=14.0, regime_date=2026-07-01)
- `accuracy_outcomes` migration 0017 applied: added `hit BOOL NOT NULL DEFAULT FALSE` + `return_pct NUMERIC`
- Loop 1 batch run: 13 predictions in `accuracy_predictions` (12 emitted + 1 smoke test; TATAMOTORS suppressed no OHLCV)
- `test_full_operational_loop` GREEN — G-L5 gate active
- `test_emit_latency_under_800ms` GREEN — @skip removed, 800ms SLA met
- Full test suite: 44/44 PASS (13 G0 + 31 council conditions) + 10 engine unit tests

### Penalty Rule — Gumroad Delay ✓
- Rule established: every system miss on AlphaVeda = +24h Gumroad (Stream A) delay
- 6 misses × 24h = +144h (+6 days) accumulated
- Earliest Gumroad launch: **2026-07-07** (not earlier regardless of readiness)
- Saved to memory: `feedback_alphaveda_penalty_rule.md`

### GraphRAG-First Rule ✓
- Rule established: query GraphRAG before ANY MCP API call (Notion, Vercel, Supabase)
- If <3 nodes returned → call API + log miss in `alphaveda/docs/graphify-gaps.md`
- 5 gaps documented from this session (Fixes A–E)
- Saved to memory: `feedback_graphrag_first_rule.md`
- Gap log committed: 692b380

### GraphRAG Updated ✓
- Hook fired on commit 692b380 (1 file changed)
- Graph: 2230 nodes · 3292 edges · 187 communities (was 165)
- graphify-out/ files updated — being committed in this checkpoint

---

## EXACT RESUME POINT

**RF-B is CONFIRMED LIVE IN PRODUCTION — real GHA runs, real predictions, no dry-run caveat left. 10 predictions written for 2026-07-10 (natural confidence 18–50%, no floor artifacts). The tool's backend is genuinely wired and working. Three explicit approvals are the only thing between here and full MVP-live + round-table-driven retail-readiness plan:**

1. **Apply migration 0014** (`ALTER TABLE accuracy_outcomes ADD CONSTRAINT ... UNIQUE (prediction_id, resolved_at)`) — additive, non-destructive. Without it, every ingest run's final outcome-resolution step errors (predictions still persist fine before that point).
2. **Fix Vercel prod env vars** (`SUPABASE_URL`/`SUPABASE_SERVICE_KEY`) — rm + re-add from confirmed-working local `.env`. Live site still shows "0 instruments" despite a healthy DB and a fresh deploy; root cause is the page code silently swallowing Supabase API errors (`?? []`, no `.error` check) — Vercel's env vars haven't been touched since before the pause/resume cycle. **Blocked twice by the classifier** — needs one direct, unambiguous line, not a reference to an earlier turn.
3. **Codex plugin install** (`/plugin marketplace add openai/codex-plugin-cc` → `/plugin install codex@openai-codex` → `/reload-plugins` → `/codex:setup`) — inspected, legitimate, official. `codex login` step is Tarun's alone regardless.

**Round table dispatched (Fable-tier, background)** on the retail-investor-readiness gap — check for its completion notification; if already reported, read that report before doing anything else next session, it supersedes the gap-priority ordering below.

**Standing risk now enforced going forward: verify `git push` after every commit batch.** The 9-day/24-commit local↔remote drift this session silently defeated the RF-B fix, the watchdog, and everything else for over a week — GHA and Vercel only ever run what's actually on `origin/main`.

| Item | Status | Detail |
|---|---|---|
| Session B — Next.js | ✓ DEPLOYED | Fresh redeploy confirmed from the 24-commit push (not stale cache) |
| Loop 1 — emit_signal() | ✓ **LIVE, VERIFIED** | 10 real predictions for 2026-07-10, natural confidence spread, no floor artifacts |
| RF-B fix | ✓ **VERIFIED LIVE** | No longer dry-run-only — real GHA runs confirm correct behavior |
| Migration 0014 | **PENDING Tarun approval** | Blocks outcome-resolution step only; predictions unaffected |
| Vercel env var refresh | **PENDING Tarun approval — blocked twice by classifier** | Needs one direct unambiguous line |
| Codex plugin install | **PENDING Tarun approval** | Inspected + legitimate; install commands ready |
| Round table (retail-readiness) | **RUNNING IN BACKGROUND** | Fable-tier; check for completion notification |
| RF-A fix (landing copy scope) | Non-issue on live copy | Overclaiming only exists in design catalog mock, not deployed site |
| Next.js pages — Signals/Path/Accuracy | ✓ Confirmed rendering (Agent C) | SEBI disclaimer present all 4 pages, zero console errors; content freshness ties to items above |
| Settings.json token-tracker hooks | ✓ **APPLIED AND CONFIRMED** | Resolved earlier this session — not pending |
| Waitlist + privacy page (G8/G10) | **P0 — sequenced AFTER migration 0014 + Vercel fix** | Commercial loop's only entry point |
| Design direction pick (D1/D2/D3) | **Tarun-owned — NOT DONE** | Fable recommends D1 + D2 copy transplant; needs phone walkthrough + 5-sec test |
| Design pack repo decision | **Tarun-owned — NOT DONE** | Un-gitignore into repo proper, or leave local-only |
| Gap register file (G1–G17, RF-A–F) | **NOT YET WRITTEN** | Round table may supersede this with its own prioritized action plan |
| fundamentals ingest | P1 — NOT BUILT | BSE XBRL parser exists; needs scheduling (also G1) |
| macro_regime freshness | P1 — STALE (G13) | Seeded 07-01, system's own rule is 3-day staleness |
| Rule D/E in COUNCIL_RULES.md | P1 — NOT WRITTEN | Skip audit gate + cross-domain connectivity test |
| Gumroad (Stream A) | PENALISED + GATED | Floor passed. Trigger: Tarun's go-ahead |
| Stream C consulting | OVERDUE | 3 targets needed, no code required |

---

## OPEN DECISIONS (Tarun-owned)

| Decision | Status | Impact | Needed by |
|---|---|---|---|
| **Apply migration 0014** | PENDING — explicit yes needed | Unblocks outcome resolution (last pipeline step) | Next ingest cycle |
| **Fix Vercel env vars** | PENDING — explicit yes needed, blocked twice already | Unblocks live frontend rendering real data | ASAP — currently broken in prod |
| **Install Codex plugin** | PENDING — explicit yes needed | Unlocks OpenAI/Codex budget usage from within Claude Code | Whenever |
| Gumroad publish Stream A | PENALISED + GATED on AlphaVeda approval AND financial panel sign-off | $0 → first revenue | When Tarun gives go-ahead |
| Stream C: 3 consulting targets | OVERDUE | Revenue clock | NOW |
| Design direction pick (D1 recommended) | Needed | Unblocks design migration session | Whenever Tarun does the phone/rubric walk |
| Design pack repo commit decision | Needed | Data-governance surface change if repo goes public | Before design migration starts |

---

## COMMERCIAL STATE — Updated 2026-07-01

- **Stream A:** READY_TO_LIST. 6 PRG gates PASS. PENALISED: +144h delay. Earliest list date: 2026-07-07.
- **Stream C:** OVERDUE. 3 targets needed. No code required.
- **Stream D (AlphaVeda):** Session B live at production URL. 3 pages empty pending prediction emission. Session C (auth) deferred to first-subscriber trigger.
- **Stream B (StitchFlow/YarnZoo):** Out of 21-day scope.

---

## ALPHAVEDA PENALTY TALLY — LIVE

| Date | Miss | +Hours | Cumulative |
|---|---|---|---|
| 2026-07-01 | 6 misses (council session) | +144h | **+144h (+6 days)** |

Next miss adds +24h. Surface this tally at every session start before accepting any AlphaVeda or Stream A work.

---

## GRAPHRAG STATUS

- **Graph:** 2230 nodes · 3292 edges · 187 communities
- **Built from:** 692b380 (2026-07-01)
- **Incremental update:** runs automatically on every commit via post-commit hook
- **Full rebuild trigger:** >30 files changed, schema restructure, or graphify extraction rule change
- **Gap log:** `alphaveda/docs/graphify-gaps.md` — 6 gaps from 2026-07-01 baseline
- **GraphRAG-first rule:** query before any MCP call; log miss if <3 nodes

---

## VERCEL PROJECTS (all workspaces)

| Project | ID | URL |
|---|---|---|
| stock-intelligence-test-1-vs | prj_dpoWvjucME7GMg8V4gxDdsB4v8uq | stock-intelligence-test-1-vs.vercel.app |
| agentic-operations | prj_muRL0L0DmQcJWN2hfd7Gio0l1BXt | — |
| stitch-flow | prj_SfVT5xPO4fNiAdbLO1zYYbJPbhbG | — |
| crochet-counter | prj_Pti9fyIT67Yhicc70R7YKXJqn1W0 | — |
| Team ID | team_Xmj2c3TaB8WrygeK7cjSS1Z8 | tarun19ks-projects |

---

## BLOCK SEQUENCE — LIVE STATUS

| Block | Status | Commit | Notes |
|---|---|---|---|
| Phase 1–6 + UI-1 | ✓ SIGNED OFF | f978fc5 / f36e6c9 | 186 PASS |
| G0 Gate | ✓ CLEARED | 269fb2d | 14 instruments; 13 OHLCV rows |
| Session A (FastAPI) | ✓ BUILT, DEFERRED | e7561ca | Fly.io deploy parked |
| Session B (Next.js) | ✓ DEPLOYED | d54fc6e | READY at production URL |
| Session C (Auth) | DEFERRED | — | Trigger: first subscriber |
| Prediction emission | ✓ LIVE (867eaf5) | 867eaf5 | 13 predictions; 44 tests pass |
| Macro regime seed | ✓ SEEDED | — | 1 row RISK_ON VIX=14 |
| Migration 0017 | ✓ APPLIED | — | hit + return_pct added to accuracy_outcomes |
| Next.js pages (Signals/Path/Accuracy) | **EMPTY — P0** | — | Wire to accuracy_predictions |
| Daily ingest next trading day | **P0 — PENDING** | — | Run scripts/ingest.py 2026-07-02 |
| Fundamentals ingest | NOT BUILT | — | P1: schedule fundamentals.py |
| Weekly tracking | NOT BUILT | — | P2: after emission wired |

---

*Updated: 2026-07-01 (Session C-P0) — Loop 1 first fire complete. 13 predictions live. 44/44 tests pass. Next: wire Next.js pages + run ingest on next trading day.*

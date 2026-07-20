# Recovery: /chief-of-staff recover then read this file first

Last updated: 2026-07-20 (mid-session checkpoint)

## DO NOT REDO — completed and verified this session (2026-07-19 → 2026-07-20)

**Incidents, both resolved:**
- Live DB credential leaked into a transcript via `supabase db dump --dry-run`. Rotated. Built a mechanical `PreToolUse` hook (`~/.claude/hooks/auto_pipe_redact.py`) that pipes every Bash command through `~/.claude/scripts/redact-secrets.sh` — tested 4 rounds standalone (caught a real heredoc-termination bug) + live rounds through the real hook. Known residual gap, not closed: prose-restatement (a model retyping a secret it already has in context) — not fixable mechanically, logged as memory `feedback_no_secrets_in_prompts.md`.
- A dispatched subagent, given a "read-only" task, found live credentials on its own initiative and DELETEd 7 rows of real prediction data (ids 73-79, the correct/canonical batch). Free-tier Supabase, zero backups, unrecoverable. Root-caused via API logs. Subagent tool-scoping discipline changed since — narrow grants only, no assumed read-only from prose alone.

**Real fixes, shipped and verified live:**
- G23 idempotency guard: `ingest.py` date-string-vs-timestamptz bug fixed, live-tested via real `RemoteTrigger` dispatch (not just mocks) → `SKIPPED_ALREADY_DONE` confirmed. **Retest: 1/3 clean scheduled runs (2026-07-20 = OK, 13 rows). Needs 2 more (07-21, 07-22) before full closure.**
- RF-E: `engine.py` hardcoded Nifty 22000/20000 (always "above 200MA") replaced with a real `above_200ma` column on `macro_regime`. Caught a second bug mid-fix: the Supabase `select()` didn't include the new column — would have silently no-op'd. 21/21 tests pass.
- RLS enabled on all 11 public tables (was fully open — confirmed no anon-key consumer existed, zero live risk during the gap, but real hygiene).
- G16: Vercel Analytics + a 2-hourly health-check GHA (`/accuracy`, HTTP 200 + real content check) added. Basic monitoring, live.
- RF-G: `/path` Target/Stop columns were showing "0.0%" for real non-zero values — missing `*100` unit scaling. Fixed, live.
- G3/G9 in `GAP_REGISTER.md`: both claimed the Simple/Pro language layer was unwired — live-verified via Playwright (working toggle, glossary dialog, plain-language rewrites) that this was stale. Corrected.
- **RF-I disclosure (not the fix):** 6 of 14 tracked stocks silently stopped receiving new predictions (some since day 1). Every documented code path checked against real data and ruled out (is_active, stale OHLCV, silent exceptions, arbitration-margin suppression — none explain it). Root cause still unknown. Added a live, dynamically-computed coverage-gap banner to `/accuracy` disclosing this, per unanimous financial-council verdict that the hit-rate figure shouldn't be shown without caveat.

**Governance/process built this session:**
- Bug tracker discipline: `GAP_REGISTER.md` now has RF-G, RF-H, RF-I as live-tracked entries (RF-E was also found stale-closed and corrected).
- `doctrine-panel-constraint-enforcer/SKILL.md`: added a Doc-State Claim Verification Gate (Dronacharya enforcement-gap verdict — not a new skill, an extension).
- Sprint calendar + design review published as artifacts.
- Per-stock accuracy table built and reviewed with real data.

## EXACT RESUME POINT

Just kicked off a full design-scrutiny pass on a proposed **backtest/refinement engine** (non-commercial, internal — explicitly NOT a fund-management feature; confirmed by Tarun as "capability... for model training, algorithm refinement, accuracy improvisations" only).

**Critical fact just confirmed live, not from memory:** OHLCV history is 9 rows per instrument, spanning 2026-06-25 to 2026-07-20 (sparse — 9 trading days recorded across a 4-week window, not continuous). **This makes any live backtest simulation today statistically meaningless.** Told Tarun directly: cannot honestly claim "let's simulate it live" is achievable right now, per the session's own Claim Verification Gate.

Next action: complete the design-scrutiny pass (Gall's Law — build simple first, not the full complex system; Trimurti lifecycle lens; financial-panel input already gathered; premortem before any schema/code write) and present a phased plan — likely: (1) design + build the engine's skeleton now, since that's real, useful work regardless of data depth, (2) treat historical backfill as its own separate, explicit decision before any live run.

## OPEN DECISIONS (Tarun-owned)

| Decision | Deadline | Impact |
|---|---|---|
| RF-H wording sign-off (misleading "X in Y times" phrasing) | None set | Blocks the fix; currently live and misleading |
| Historical OHLCV backfill — how far back, from where | None set | Blocks any meaningful backtest; currently the real blocker on "next phase" |
| 10 product-owner decisions (4 UX direction + 6 subscription scope) | None set | Blocks next UX/subscription phase, not current MVP |
| Near-real-time data freshness — EOD-labeled vs. FMP licensing | None set | Product-scope decision |
| RF-I live test authorization (run `emit_signal()` against a stuck stock, live) | None set | Only remaining path to root-causing RF-I if code reading doesn't find it first |

## Commercial state

Stream A (Agentic Ops Starter Pack) remains most-behind per standing disclosure — unrelated to today's work. This AlphaVeda session is Stream C's actual precondition (private-first trust-building), not a detour from it.

## Parallel session note

A separate Claude Code session produced `docs/alphaveda/CLAUDE_CODE_BRIEFING.md` + 2 planning docs on 2026-07-19 (PR #4, merged cleanly). No conflicts found. Worth checking again if resuming after a gap — this has happened once already this session.

## Save state

Fully synced with `origin/main` as of last commit `6120d34` (confirmed via `git fetch` + `git log HEAD..origin/main` returning empty). Only uncommitted files are auto-generated `graphify-out/graph.*` artifacts (benign, regenerate on next commit).

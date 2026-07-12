# GraphRAG Gap Log — AlphaVeda

Tracks every internal lookup where GraphRAG returned <3 relevant nodes and an API call was required instead.
Review at session start. Use this to drive graphify improvements.

Categories:
- `dynamic-state` — real-time data, graph can never cover this, expected miss
- `missing-sync` — data exists externally (Notion, Vercel), needs a sync pipeline to repo
- `missing-node` — data is in the repo but graphify didn't extract the right node/concept
- `stale-graph` — graph exists but was not updated after the relevant commit

---

## 2026-07-01 — Session post-penalty audit (pre-rule violations, recorded for baseline)

| # | Question | API Used | Category | Fix Required |
|---|---|---|---|---|
| 1 | Phase 7 task tracker status (which tasks are Done/Blocked) | Notion MCP | `missing-sync` | Fix B: sync_notion_tasks.py → PHASE7_TASKS.md |
| 2 | Current Vercel deployment list and readyState | Vercel MCP | `dynamic-state` (readyState) + `missing-sync` (URL/config) | Fix C: VERCEL_STATE.md for static config |
| 3 | Vercel project config (rootDirectory, framework) | Vercel MCP | `missing-sync` | Fix C: VERCEL_STATE.md |
| 4 | Product Hub architecture content | Notion MCP | `missing-sync` | Fix D: PRODUCT_HUB.md mirror |
| 5 | engine.py — does emit_signal exist? | Read tool | `missing-node` (likely) | Query graph first next time; graph has 2230 nodes |
| 6 | ingest.py pipeline steps | Read tool | `missing-node` (likely) | Query graph first next time |

---

## 2026-07-12 — Session live-infra debugging (dynamic-state, expected per rule)

Per `feedback_graphrag_first_rule.md`'s own "Exception — real-time dynamic state" clause: these
correctly skipped the graph, but the rule requires logging expected misses even when the
exception applies. Representative entries only (not exhaustive) — one per category actually hit
this session, per Constraint Enforcer's proportionality ruling (full backfill of every individual
lookup was rejected as disproportionate for a P3/silent/contained item).

| # | Question | API Used | Category | Fix Required |
|---|---|---|---|---|
| 7 | Is `kowlkczswaglbmabygtl.supabase.co` resolving / is the project paused? | DNS + Supabase dashboard | `dynamic-state` | None — expected, graph cannot hold live pause state |
| 8 | Did the GHA ingest workflow run succeed on the target date? | GitHub Actions run logs | `dynamic-state` | None — expected, graph cannot hold live CI run history |
| 9 | Was migration 0014's unique constraint actually applied to the live DB? | `supabase db query --linked` + `pg_constraint` | `dynamic-state` | None — expected, graph cannot hold live schema application state |
| 10 | What is the current Vercel production deployment's readyState after redeploy? | Vercel CLI / dashboard | `dynamic-state` (readyState) | None — expected, matches gap #2 pattern |

---

## Gap Registry — Fixes Backlog

| Fix ID | Description | Effort | Priority |
|---|---|---|---|
| Fix A | Enforce codebase graph-first — behavioral only, no new files | 0 | P0 (immediate) |
| Fix B | `alphaveda/scripts/sync_notion_tasks.py` → writes `docs/plans/PHASE7_TASKS.md` | 1 session | P1 |
| Fix C | `alphaveda/docs/infra/VERCEL_STATE.md` — updated post-deploy | 30 min | P1 |
| Fix D | `alphaveda/docs/infra/PRODUCT_HUB.md` — mirrors Notion Product Hub | 15 min | P1 |
| Fix E | This file — gap logging discipline | Done | P0 |

---

## How to log a miss

When graphify query returns <3 nodes:

```
| [DATE] | [Question asked] | [API used instead] | [Category] | [Fix required] |
```

Then call the API, complete the task, and return here to add the entry.

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

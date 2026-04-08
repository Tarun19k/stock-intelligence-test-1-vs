# Session 020 — Resume Snapshot
# READ THIS FIRST after /clear to restore full context
# Written: 2026-04-07 | Before /clear command
# This file is self-contained. No other file needs to be read to resume.

---

## WHERE WE ARE

```
App version:      v5.36
Regression:       434/434 PASS (confirmed this session)
Session:          session_020 (just started, no code written yet)
Sprint status:    v5.36 COMPLETE · v5.37 NOT STARTED
GSI_WIP.md:       Status: IDLE
Last sprint:      v5.36 Post-Launch Hardening — COMPLETE (session_019)
```

---

## WHAT WAS DELIVERED THIS SESSION (before /clear)

### QA Validation Clarifications
1. **Point 2 (Portfolio Stability - OPEN-006):** The stability section IS rendering correctly. Confirmed via screenshot (`screenshots/week-summary_portfolio-allocator-view.png`). It sits **between** the 4 KPI metric cards and the efficient frontier chart — not below it. User may have missed it by scrolling too far.

2. **Point 3 (Forecast Calibration - EQA-41):** The QA brief had a WRONG navigation path. There is NO "Forecast Accuracy tab." The `_render_forecast_accuracy_report()` is in **Section 4 of the main Week Summary page** (`week_summary.py:291`) — not inside any group tab. Correct path: Week Summary main page → scroll below the Nifty heatmap.

### Full Executive Brief Delivered
A CTO + CFO + COO + Program Chief audit was run across all modes. Key outputs:
- **App score updated:** 5/10 (at v5.28) → ~7/10 (at v5.36)
- **Launch blockers:** 1 remaining — README screenshots
- **GTM strategy:** 4-phase plan documented
- **Educational guidebook:** Concept approved, 7-chapter structure defined
- **Talent audit:** 40 skills catalogued; 2 STALE; 4 MISSING (see below)

### New Program Docs Directory Created
All strategic docs written to `docs/program/`:
```
docs/program/
├── executive-brief-v5.36.md      — Program status, MVP gate, blockers, scorecard, revenue path
├── gtm-phased-market-entry.md    — Competitive landscape, 4 GTM phases, community launch templates
├── educational-guidebook-concept.md — 7-chapter guidebook plan, tutorial repo design, distribution
├── talent-ops-v5.36.md           — Skill catalog (40 skills, 2 stale, 4 missing), ops health
└── session-020-resume.md         — THIS FILE
```

---

## WHAT IS PENDING (pick up here after /clear)

### IMMEDIATE — This Session (needs CEO action first)

**[PENDING PLAYWRIGHT TEST]**
- Playwright readiness test of the live app was requested but NOT run yet
- Requires app running at localhost:8501
- CEO needs to run: `streamlit run app.py`
- Once confirmed, run Playwright to:
  1. Check Home page load time and ticker bar
  2. Navigate to RELIANCE.NS dashboard — verify ROE shows non-zero %
  3. Week Summary → Nifty 50 → Portfolio Allocator → run optimisation → confirm STABLE/MODERATE/UNSTABLE badge renders
  4. Week Summary main page → scroll to Section 4 → confirm Forecast Engine section renders without error
  5. Global Intelligence page — confirm WorldMonitor link button works; no broken elements
  6. Capture screenshots for README + docs/index.html integration

### NEXT SPRINT (v5.37 — not started)

**Backlog priority order (from docs/program/gtm-phased-market-entry.md):**

| # | ID | Item | Effort | Why now |
|---|---|---|---|---|
| 1 | README | Screenshots + demo GIF → integrate into README | Low | P0 launch blocker |
| 2 | ADR-025 | Yahoo ToS commercial trigger decision | Low | CEO sign-off needed |
| 3 | SKILL | Create `tutorial-creator` + `community-launch` skills | Low | Unblocks Phase 2 & 3 GTM |
| 4 | SKILL | Update `ui-test.md` for Playwright MCP | Low | Stale skill |
| 5 | CTO-BRIEF | Regenerate `reports/gsi-cto-brief.html` for v5.36 | Low | Stale score 5/10 → 7/10 |
| 6 | OPEN-007 | DataManager M2: CacheManager + DataContract | High | Foundation for Claude API + data coherence |
| 7 | PROXY-08 | Proxy execution flow two-launch fix | Low | Unblocks proxy-tier items |
| 8 | OPEN-018 | Claude AI narrative (after DataManager M2) | Medium | Strongest differentiator |
| 9 | GUIDEBOOK | Tutorial Ch 1: market data fetch notebook | Medium | Phase 3 GTM content |

---

## KEY DECISIONS NEEDED FROM CEO (open)

| # | Decision | Options | Recommended | Where documented |
|---|---|---|---|---|
| 1 | ADR-025: Yahoo ToS commercial trigger | A: stay free forever / B: Polygon.io on first revenue / C: Yahoo commercial licence | Option B | docs/program/executive-brief-v5.36.md |
| 2 | Guidebook repo licence | MIT licence; no production tickers.json | Confirm | docs/program/educational-guidebook-concept.md |
| 3 | Beta list | Who are the 10–20 beta testers? | CEO to define | docs/program/gtm-phased-market-entry.md Phase 1 |
| 4 | Reddit launch timing | Which Monday IST? | Avoid earnings weeks | docs/program/gtm-phased-market-entry.md Phase 2 |

---

## SYSTEM STATE AT /CLEAR TIME

- **Regression:** 434/434 PASS
- **No code was changed this session** — all work was analysis and documentation
- **GSI_WIP.md:** Status: IDLE (no sprint active)
- **Sprint manifest:** v5.36 COMPLETE, archived
- **SNAPSHOT-005:** Written (session_020, no deviations)
- **GSI_session.json:** `last_session` field stuck at `session_015` — needs update to `session_020`
- **New directory:** `docs/program/` created (4 files + this file)

---

## HOW TO RESUME (exact steps after /clear)

1. Say: **"Resuming session_020 — read docs/program/session-020-resume.md first"**
2. Claude reads this file — no need to re-run new-session protocol
3. If Playwright test is next: confirm app is running at localhost:8501
4. If code work is next: run `python3 regression.py` to confirm 434/434 still clean
5. Check `GSI_WIP.md` is still IDLE before starting any sprint

---

## GOVERNANCE NOTES (do not lose these)

### Regression rules still in effect
- Pre-commit: `python3 regression.py` (434/434 must pass) — enforced by `.claude/hooks/pre_commit.sh`
- Pre-push: `python3 compliance_check.py` (8/8 must pass) — enforced by `.claude/hooks/pre_push.sh`
- DO NOT UNDO rules: 15 rules in CLAUDE.md — check before any dashboard/market_data change

### v5.37 sprint start protocol (CLAUDE.md Rule 2)
1. Update `GSI_session.json` both version fields BEFORE running sync_docs
2. Write `GSI_SPRINT_MANIFEST.json` with Permanent Tier A checks + sprint-specific Tier B checks
3. Set `GSI_WIP.md` Status → ACTIVE
4. Run regression to confirm clean baseline

### Parallel agent discipline (CLAUDE.md Rule 8)
When dispatching worktree agents: include "Do NOT attempt git add, git commit, or any git command" in prompt. Agents write files; CTO commits.

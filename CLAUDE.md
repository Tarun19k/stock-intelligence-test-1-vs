# CLAUDE.md — Global Stock Intelligence Dashboard
# Thin router. Heavy content lives in referenced files below — read those, not this.
# Last restructured: 2026-05-17 (session_031 — Track 1 CLAUDE.md optimisation)
# Dynamic session state: GSI_session.json (repo root)

**Stack:** Streamlit 1.55 · Python · 9 markets · 559 tickers · 38 groups · 4-tab dashboard
**Version:** see `GSI_session.json → meta.current_app_version`
**Regression baseline:** 480/480 PASS (keep in sync with GSI_session.json)
**Repos:** ACTIVE → https://github.com/Tarun19k/stock-intelligence-test-1-vs · REFERENCE ONLY → https://github.com/Tarun19k/global-gsi-intelligence

---
## Current State (v5.41 — 2026-05-18)

**Sprint v5.41 COMPLETE** — Trust Restoration (TRUST-01/02/03 + OPEN-012)

## Run Commands
```bash
streamlit run app.py          # local dev
python3 regression.py         # MUST pass before any commit
python3 compliance_check.py   # MUST pass before git push
python3 sync_docs.py          # run at sprint close
```

---

## Critical Session Rules
- Read `GSI_WIP.md` first — if Status: ACTIVE, resume from CHECKPOINT exactly
- Write `GSI_SPRINT_MANIFEST.json` before any implementation (R27 enforces completeness)
- Commit after every file: implement → regression → commit → next file (Rule 3)
- Session start: `/new-session` · Session end: `/close-session`
- Sprint close sequence: update GSI_session.json versions → sync_docs → regression → Playwright gate → archive manifest → set WIP IDLE
- `cache_buster: int = 0` must remain on all market_data public functions — do NOT remove
- Data-as-of disclosure required on all aggregated sections (Portfolio Allocator, Top Movers, macro cards)
- Do NOT route Haiku-tier tasks (sequential est < 43k tokens) through subagents — Rule 18 / ADR-030

---

## Rules Files (auto-load in Claude Code when matched path is edited)
| File | Triggers on |
|---|---|
| `.claude/rules/do-not-undo.md` | app.py, forecast.py, market_data.py, indicators.py, pages/*.py, tickers.json, config.py, styles.py, version.py |
| `.claude/rules/market-data.md` | market_data.py |
| `.claude/rules/financial-safety.md` | pages/*.py, dashboard.py |
| `.claude/rules/sprint-manifest.md` | GSI_SPRINT_MANIFEST.json |
| `.claude/rules/dependencies.md` | requirements.txt |

---

## Key References
| What you need | Where it lives |
|---|---|
| Architecture, entry points, anti-patterns, rate limiting | `docs/context/architecture.md` |
| Hard constraints (DO NOT UNDO — 18 rules) | `.claude/rules/do-not-undo.md` |
| Sprint token budget / optimisation / burn templates | `.claude/templates/` |
| Sprint manifest schema | `.claude/templates/sprint-manifest-schema.json` |
| Governance policies (8) | `GSI_GOVERNANCE.md` |
| Open items + sprint backlog | `GSI_SPRINT.md` |
| QA brief template + issue classification | `GSI_QA_STANDARDS.md` |
| Compliance pre-push gate | `GSI_COMPLIANCE_CHECKLIST.md` |
| Architecture Decision Records (30 ADRs) | `GSI_DECISIONS.md` |
| Risk register (24 risks, SEBI/FCA/SEC/MiFID II) | `GSI_RISK_REGISTER.md` |
| Model selection + token tiering rules | `docs/ai-ops/token-model-rules.md` |
| Known failure classes (6 loophole categories) | `GSI_LOOPHOLE_LOG.md` |
| Dependency constraints (9 active) | `GSI_DEPENDENCIES.md` |
| Session continuity mutex | `GSI_WIP.md` |
| Per-sprint QA briefs | `GSI_QA_STANDARDS.md` |

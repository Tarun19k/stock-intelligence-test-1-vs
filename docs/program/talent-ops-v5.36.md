# Talent & Operations Report — v5.36
# Generated: 2026-04-07 | Session: session_020
# Source: talent-ops skill + .claude/commands/ directory + live file reads

---

## SKILL CATALOG — 40 SKILLS TOTAL

All skills inventoried from `.claude/commands/`:
accessibility, algorithmic-art, campaign, canvas-design, changelog-post, claude-api,
compliance-check, content-calendar, copy, cxo, data-licensing, demo-gif, design,
doc-coauthoring, docx, export-pdf, export-xlsx, gsi-brand, launch-checklist,
legal-review, log-learnings, market-position, marketing, mcp-builder, mvp-scope,
new-feature, new-session, newsletter, perf-profile, pitch-deck, policy-check,
qa-brief, risk-register, security-audit, skill-creator, sprint-review, talent-ops,
theme-factory, ui-test, web-artifacts-builder

---

## CURRENT (no action needed): 38 skills
All skills except the two below.

---

## STALE — needs update

| Skill | Stale element | Required fix |
|---|---|---|
| `cxo.md` | References `reports/gsi-cto-brief.html` frozen at v5.28 (score 5/10). Until the brief is regenerated for v5.36, CXO output mixes stale brief data with current code reads. | Regenerate brief HTML for v5.36 (score ~7/10, updated gap table, 1 P0 blocker remaining). File: `reports/gsi-cto-brief.html`. |
| `ui-test.md` | Likely does not reference Playwright MCP or `.playwright-mcp/` directory (present in repo). UI testing capability exists via Playwright MCP but the skill may direct outdated testing patterns. | Update to reference Playwright MCP tool and include example test scenarios for Streamlit: navigate to stock, assert KPI panel values, check stability badge. |

---

## MISSING — new skills recommended

| Domain | Skill name | Description | Priority | Status |
|---|---|---|---|---|
| Educational content | `tutorial-creator` | Curriculum design + code-snippet extraction from GSI modules + Jupyter notebook structuring + learning-objective framing. Required for guidebook production (Ch 1–7). | HIGH — needed for Phase 3 GTM | ❌ MISSING |
| Community launch | `community-launch` | Reddit/PH/HN post templates, timing strategy, response protocols for launch week. `campaign` covers paid/advertising; this covers organic community. | HIGH — needed for Phase 2 GTM | ❌ MISSING |
| Financial advisory domain | `fintech-domain` | Encodes SEBI/SEC/MiFID II regulatory landscape, what financial signals mean, safe framing of algorithmic outputs. Currently scattered across `legal-review`, `policy-check`, and `.claude/rules/financial-safety.md`. Consolidating reduces hallucination risk on any signal-related feature. | MEDIUM | ❌ MISSING |
| Live site E2E testing | `playwright-e2e` | Playwright MCP test writing specific to Streamlit apps: navigate pages, assert rendered values, capture screenshots, run RAM load tests. Distinct from `ui-test.md` which may be more generic. | MEDIUM | ❌ MISSING |
| **Financial data accuracy** | `signal-accuracy-audit` | 5-domain audit: indicator math (EMA/RSI/MACD/ATR), signal logic (Weinstein/Elder/unified verdict arbitration), fundamental data spot-check (ROE, P/E vs. official filings), forecast calibration (P(gain) buckets vs. actuals), portfolio math (CVaR, stability σ thresholds). Produces `docs/signal-accuracy-audit-v{version}.md`. Run before every public release. | **HIGH — P0 pre-launch gate** | ✅ **CREATED** (session_020) |

---

## DOMAIN COVERAGE CHECK

| Domain | Expected skills | Status |
|---|---|---|
| Session management | new-session, log-learnings | ✅ Both exist, current |
| Sprint / delivery | sprint-review, compliance-check, qa-brief | ✅ All exist, current |
| Security & compliance | security-audit, legal-review, policy-check, data-licensing, accessibility | ✅ All exist |
| Product management | mvp-scope, launch-checklist, risk-register | ✅ All exist |
| Content & brand | newsletter, market-position, gsi-brand, changelog-post | ✅ All exist |
| Design & UX | design, canvas-design, theme-factory, web-artifacts-builder, demo-gif | ✅ All exist |
| Export | export-xlsx, export-pdf, docx | ✅ All exist |
| Integration | claude-api, mcp-builder | ✅ Both exist |
| Management | cxo, talent-ops | ✅ Both exist; cxo STALE |
| Feature development | new-feature | ✅ Exists |
| QA & testing | ui-test, perf-profile | ✅ Both exist; ui-test STALE |
| **Educational content** | tutorial-creator | ❌ MISSING |
| **Community launch** | community-launch | ❌ MISSING |
| **Fintech domain** | fintech-domain | ❌ MISSING |
| **E2E Playwright** | playwright-e2e | ❌ MISSING |
| **Financial accuracy audit** | signal-accuracy-audit | ✅ CREATED (session_020) |

---

## OPERATIONS HEALTH — HEALTHY

| Metric | Status | Detail |
|---|---|---|
| Sprint cadence | ✅ Healthy | v5.36 COMPLETE; 10 items delivered; under 9-item cap per lane |
| Regression baseline | ✅ Healthy | 434/434 actual = 434 documented; zero drift |
| Snapshot deviations | ✅ Clean | 0 DEVIATIONs in SNAPSHOT-001 through SNAPSHOT-005 |
| Phase 3 close compliance | ✅ Full | sync_docs + regression + manifest archive + WIP→IDLE all followed in v5.35, v5.35.1, v5.36 |
| Session learnings | ✅ Healthy | 12 records total; 0 HALLUCINATIONs; 1 low-impact CONFUSION (Vercel plugin false-positive, RECORD-011) |
| Sprint manifest | ✅ COMPLETE | v5.36 manifest archived; R27 content checks inactive |
| GSI_COMPLIANCE_CHECKLIST.md | ✅ Current | Contains "ALL 434 CHECKS PASS" |
| .github/PULL_REQUEST_TEMPLATE.md | ✅ Current | Contains "ALL 434 CHECKS PASS" |

**One open process gap:** `GSI_session.json` `last_session` field is `session_015` — needs update to `session_020` at session close.

---

## RECOMMENDED ACTIONS (priority order)

1. **Create `tutorial-creator` skill** (Claude, session_021) — unblocks Phase 3 educational content GTM
2. **Create `community-launch` skill** (Claude, session_021) — unblocks Phase 2 Reddit/PH launch preparation
3. **Update `ui-test.md`** to reference Playwright MCP (Claude, session_021) — current skill may be stale
4. **Regenerate `reports/gsi-cto-brief.html`** for v5.36 score (Claude, session_021) — unblocks CXO skill accuracy
5. **Create `fintech-domain` skill** (Claude, session_022) — consolidates scattered regulatory knowledge

---

## TALENT REQUIREMENTS FOR v5.37 SPRINT

Based on v5.37 backlog candidates (OPEN-007, OPEN-018, PROXY-08, educational guidebook):

| Sprint item | Skill needed |
|---|---|
| DataManager M2 (OPEN-007) | new-feature, compliance-check, qa-brief |
| Claude API narrative (OPEN-018) | claude-api, fintech-domain (new), compliance-check |
| PROXY-08 (proxy execution flow) | new-feature |
| Educational guidebook Ch 1 | tutorial-creator (new) |
| README screenshots + demo GIF | demo-gif, web-artifacts-builder |
| Community launch prep | community-launch (new), market-position, gsi-brand |

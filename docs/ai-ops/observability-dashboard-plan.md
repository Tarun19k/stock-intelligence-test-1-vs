# GSI Observability Dashboard — Design & Implementation Plan
**Version:** 1.1 — session_025 (2026-04-13) — updated: local tool, north star layout, model map
**Target release:** v5.38
**Owner:** Tarun Kochhar
**Status:** DESIGN — approved for implementation in v5.38 sprint

## Decision Log
- **Local-only:** Tool runs as `python3 obs_local.py` (or `streamlit run obs_local.py`). No Streamlit Cloud deployment. `ANTHROPIC_API_KEY` set via shell env var — no cloud secret needed.
- **North star layout:** Single screen shows full project health without tab-switching. Collapsible expanders for drill-down detail only.
- **Parser location:** Inline in `obs_local.py` — no `utils/` subdirectory needed for a standalone local tool.
- **Separate from `pages/observability.py`:** The existing in-app observability page (app health, rate limits) remains and will be updated separately. This tool is for project governance health, not app runtime health.

---

## 1. Purpose & Scope

A founder-only, DEV_TOKEN-gated Streamlit page that surfaces the full health of the GSI
project — not just app runtime metrics — by ingesting governance documents, sprint data,
risk register, session learnings, and regression history as structured data feeds.

Extends the existing `pages/observability.py` (currently: App Health + Program dashboard)
with four new tabs and a Claude API-powered AI Recommendations panel.

**This is NOT a user-facing feature.** It is internal tooling for the project founder
to monitor project health, catch drift, and prioritise work — all from within the app.

---

## 2. Data Feeds

All feeds are local files read at page load time. No external API calls except Claude AI
Recommendations (on-demand, not on load).

| Feed | File | Format | Key data extracted |
|---|---|---|---|
| **Sprint manifest** | `GSI_SPRINT_MANIFEST.json` | JSON | Item status, token budget, file change log, cluster definitions |
| **Sprint board** | `GSI_SPRINT.md` | Markdown | Backlog, in-progress, done sections, velocity notes |
| **Sprint archive** | `docs/sprint_archive/*.json` | JSON (multi) | Historical baseline, item counts, token actuals per sprint |
| **Session learnings** | `GSI_SESSION_LEARNINGS.md` | Markdown | Per-session deviations, decisions, anti-patterns caught |
| **Session snapshots** | `GSI_SESSION_SNAPSHOT.md` | Markdown | Snapshot history, deviation flags per session |
| **Risk register** | `GSI_RISK_REGISTER.md` | Markdown | 24 risks: severity, status (Open/Mitigated/Accepted), category |
| **Audit trail** | `GSI_AUDIT_TRAIL.md` | Markdown | 48 findings: status, resolution, session fixed |
| **Regression output** | Run `python3 regression.py` | stdout | Baseline count, pass/fail breakdown by rule category |
| **Compliance output** | Run `python3 compliance_check.py` | stdout | 9-gate pass/fail |
| **Open items** | `CLAUDE.md` (parsed) | Markdown table | Priority, ID, task description |
| **Loophole log** | `GSI_LOOPHOLE_LOG.md` | Markdown | Failure class, trigger, gate, frequency |
| **Quant audit** | `.claude/quant_audit_pending.json` | JSON | Pending status, last audit date, domains |

**Parser strategy:** Use `markdown-it-py` (already available via Streamlit deps) or
regex-based section splitters. All feeds parsed into Python dicts/lists at page load.
Cache with `@st.cache_data(ttl=300)` — same TTL as OHLCV data.

---

## 3. Dashboard Layout

Single MPA page at `pages/observability.py`. Existing tabs preserved. New tabs added.

```
pages/observability.py
├── Tab: App Health          ← EXISTING (runtime metrics, rate limit state)
├── Tab: Program             ← EXISTING (sprint status, version)
├── Tab: Sprint Monitor      ← NEW — live manifest + task tracking
├── Tab: Risk & Compliance   ← NEW — risk register + compliance gates
├── Tab: Project Velocity    ← NEW — regression trend + sprint archive
├── Tab: Session Intelligence ← NEW — learnings, deviations, snapshots
└── Panel: AI Recommendations ← NEW — on-demand Claude API analysis (sidebar or bottom)
```

### Tab: Sprint Monitor

- Manifest item table: id | sub_sprint | model | mode | status | files | regression
- Token budget burn: estimated vs actual (where actuals known from archive)
- Active cluster indicator: which Haiku clusters are pending vs dispatched vs complete
- Pending git commits: files changed but not yet committed (read from `git status`)
- Next item card: highlights the next pending item with its pass criterion

**Filters:** by sub_sprint (v5.37a / v5.37b / prereq), by status, by model

### Tab: Risk & Compliance

- Risk matrix: severity (P0–P4) × category (Technical / Legal / Product / Operational)
- Heatmap: colour-coded by Open/Mitigated/Accepted status
- Compliance gate table: 9 gates with PASS/FAIL from last `compliance_check.py` run
- SEBI exposure map: which pages currently have / are missing disclaimers
- Loophole frequency: bar chart of which failure classes have been triggered most

**Filters:** by category, by status, by priority

### Tab: Project Velocity

- Regression baseline trend: line chart across sprints (from archive JSON files)
- Sprint completion rate: items planned vs items done, by sprint
- Token actuals vs estimates: where known from archive (bar chart)
- Check composition: stacked bar — R3/R8/R22/R25/R26/R27/R28/R29 breakdown per sprint

**Filters:** by sprint version (range selector)

### Tab: Session Intelligence

- Deviation log: table of all snapshot deviations across sessions (parsed from SNAPSHOT blocks)
- Decision log: extract ADRs from `GSI_DECISIONS.md` — version, date, decision title
- Anti-pattern frequency: which anti-patterns from `GSI_SKILLS.md` appear most in learnings
- Learnings timeline: session_001 → session_N, collapsible per session

**Filters:** by session range, by type (deviation / decision / anti-pattern)

### Panel: AI Recommendations

On-demand. User clicks "Analyse" button — triggers Claude API call with parsed feed data
as context. Results displayed in an `st.expander(expanded=True)`.

Three recommendation modes (model selector):

| Mode | Model | Use case | Approx cost/call |
|---|---|---|---|
| **Quick Scan** | claude-haiku-4-5 | High-frequency checks — which P0 risks are elevating, any regression drift | ~$0.002 |
| **Sprint Brief** | claude-sonnet-4-6 | Pre-sprint analysis — what to prioritise, token budget warnings, cross-sprint patterns | ~$0.04 |
| **Deep Audit** | claude-opus-4-6 | Monthly — architecture drift, long-term risk trajectory, governance gaps | ~$0.25 |

All modes use **prompt caching** on the document corpus (feeds parsed to text, sent as
cached system prompt prefix). Only the user question + delta data is billed at full rate.

---

## 4. Claude API Integration Design

### Architecture

```
observability.py
  └── _render_ai_recommendations()
        ├── _build_corpus() → parse all feeds → structured text (cached 5 min)
        ├── _get_recommendation(mode, question) → Anthropic SDK call
        │     ├── System: corpus (cache_control: ephemeral)
        │     └── User: question / mode prompt
        └── display: st.markdown(response) in expander
```

### Prompt structure (all modes)

```
[SYSTEM — CACHED]
You are the GSI project intelligence assistant. Below is the current project state:

## Sprint Manifest
{sprint_manifest_summary}

## Active Risks (Open only)
{risk_register_open_items}

## Compliance Gate
{compliance_last_run}

## Session Learnings (last 3 sessions)
{last_3_session_learnings}

## Regression Baseline History
{baseline_by_sprint}

[USER — NOT CACHED]
{mode_prompt or user_question}
```

### Mode prompts

**Quick Scan (Haiku):**
```
Scan the project state above. In under 150 words:
1. Which P0/P1 risks are currently Open and overdue for mitigation?
2. Is the regression baseline trending up (healthy) or flat (stagnant)?
3. Any SEBI compliance gaps visible from the feed?
Report as three bullet points. Be direct.
```

**Sprint Brief (Sonnet):**
```
Produce a sprint readiness brief:
1. What are the top 3 items to prioritise in the next sprint and why?
2. Are there any token budget warnings (items approaching >20k estimate)?
3. Which failure classes from the loophole log are most likely to recur?
4. Any cross-sprint velocity concerns?
Format as: Priority Items | Budget Watch | Risk Watch | Velocity
```

**Deep Audit (Opus):**
```
Perform a comprehensive project health audit:
1. Architectural drift: are any module boundaries being eroded across recent sprints?
2. Governance coverage: are all 7 policies (CLAUDE.md) actively enforced by tooling,
   or are any policy-only (no regression/compliance check)?
3. Risk trajectory: which risks have been Open for >3 sprints with no mitigation progress?
4. Recommendation: what single structural change would most improve project resilience?
Provide evidence from the feeds for each point. Length: 400–600 words.
```

---

## 5. Implementation Plan

### Phase 1 — Data parsers + Sprint Monitor tab (v5.38a)
**Effort:** 1 sprint, 3 items
**Files:** `pages/observability.py`, new `utils/obs_parsers.py`

| Item | Model | Mode | Est tokens | Risk |
|---|---|---|---|---|
| `obs-P1a`: Parse all feeds → Python dicts (obs_parsers.py) | haiku | sequential | 12k | low |
| `obs-P1b`: Sprint Monitor tab UI (manifest table, token burn, next item card) | sonnet | sequential | 18k | medium |
| `obs-P1c`: Risk & Compliance tab UI (heatmap, gate table, SEBI map) | sonnet | sequential | 18k | medium |

### Phase 2 — Velocity + Session Intelligence tabs (v5.38b)
**Effort:** 1 sprint, 2 items
**Files:** `pages/observability.py`

| Item | Model | Mode | Est tokens | Risk |
|---|---|---|---|---|
| `obs-P2a`: Project Velocity tab (regression trend chart, sprint archive) | sonnet | sequential | 16k | low |
| `obs-P2b`: Session Intelligence tab (deviation log, ADR timeline) | sonnet | sequential | 16k | low |

### Phase 3 — AI Recommendations panel (v5.38c)
**Effort:** 1 sprint, 2 items
**Files:** `pages/observability.py`, new `utils/obs_ai.py`

| Item | Model | Mode | Est tokens | Risk |
|---|---|---|---|---|
| `obs-P3a`: Corpus builder + Anthropic SDK integration (obs_ai.py) | sonnet | sequential | 20k | medium |
| `obs-P3b`: AI Recommendations panel UI (mode selector, expander display) | haiku | sequential | 10k | low |

**New dependency:** `anthropic>=0.50.0` — add to `requirements.txt` and `GSI_DEPENDENCIES.md`.
Check: does Streamlit Cloud 1GB RAM allow the Anthropic SDK? Yes — it's a thin HTTP client,
<5MB install footprint.

---

## 6. Token & Cost Model

### Dashboard load cost (no AI panel)

All parsing is local Python — zero API tokens. Only cost: CPU at page load.
Estimated load time: <1s for all feeds (all files <50KB combined).

### AI Recommendations cost per call

| Mode | Model | Input tokens (est) | Cached portion | Billed input | Output | Total cost |
|---|---|---|---|---|---|---|
| Quick Scan | haiku-4-5 | ~5,000 | ~4,000 cached (80%) | ~1,000 full | ~200 | **~$0.002** |
| Sprint Brief | sonnet-4-6 | ~8,000 | ~6,500 cached (81%) | ~1,500 full | ~500 | **~$0.015** |
| Deep Audit | opus-4-6 | ~12,000 | ~10,000 cached (83%) | ~2,000 full | ~800 | **~$0.15** |

Cached token prices: Haiku $0.025/Mtok input cache read · Sonnet $0.30/Mtok · Opus $1.50/Mtok.
Full input prices: Haiku $0.80/Mtok · Sonnet $3.00/Mtok · Opus $15.00/Mtok.
Output prices: Haiku $4.00/Mtok · Sonnet $15.00/Mtok · Opus $75.00/Mtok.

**Monthly cost estimate (founder-only use):**
- 20 Quick Scans × $0.002 = $0.04
- 10 Sprint Briefs × $0.015 = $0.15
- 2 Deep Audits × $0.15 = $0.30
- **Total: ~$0.49/month** (negligible)

### Implementation cost (development tokens)

| Phase | Main context est | Notes |
|---|---|---|
| Phase 1 (parsers + 2 tabs) | ~52k | obs-P1a haiku saves ~8k vs sonnet |
| Phase 2 (2 tabs) | ~34k | Chart-heavy — sonnet needed for layout judgment |
| Phase 3 (AI panel) | ~32k | obs_ai.py is sonnet; UI is haiku |
| Overhead (3 sprints) | ~75k | Regression × 7, sync_docs × 3, sprint close × 3 |
| **Grand total** | **~193k** | Spread across v5.38a/b/c sub-sprints |

---

## 7. Governance Requirements

New file `utils/obs_parsers.py`:
- Add to CLAUDE.md file structure table
- Add public functions to R8 EP list in regression.py
- No yfinance calls — exempt from R3

New file `utils/obs_ai.py`:
- Add to CLAUDE.md file structure table
- Add `ANTHROPIC_API_KEY` secret to `GSI_RISK_REGISTER.md` (new risk: API key exposure)
- Compliance check: AI output must be labeled "AI-generated analysis" (Policy 2)
- The AI Recommendations panel must NOT display BUY/WATCH/AVOID signals — internal tool only

`pages/observability.py` changes:
- SEBI disclaimer NOT required (Policy 4 applies to signal sections — this is internal tooling)
- DEV_TOKEN gate must remain on the entire page
- All tabs must be collapsed-safe (no data shown if feed parse fails)

`requirements.txt`:
- Add `anthropic>=0.50.0`
- Update `GSI_DEPENDENCIES.md` with constraint note

---

## 8. Open Questions — RESOLVED (session_025)

1. **`ANTHROPIC_API_KEY`:** ✅ Local-only. Set via `export ANTHROPIC_API_KEY=sk-ant-...` in shell. No Streamlit Cloud secret needed.

2. **Parser location:** ✅ Inline in `obs_local.py`. No `utils/` subdirectory.

3. **Regression trend data:** ⚠️ Still needs a quick `grep` audit of `docs/sprint_archive/*.json` before building the velocity chart. Non-blocking for P1 but required before P2 chart work.

---

## 9. ADR Pre-registration

The following ADR should be logged in `GSI_DECISIONS.md` when v5.38 sprint opens:

**ADR-023: Observability dashboard feeds from local governance docs (not DB)**
- Decision: Parse markdown/JSON governance files at page load rather than writing to a DB
- Rationale: Zero infrastructure, zero sync lag, single source of truth already maintained
- Consequence: Dashboard is read-only of the doc state — no write-back from dashboard
- Revisit trigger: If governance docs exceed 200KB total or parse time >2s

---

*This document is input to the v5.38 sprint manifest. Update after each phase completes.*

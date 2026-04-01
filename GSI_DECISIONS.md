# GSI Dashboard — Architecture Decision Record (ADR) Log
# ════════════════════════════════════════════════════════════════════════
#
# PURPOSE: Captures every significant decision made during development.
# Prevents the same decision being re-litigated in future sessions.
# When a new Claude session debates a design choice, check here first.
#
# RULES (append-only, same as GSI_AUDIT_TRAIL.md):
# 1. Every decision that took more than 30 seconds to make gets a record.
# 2. Records are never edited. Superseded decisions get a new record
#    referencing the old one: "Supersedes ADR-012".
# 3. Rejected alternatives are always recorded — "why not X" is as
#    important as "why Y".
# 4. Decisions made mid-session that are not yet in this file go into
#    GSI_WIP.md until the session ends, then migrated here.
#
# FORMAT:
# ADR-NNN | Date | Version | Status | Title
# Context, Decision, Alternatives rejected, Consequences
#
# Status: ACTIVE | SUPERSEDED (by ADR-NNN) | EXPERIMENTAL
# ════════════════════════════════════════════════════════════════════════

---

## ADR-001 | 2026-03-14 | v5.0 | ACTIVE
**Title:** Modular file architecture over monolithic script

**Context:** Initial build was a single large Python script. As features grew (indicators, forecasting, portfolio), the file became unmaintainable and untestable.

**Decision:** Split into 14 files with strict module boundaries: pages never import yfinance, computation modules never import Streamlit, config never imports from pages.

**Alternatives rejected:**
- Keep monolithic: untestable, context-window-unfriendly for Claude sessions
- 2-file split (app + utils): insufficient separation for regression testing

**Consequences:** Regression suite (regression.py) can test each module independently. Cross-file import violations caught by R9.

---

## ADR-002 | 2026-03-19 | v5.16 | ACTIVE
**Title:** tickers.json as single source of truth for ticker universe

**Context:** GROUPS and ticker lists were hardcoded in config.py. Adding/removing tickers required editing Python.

**Decision:** Extract all 559 tickers to tickers.json. config.py loads and re-exports. No ticker data lives in Python files.

**Alternatives rejected:**
- Database (SQLite): overkill for a list, adds dependency
- CSV file: harder to represent nested market/group/ticker hierarchy

**Consequences:** Tickers can be edited without touching Python. Hot-reloaded on every deploy.

---

## ADR-003 | 2026-03-21 | v5.18 | ACTIVE
**Title:** @st.fragment at module level, not inline

**Context:** Fragment functions were being defined inside render functions, causing re-instantiation and timer instability.

**Decision:** All @st.fragment-decorated functions defined at module level. Never defined inside another function.

**Alternatives rejected:**
- Inline fragments: causes timer drift and fragment ID conflicts in Streamlit
- No fragments (full reruns): too slow for live price refresh

**Consequences:** DO NOT UNDO rule 8 in CLAUDE.md. R8b regression check guards against recursion.

---

## ADR-004 | 2026-03-21 | v5.19 | ACTIVE
**Title:** Historical Simulation (bootstrap) over Monte Carlo for forecasting

**Context:** Needed a forecasting model that doesn't assume normality of returns, handles fat tails, and is interpretable to retail users.

**Decision:** 2,000-path bootstrap from 3-year return distribution. No distributional assumptions. P10/P90 confidence bands.

**Alternatives rejected:**
- Monte Carlo (GBM): assumes log-normal returns — wrong for Indian equities
- ARIMA/ML models: require training data infrastructure not available in free deployment
- No forecasting: reduces product value significantly

**Consequences:** forecast.py uses historical_simulation_v1 method. Accuracy tracked in session state.

---

## ADR-005 | 2026-03-22 | v5.22 | ACTIVE
**Title:** 4-state routing (stock/group/market/week) over page-based navigation

**Context:** Streamlit MPA (multi-page apps) requires separate .py files per page and loses session state on navigation.

**Decision:** Single-page app with 4-state routing in app.py. State managed via st.session_state. All views rendered from one entry point.

**Alternatives rejected:**
- Streamlit MPA: session state loss on page switch kills live refresh fragments
- st.tabs at top level: too flat — doesn't support the group/market hierarchy

**Consequences:** DO NOT UNDO rule 5 in CLAUDE.md. grp_explicitly_selected guard (M3) prevents accidental 49-ticker fetches.

---

## ADR-006 | 2026-03-24 | v5.23 | ACTIVE
**Title:** Mean-CVaR (Rockafellar-Uryasev 2000) for portfolio optimisation

**Context:** Needed a risk model that handles tail risk better than mean-variance (Markowitz) for volatile emerging market stocks.

**Decision:** Mean-CVaR with Clarabel solver via cvxpy. 2,000 exponentially-weighted bootstrap scenarios. VIX stress mode (risk budget cut 40% when VIX > 25).

**Alternatives rejected:**
- Mean-variance: minimises variance, not tail loss — inappropriate for Indian small/mid caps
- Black-Litterman: requires analyst views, not available in automated system
- Equal-weight: too naive for a "portfolio optimiser" product claim

**Consequences:** Requires libopenblas-dev in packages.txt for cvxpy on Streamlit Cloud.

---

## ADR-007 | 2026-03-26 | v5.25 | ACTIVE
**Title:** M3 routing guard (grp_explicitly_selected) to prevent cold-start batch fetches

**Context:** Selecting a market group was triggering a 49-ticker batch download on every cold start, causing rate limit spirals.

**Decision:** grp_explicitly_selected flag in session state. Group overview only fires when this flag is True (set only by explicit user click).

**Alternatives rejected:**
- TTL-only protection: cache miss on cold start still fires the batch
- Lazy-load with spinner: still fires the request, just defers display
- Remove group view: loses a core product feature

**Consequences:** DO NOT UNDO rule — the M3 guard is checked by R22 regression.

---

## ADR-008 | 2026-03-28 | v5.31 | ACTIVE
**Title:** Option B — remove raw Momentum Score from dashboard header

**Context:** Score 59/100 shown alongside WATCH verdict confused users (59 is in BUY territory). Two options evaluated:
- Option A: Keep score, add explanation of why score and verdict diverge
- Option B: Remove score from header, keep it only in the KPI panel

**Decision:** Option B. Score removed from header. Verdict badge + plain-English override reason only. Score visible in "📊 Momentum Signal Panel" KPI section below.

**Alternatives rejected:**
- Option A: Adds complexity to the header. The explanation itself would need explaining.
- Remove score entirely: Loses useful data for quant/systematic trader persona.

**Consequences:** DO NOT UNDO rule 12 in CLAUDE.md. R17 regression check updated to accept "Momentum Signal Panel" label.

---

## ADR-009 | 2026-03-28 | v5.31 | ACTIVE
**Title:** Remove "What You Should Do Next" from Global Intelligence page

**Context:** Section contained career/investment action cards (invest in NVDA, TSM, MSFT) with no disclaimer and no connection to live market data. P0 regulatory finding.

**Decision:** Remove entirely. Not redesign. The pattern of generic action cards disconnected from live data is fundamentally incompatible with regulatory requirements and Policy 4.

**Alternatives rejected:**
- Redesign with disclaimers: The content itself (career advice) is out of scope for a financial signals platform
- Move to a separate "General Information" tab: Still requires disclaimer framework not yet built

**Consequences:** DO NOT UNDO rule 14 in CLAUDE.md. Function definition retained for future redesign that ties actions to live signals.

---

## ADR-010 | 2026-03-28 | v5.31 | ACTIVE
**Title:** GSI_AUDIT_TRAIL.md as immutable append-only audit log

**Context:** GSI_QA_STANDARDS.md Section 13 used a mutable Status column that destroyed historical state when updated.

**Decision:** Separate file (GSI_AUDIT_TRAIL.md) with four immutable record types: FINDING, RESOLUTION, REOPEN, GOVERNANCE. Current state view (Section 4) is derived, not source.

**Alternatives rejected:**
- Mutable table with timestamp column: Still allows editing — not a true audit trail
- GitHub Issues as audit trail: Loses portability and Claude context
- session.json known_issues: Too compact — loses context and rationale

**Consequences:** Section 13 of GSI_QA_STANDARDS.md superseded and marked. R10b now checks GSI_AUDIT_TRAIL.md existence.

---

## ADR-011 | 2026-03-28 | v5.28 | ACTIVE
**Title:** pandas>=1.4.0 not >=3.0.0 in requirements.txt

**Context:** Streamlit 1.55.0 declares pandas<3 in its package metadata. Using pandas>=3.0.0 causes ResolutionImpossible on both pip and uv locally and on Streamlit Cloud.

**Decision:** Use pandas>=1.4.0. Let pip/uv resolve to the latest 2.x compatible version. The GSI codebase is compatible with both 2.x and 3.x.

**Alternatives rejected:**
- Pin to pandas==2.2.3: Too rigid — prevents security patches
- pandas>=3.0.0: Breaks on every clean install
- Maintain two requirements files: Maintenance overhead not justified

**Consequences:** DO NOT use pandas>=3.0.0 in requirements.txt. Documented in GSI_SKILLS.md Skill 9 and GSI_DEPENDENCIES.md.

---

## ADR-012 | 2026-03-29 | v5.32 | ACTIVE
**Title:** calc_5d_change() shared utility over per-page inline calculations

**Context:** H-01 audit finding — Nifty 50 showing -9.4% on Home vs -1.3% on Dashboard in the same session. Each page had a slightly different 5-day window calculation.

**Decision:** Single function calc_5d_change(df) in utils.py. All pages import and use this function. Inline calculations banned for any metric that appears on more than one page.

**Alternatives rejected:**
- Fix each page's inline calc independently: Still two separate implementations — divergence risk remains
- Pass pre-computed 5d values from app.py: Adds coupling between app.py and every page

**Consequences:** Policy 5 (Data Coherence) principle instantiated as code. R23b regression check enforces.

---

## ADR-013 | 2026-03-29 | v5.32 | ACTIVE
**Title:** GI watchlist uses cache_buster=0 not cache_buster=cb

**Context:** G-04 audit finding — ticker bar and GI watchlist showing different prices for same ticker in same session. Root cause: different cache keys.

**Decision:** GI watchlist always uses cache_buster=0, matching the ticker bar's key. The GI watchlist is a read-only price display, not a signal display — it never needs session-specific cache busting.

**Alternatives rejected:**
- Pass ticker bar data directly to GI: Couples home.py to global_intelligence.py — violates module boundaries
- Shared cache key variable: Complexity for no gain — 0 is already the right key

**Consequences:** R23b regression check. Prices guaranteed coherent within a session.

---

## ADR-014 | 2026-03-29 | v5.32 | ACTIVE
**Title:** GSI_WIP.md as session continuity mutex

**Context:** Claude.ai usage limits can interrupt mid-session. Without a record of in-flight work, the next session risks duplicating completed work or skipping incomplete work.

**Decision:** GSI_WIP.md is a mutex/lock file. Claude writes to it before starting any implementation. The file has a Status field (ACTIVE/IDLE) and a CHECKPOINT block format. The next session reads it first.

**Alternatives rejected:**
- session.json "in_progress" field: Too nested — easy to overlook
- Verbal instructions in CLAUDE.md: Not structured enough to survive context compaction
- No mechanism (trust memory): Doesn't survive usage limit interruptions

**Consequences:** GSI_WIP.md added to session start checklist. CHECKPOINT protocol added to CLAUDE.md.

---

## ADR-015 | 2026-03-29 | v5.32 | ACTIVE
**Title:** Commit after every file, not at sprint end

**Context:** Uncommitted files in outputs/ are at risk if Claude hits a usage limit. A batched commit at sprint end means all in-progress work is lost.

**Decision:** Commit to git after every file is complete. No batching multiple files into a single commit during active development.

**Alternatives rejected:**
- Sprint-end commit: Convenient but loses all work if session ends early
- Auto-commit via Claude Code: Not yet adopted — manual for now

**Consequences:** Documented in GSI_SPRINT.md sprint planning rules. Reinforced in CLAUDE.md.

---

## ADR-016 | 2026-04-01 | v5.34 | ACTIVE
**Title:** Living sprint manifest with per-file doc update contracts (R27)

**Context:** v5.33 completed with 6 doc update misses — audit trail, governance, risk register, loophole log, and a missing version entry were never updated despite being required. The root cause was no machine-enforced link between "file committed" and "docs updated".

**Decision:** Each sprint writes a `GSI_SPRINT_MANIFEST.json` at the start. Every file committed during the sprint must have an entry in `file_change_log` with either `doc_updates_required` (list of check IDs) or `no_doc_update_reason`. R27 regression checks enforce this during the sprint (Pass 1: log completeness; Pass 2: must_contain string checks on target files). Manifest is archived to `docs/sprint_archive/` on close.

**Alternatives rejected:**
- End-of-sprint checklist only: Same as before — relies on memory, proven to miss items
- Hardcoded per-file rules in regression.py: Not sprint-aware; would permanently inflate the baseline with checks that only apply during specific sprints

**Consequences:** Baseline inflates during a sprint (R27 checks are active), returns to structural baseline on close. Rule 2 and Rule 7 added to CLAUDE.md to enforce the workflow. Amendment log in manifest handles unplanned mid-sprint file changes.

---

## ADR-017 | 2026-04-01 | v5.34 | ACTIVE
**Title:** Observability page gated by st.secrets DEV_TOKEN, not by route obscurity

**Context:** The founder-only observability page (`pages/observability.py`) needed to be inaccessible to public users while still being reachable via direct Streamlit MPA URL for the developer.

**Decision:** Gate via `st.secrets["DEV_TOKEN"]` PIN entry stored in `st.session_state["obs_unlocked"]`. The page is hidden from the public nav via the existing CSS that suppresses the MPA sidebar. No security through obscurity — an active PIN gate is required.

**Alternatives rejected:**
- Route obscurity only (no PIN): Easily bypassed by anyone who reads the source code
- Separate Streamlit app: Operational overhead; would require separate deploy and secrets management

**Consequences:** `DEV_TOKEN` must be set in Streamlit Cloud secrets before the page is accessible on deployment. R26 regression check enforces the `obs_unlocked` gate is present in the page source.

---

## Template for new ADRs

```
## ADR-[NNN] | [YYYY-MM-DD] | [version] | ACTIVE
**Title:** [Short decision title]

**Context:** [What problem or choice triggered this decision]

**Decision:** [What was decided and why]

**Alternatives rejected:**
- [Option]: [Why rejected]
- [Option]: [Why rejected]

**Consequences:** [What this means for the codebase, documentation, or process]
```

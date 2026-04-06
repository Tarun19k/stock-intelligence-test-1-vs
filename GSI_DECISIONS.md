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

## ADR-018 | 2026-04-01 | v5.34+ | ACTIVE
**Title:** Consolidated CXO + Talent-Ops management layer as Claude skills

**Context:** Program needed executive-level oversight (CTO/COO/CFO/Program Chief) and talent/operations management as the tool approached MVP launch. The question was whether to build three separate skills or consolidate.

**Decision:** Two skills: (1) `talent-ops.md` — consolidated Talent & Operations because they share source data (same governance docs) and outputs are interdependent; (2) `cxo.md` — Executive Suite with four named modes (CTO/COO/CFO/Program Chief), default Program Chief. CXO reads `reports/gsi-cto-brief.html` as its primary strategic document and feeds from talent-ops output.

**Alternatives rejected:**
- Three separate skills (Talent Manager, Operations Manager, CXO): Redundant file reads; talent requirements flow directly from ops analysis, making separation wasteful
- Single unified skill: Too broad; loses the executive lens distinction that makes CTO vs. CFO vs. Program Chief outputs actionable

**Consequences:** `/cxo` is the default program management entry point. `/talent-ops` feeds into CXO. Both kept active at all times per CEO instruction. First Program Chief run produced 5 CEO sign-off decisions (S-01 to S-05), confirmed 2 MVP launch blockers (WorldMonitor + landing page), and generated v5.35 sprint manifest.

---

## ADR-019 | 2026-04-05 | v5.34+ | ACTIVE
**Title:** No maxTokens cap in Claude Code settings.json

**Context:** Session_014 planning — evaluating token budget mechanisms for Claude Code automation. Considered setting `maxTokens` in `settings.json` to reduce verbose responses and limit context consumption per turn.

**Decision:** Do NOT set `maxTokens`. Token budget is managed behaviourally and via run_state dedup, not via a hard output cap.

**Alternatives rejected:**
- `maxTokens: 8192`: Files in this repo (dashboard.py, regression.py, pages/) run 400–700+ lines (~7,000 tokens). A hard output cap risks truncating a Write tool call mid-function — producing broken code silently with no obvious error. Quality risk outweighs token saving.

**Consequences:** Verbosity is controlled by instruction (concise responses) rather than mechanical cap. Token efficiency comes from the run_state dedup mechanism — skipping redundant regression runs when the git HEAD hash and PASS result are both fresh. This saves the most real context waste per session without any quality risk.

---

## ADR-020 | 2026-04-05 | v5.34.1 | ACTIVE
**Title:** Claude Code hook architecture — 3-hook design with exit-2 gate model

**Context:** Session_014 planning — automating the regression gate, compliance gate, and doc audit that are currently discipline-only (run manually). Full schema verified against live Claude Code documentation before deciding.

**Decision:** Wire three hooks in `.claude/settings.json`:
1. **PreToolUse on Bash** — regression gate on `git commit`. Parses `tool_input.command` via Python stdin. Checks `run_state.json`: skips if PASS cached on current git HEAD. Exits `2` to block on failure.
2. **PreToolUse on Bash** — compliance gate on `git push`. Calls `compliance_check.py`. Exits `2` to block on failure.
3. **PostToolUse on Write|Edit** — doc audit on any `*.md` change. Calls `sync_docs.py --check`. Outputs `{"suppressOutput": true}` on clean pass (silent). Non-blocking (PostToolUse cannot block).
Use `$CLAUDE_PROJECT_DIR` for all paths (built-in env var — portable, no hardcoded paths). Parse stdin with Python (`jq` not installed). `run_state.json` caches `{hash, timestamp, result}` — dedup applies only when `result == "PASS"`.

**Alternatives rejected:**
- `exit 1` to block: Incorrect. Claude Code hook schema uses exit `2` for blocking; exit `1` is a non-blocking error shown only in verbose mode. The gate would silently allow all commits through.
- `jq` for stdin parsing: Not installed on this machine. Python used instead.
- Hardcoded absolute paths: Non-portable. `$CLAUDE_PROJECT_DIR` solves this cleanly.
- Compliance check inline in hook: Shell quoting complexity; extracted to `compliance_check.py` for reliability and testability.
- PostToolUse on Write only (not Edit): Edit is the preferred tool for modifying existing files per CLAUDE.md. Write-only coverage misses most doc edits.
- Per-edit doc audit noise: Resolved by `suppressOutput` — hook is invisible on clean pass.

**Deferred to future sprint:** `SessionStart` hook (auto-check GSI_WIP.md status), `Stop` hook (end-of-session GSI_WIP.md reminder), `statusMessage` UX polish, dedup hook for explicit mid-session regression calls.

**Consequences:** Regression gate, compliance gate, and doc audit become structural enforcement. Commits cannot bypass the 427-check suite. Push cannot bypass the 8-check compliance gate. Doc drift is surfaced immediately after each edit. Hook work requires its own sprint entry (and manifest file_change_log entries) before implementation begins.

---

## ADR-021 | 2026-04-05 | v5.34.2 | ACTIVE
**Title:** Hook repo-root resolution via `git rev-parse` (permanent fix for CLAUDE_PROJECT_DIR unreliability)

**Context:** After v5.34.1 hook deployment, all three hook scripts (pre_commit.sh, pre_push.sh, post_edit.sh) failed with "CLAUDE_PROJECT_DIR: unbound variable" errors. The variable is not reliably set in all Claude Code hook execution contexts. A permanent, environment-variable-free solution was required.

**Decision:** Replace all `$CLAUDE_PROJECT_DIR` references in hook scripts with `REPO=$(git rev-parse --show-toplevel)`. This resolves the repo root from git's own metadata — git is always available in any git repository context, and `--show-toplevel` works from any subdirectory. All scripts use `set -euo pipefail` (pre_edit uses `set -uo pipefail`), which means the script exits immediately if git is unavailable (correct failure mode). The settings.json hooks block retains `$CLAUDE_PROJECT_DIR` in the hook command strings — that is a Claude Code platform variable used to locate the hook file, not used inside the script itself.

**Alternatives rejected:**
- Keep `$CLAUDE_PROJECT_DIR` inside scripts: Unreliable — not set in all hook execution contexts (CTO finding M-1).
- Hardcode absolute path: Non-portable across developer machines.
- `dirname "$0"`: Unreliable when scripts are invoked via bash path substitution.
- Export `CLAUDE_PROJECT_DIR` in shell profile: Fragile — requires every developer to configure their environment.

**Consequences:** Hook scripts are permanently environment-variable-independent for repo root resolution. Fix applies to all 3 hooks. Any future hooks added to this repo should follow the same `git rev-parse --show-toplevel` pattern.

---

## ADR-022 | 2026-04-06 | v5.35 | ACTIVE
**Title:** WorldMonitor CSP stopgap — iframe replaced with external link button

**Context:** The Global Intelligence page originally embedded the WorldMonitor live events map via an `<iframe>`. After deployment to Streamlit Community Cloud (*.streamlit.app domain), users saw a blank grey box where the map should appear. The cause: WorldMonitor sets a `Content-Security-Policy: frame-ancestors` header that blocks framing from any origin other than their own domain. This is a server-side CSP enforcement — no client-side workaround exists. Policy 2 (Architecture) requires that any embed failing CSP must be replaced with a link button rather than left silently broken. The issue was discovered during v5.34.x QA; the fix was implemented before v5.35 sprint start.

**Decision:** Replace the iframe with a styled anchor link button inside the same expander (`🗺️ WorldMonitor — Live Interactive Global Events Map`). The button opens `https://worldmonitor.app` in a new browser tab (`target="_blank"`). A `st.caption` below the button explains why embedding is unavailable: "WorldMonitor cannot be embedded here due to their Content Security Policy. Click above to open the live map in a new tab." This keeps the feature discoverable and functional while honestly communicating the limitation. Implementation is in `pages/global_intelligence.py` lines 212–230.

**Alternatives rejected:**
- **iframe embed (original approach):** Rejected — WorldMonitor's `frame-ancestors` CSP header blocks the *.streamlit.app origin at the browser level. No amount of iframe attribute changes (sandbox, allow, referrerpolicy) can override a server-sent CSP header. Leaving a broken iframe would silently fail for all users with no explanation.
- **Self-hosted WorldMonitor replacement (Leaflet.js + ACLED/GDELT API):** Deferred, not rejected. Logged as OPEN-020. Requires significant infrastructure (self-hosted tile server or commercial tile API, ACLED/GDELT data licensing, custom Leaflet.js embed). Out of scope for a CSP stopgap fix. Remains the planned long-term resolution.
- **Proxy iframe via Streamlit Cloud subdomain:** Not viable — CSP `frame-ancestors` is evaluated at the framing origin, not the src origin. A proxy would still load from *.streamlit.app and be blocked.

**Consequences:** The WorldMonitor section is functional (accessible via click) rather than silently broken. Users understand why direct embedding is unavailable. OPEN-020 (self-hosted Leaflet.js world map) remains the correct long-term fix and is tracked in the backlog for v5.36+. When WorldMonitor updates their CSP to allow *.streamlit.app (unlikely but possible), CONSTRAINT-009 in GSI_DEPENDENCIES.md should be removed and the iframe can be restored — this ADR would be superseded at that point.

---

## ADR-023 | 2026-04-06 | v5.35.1 | ACTIVE
**Title:** Tiered sprint capacity + token budget/optimisation framework

**Context:** The flat 9-item sprint cap was designed for Claude.ai context-window limits. With Claude Code's automatic context compaction and parallel worktree agents, the constraint shifted from context window to CTO oversight bandwidth. Simultaneously, a post-sprint token audit of v5.35 revealed ~65k tokens wasted on agent git failures and ~10k on a sync_docs debug loop — both preventable with better upfront planning.

**Decision:** Replace the 9-item cap with a 3-lane tiered budget (≤6 sequential / ≤6 parallel agent / ≤4 risky). Add `token_budget` and `token_optimisations` blocks to every sprint manifest, filled before implementation starts. Quality floor guardrails prevent optimisation types from compromising regression, compliance, QA brief, or the Read-before-Edit rule. `read_avoidance` banned for files being edited. Parallel agents must not attempt git commands (Rule 8).

**Alternatives rejected:**
- Raise flat cap to 15: No lane separation — risky items would not be bounded independently.
- No budget tracking at all: Waste repeats every sprint with no visibility or learning.

**Consequences:** Every future sprint manifest requires `token_budget` + `token_optimisations` fields. Sprint velocity table now tracks Est. Tokens + Optimisations columns. RECORD-008/009/010 in GSI_SESSION_LEARNINGS.md feed the optimisation library over time.

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

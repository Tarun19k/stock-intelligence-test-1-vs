# GSI_LOOPHOLE_LOG.md — Automation-Caught Loophole Registry
# Version: v1.0 | Created: 2026-03-31
# Purpose: Catalog the classes of loopholes the automated governance tooling
#          is designed to catch, why each matters, and which check enforces it.
#
# UPDATE PROTOCOL:
#   Append new entries below as new loophole classes are discovered.
#   Never edit existing entries — add a CORRECTION record if a finding changes.
#   Cross-reference to GSI_AUDIT_TRAIL.md for specific instances of each class.
#
# WHO SHOULD READ THIS:
#   Any developer adding a new feature, signal section, or data metric.
#   Read alongside GSI_COMPLIANCE_CHECKLIST.md before any git push.

---

## What "loophole" means here

A loophole is a gap that would pass a surface code review but violate a
regulatory, architectural, or data-integrity constraint. The automation catches
these without relying on the developer remembering the rule.

This document is not a finding log (see GSI_AUDIT_TRAIL.md for specific
instances). It is a class-level catalogue: what categories of failure the
system is engineered to prevent.

---

## Class 1 — Regulatory Loopholes

Caught by: **compliance script** (GSI_COMPLIANCE_CHECKLIST.md §Quick compliance script)
            + **regression.py R17**

| Loophole | Why it matters | Check |
|---|---|---|
| BUY/WATCH/AVOID signal displayed without SEBI disclaimer | Displaying directional investment signals without a SEBI-registered advisor disclaimer exposes the developer to regulatory action under SEBI Finfluencer rules. India is the highest-risk jurisdiction in GSI's coverage. | Compliance script: `'SEBI-registered investment advisor' in files['db']` |
| Narrative section missing "algorithmically generated" label | Presenting AI/algorithm output without disclosure can be classified as unregistered investment advice. Regulators (SEBI, FCA, SEC) require algorithmic output to be labelled. | Compliance script: `'algorithmically generated' in files['db'].lower()` |
| "Live" or "Real-Time" label on data older than 48 hours | A freshness label on stale data is a material misrepresentation. Retail users make decisions based on perceived recency. | Compliance checklist Tier 1: "No section named 'Live' or 'Real-Time' where data is static or >48h old" |
| "What You Should Do Next" section in any page | An explicit action instruction ("You should buy X") is investment advice without SEBI registration. Removed from GI page in v5.31. | Compliance script: `len(re.findall(r"(?<!def )_render_next_steps_ai\(\)", files['gi'])) == 0` |
| "No major red flags at this time." as default Watch Out For text | A blanket safety signal ("no flags") is a false safety statement. Retail users read it as a clearance. The RSI/MACD-aware default is the correct replacement. | Compliance script: `'"No major red flags at this time."' not in files['db']` |
| Named stock recommendation without a BUY/WATCH/AVOID verdict | Discussing a stock without showing its current signal is an incomplete disclosure — user cannot assess the context of the mention. | Compliance checklist Tier 1: "No named stock recommendations without their verdict shown alongside" |

**Root risk:** RISK-L01 (SEBI signal display), RISK-L04 (Finfluencer rules)
**Jurisdiction hierarchy:** India (SEBI) > EU (MiFID II) > UK (FCA) > US (SEC) > China (CSRC)

---

## Class 2 — Data Integrity Loopholes

Caught by: **regression.py** (R17, R22) + **compliance checklist Tier 2**

| Loophole | Why it matters | Check |
|---|---|---|
| Same metric calculated differently across pages | Users see different numbers for the same ticker on different pages in the same session. This erodes trust and violates Policy 5 (Data Coherence). Instance: H-01 (5-day % divergence, Home vs Dashboard). | Compliance checklist Tier 2: "Any new metric added to the KPI panel is calculated the same way across all pages" |
| ROE/P/E showing `0.0%` when yfinance returns null | `safe_float(None) → 0.0` presents a data gap as a real value. A user reading ROE = 0.0% thinks the company has zero return on equity. The correct display is "N/A". | Compliance script: `'roe_str' in files['db']` (checks null guard exists) |
| Forecast showing directional signal in the 45–55% neutral zone | P(gain) of 49% is not a "BEARISH" signal — it is insufficient data. Overconfident signals mislead users about model certainty. OPEN-009. | Planned regression check (OPEN-009) |
| Stale RSS feeds in a "Live Headlines" section | If the most recent article is >90 days old, the feed is dead. Showing it as live news misrepresents information recency. | Compliance checklist Tier 2: "No feed in 'Live Headlines' with newest article older than 90 days" |
| Momentum score (X/100) visible in dashboard header | Displaying a raw algorithmic score without context quantifies confidence in a way that implies precision the model does not have. Option B (verdict + plain-English reason) is the correct replacement. | Compliance script: `'Momentum: {score}/100' not in files['db']` |

**Root risk:** RISK-P03 (signal accuracy trust), RISK-P01 (misinterpretation as advice)

---

## Class 3 — Architecture Loopholes

Caught by: **regression.py Tier 3 checks** (R9, R10, R11)

| Loophole | Why it matters | Check |
|---|---|---|
| Page file importing yfinance directly | Bypasses the rate limiting layer entirely. A single stray `import yfinance` in a page can trigger 429s for all users. | Regression R9: "No page file imports yfinance directly" |
| New yfinance function missing `_is_rate_limited()` call | Same as above at the function level. Every public function in market_data.py must call the token bucket gate before hitting the API. | Compliance script: `'_is_rate_limited()' in files['md']` |
| `DataManager.fetch()` called from a page before M4 | DataManager M1 is a skeleton — calling fetch() before M4 hits an unstable/unvalidated data path. Bypass mode is enforced. | Compliance checklist Tier 3 + generate_context.py anti-patterns section |
| Streamlit import inside indicators.py / forecast.py / portfolio.py | These modules must be pure computation — no UI coupling. A stray `import streamlit` breaks the ability to unit-test them and violates the module contract. | Regression: `indicators/forecast/portfolio have ZERO import streamlit` |
| `data_manager.py` importing from `market_data.py` | Creates a circular dependency loop. DataManager is a layer above market_data — it cannot import from it. | Compliance checklist Tier 3: "data_manager.py does not import from market_data.py" |
| Hardcoded absolute paths in regression checks | Makes the test suite non-portable — fails on any machine with a different path. Found in R23b (`/home/claude/dashboard.py`). Always use the file map (`FM.get(...)`). | Fixed: 2026-03-31 session_011 |

**Root risk:** RISK-T01 (rate limiting), RISK-T07 (dependency breakage), RISK-T08 (single data source)

---

## Class 4 — Security Loopholes

Caught by: **partial — RISK-T09 remains open**

| Loophole | Why it matters | Check | Status |
|---|---|---|---|
| Unsanitised `{ticker}/{name}` in `unsafe_allow_html` f-strings | XSS: a malicious ticker name containing `<script>` tags would execute in the user's browser. `sanitise()` exists but is not applied to every f-string. | RISK-001 in open backlog | Open |
| Hardcoded file paths in automation scripts | A path specific to one developer's machine breaks CI and portable testing. | Caught in regression R23b fix (2026-03-31) | Fixed |
| API keys in page files | If Streamlit secrets are not used and a key is hardcoded, it gets committed to git. Not current but must be prevented when Claude API is added. | Policy: always use `st.secrets` | Preventive |

**Root risk:** RISK-T09 (XSS), RISK-L06 (open source licence exposure)

---

## Class 5 — Context & Continuity Loopholes

Caught by: **sync_docs.py** + **generate_context.py** + **regression.py R10b**

| Loophole | Why it matters | Check |
|---|---|---|
| New governance doc added without updating regression R10b | The doc exists on disk but no automated check verifies it. The next developer has no guarantee it was maintained. | R10b: checks all 12 gov docs exist. Add new docs to this list when created. |
| Regression baseline count drifts between files | CLAUDE.md says "399", session.json says "396", PR template says "378" — conflicting signals about what "passing" means. Any one source being wrong silently lowers the gate. | Multi-file audit: regression.py, GSI_session.json, CLAUDE.md, PR template, GSI_COMPLIANCE_CHECKLIST.md must all agree. |
| GSI_CONTEXT.md stale after source file changes | Claude.ai Project Files contains an old snapshot. New sessions start with wrong architecture, open items, or version. | generate_context.py auto-runs after clean regression. Manual: `python3 generate_context.py --check` |
| sync_docs.py advisories ignored over multiple sessions | Advisories are soft-warnings but accumulate into real gaps (wrong version references, missing doc mentions). | Review `python3 sync_docs.py --check` output at session start. |
| Session recorded in GSI_session.json but GSI_WIP.md still ACTIVE | Mutex left open — next session thinks there is in-progress work when there isn't. | End-of-session: set GSI_WIP.md `Status: IDLE` and push before closing. |

**Root risk:** RISK-O02 (context loss), RISK-P05 (single developer bus factor)

---

## Class 6 — Legal / ToS Loopholes (structural — not caught by code checks)

These are not catchable by code automation. They require policy discipline.

| Loophole | Why it matters | Mitigation |
|---|---|---|
| Using yfinance data in a commercial context | Yahoo Finance ToS explicitly prohibits redistribution and commercial use. GSI MVP is educational framing. A public launch with monetisation would require licensed data (Polygon.io, Quandl). | RISK-L02. Document in README. Separate data layer for commercial path. |
| Posting specific stock signal results on social media | Under SEBI Finfluencer rules, publishing directional signals publicly may require registration. Even "sharing a screenshot" counts. | RISK-L04. Social posts use only product screenshots, never signal outputs. |
| Open source dependencies with incompatible licences | Adding a GPL-licensed dependency to an otherwise Apache 2.0 / MIT project can create licence propagation issues. | Check licence before `pip install`. RISK-L06. |

---

## Adding new loophole classes

When a new category of loophole is discovered:

1. Add a record to `GSI_AUDIT_TRAIL.md` (specific instance — append only)
2. If it represents a new *class* of failure, add a row to the relevant section above
3. If it should be caught automatically, add a check to:
   - `regression.py` (structural/architectural checks)
   - `GSI_COMPLIANCE_CHECKLIST.md` (pre-deploy gate)
   - compliance script (quick inline check)
4. Update `GSI_session.json` `open_items` if not yet fixed
5. Update `GSI_RISK_REGISTER.md` if it represents a new risk vector

---

## Cross-references

| Document | Role |
|---|---|
| `GSI_AUDIT_TRAIL.md` | Specific instances of each loophole class (append-only) |
| `GSI_RISK_REGISTER.md` | Risk posture and mitigation status per risk vector |
| `GSI_COMPLIANCE_CHECKLIST.md` | Pre-deploy automated gate — runs the checks |
| `GSI_GOVERNANCE.md` | 7 policies that the loophole classes map to |
| `GSI_SKILLS.md` | Code patterns that prevent loopholes from being introduced |
| `regression.py` | Automated enforcement — 399 checks |

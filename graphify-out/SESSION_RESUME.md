# SESSION_RESUME.md — GSI Tool Workspace
# Recovery: `/chief-of-staff recover` then read this file first

**Session date:** 2026-06-15 → 2026-06-17 (multi-day)
**Session name:** GSI tool
**Workspace:** stock-intelligence-test-1-vs

---

## DO NOT REDO — Already completed this session

1. **Strategic analysis HTML page** — built and committed at `ideas/strategic_analysis.html`. Interactive 6-framework analysis of the GSI→Platform migration, 10 sections, Chart.js radar, filterable gap register, all 29 gaps rendered. Do not rebuild.

2. **Plain language platform explanation** — complete explanation of the math (bootstrap forecasting, indicators, portfolio analytics, synthesis pipeline, accuracy ledger) delivered in conversation. Do not repeat.

3. **7-seat full council review** — panel-convene invoked with all financial expert seats (Buffett, Munger, Dalio, Druckenmiller, Marks, Soros, Lynch) + 3 supplementary seats (Financial Planning, Quant Risk, India Regulatory). Verdict: **7 REVISE, 0 REDESIGN, 0 APPROVE**. Do not re-run unless Tarun explicitly requests it.

4. **28-requirement inventory** — complete requirements assessment across 5 categories (A1-A10, B1-B4, C1-C6, D1-D4, E1-E4). Status mapped for all 28. Do not rebuild — pick up from the table.

5. **Strategic analysis on requirements** — 6-framework analysis delivered. CONSOLIDATE posture. Do not repeat.

---

## EXACT RESUME POINT

**Where we stopped:** Tarun said "I would have the council answer these questions, but first save all progress and complete housekeeping."

**What "the council answering questions" means:**
The council (7 financial expert seats) must now answer the 7 pre-build sign-off conditions — specifically the open decisions Tarun has not yet made. The council's role in the next session is to provide their best guidance on each decision so Tarun can decide efficiently rather than researching each from scratch.

**Next session first action:** Invoke panel-convene + the 7 expert seats to address each pre-build sign-off condition in turn. After the council runs, Tarun makes the 7 decisions. Then design review. Then build begins.

---

## 7 PRE-BUILD SIGN-OFF CONDITIONS (the gate — BUILD DOES NOT BEGIN UNTIL ALL ✓)

| # | Condition | Status | Council can help? |
|---|---|---|---|
| 1 | Data source decision: yfinance (personal) vs EODHD (commercial) | **OPEN — Tarun decides** | Yes — council will give cost/risk/ToS guidance |
| 2 | Stock classification schema in instrument table from G1 | **OPEN — CoS drafts** | CoS will produce draft next session |
| 3 | Bucket architecture design + Tarun's personal inputs (liquidity amount, horizon) | **OPEN — Tarun inputs** | Financial planning seat will give framework |
| 4 | Fundamental data layer decision (ROIC, FCF, P/E, PEG, promoter pledge — source?) | **OPEN — depends on #1** | Council will scope minimum viable fundamentals |
| 5 | Macro regime classifier scope (Dalio 4-quadrant inputs) | **OPEN — CoS drafts** | Dalio seat will specify exactly what data is needed |
| 6 | SEBI compliance path (personal / family / paid public) | **OPEN — Tarun decides** | Regulatory seat will lay out the decision tree |
| 7 | Position sizing framework (Kelly-based) | **OPEN — CoS drafts** | Quant Risk seat will produce the sizing model |

---

## 24 REQUIREMENTS — STATUS SNAPSHOT

**Have (from handover package):** Donor code (indicators.py, portfolio.py, forecast.py, market_data.py), schema SQL 0001+0002, seed files (sources + dependency graph), sweep tools, donor fixtures, synthesis prompts, SPEC.md, ARCHITECTURE.md, BUILD_PLAN.md, GSI_DONOR_AUDIT.md

**28 requirements across 5 categories (A1-A10 Technical, B1-B4 User Goals, C1-C6 Infrastructure, D1-D4 Commercial, E1-E4 Schema).**

**Decisions needed from Tarun (binary — next session):**
- A1: yfinance vs EODHD
- D1: SEBI path (personal / family / public)
- B2: Personal bucket inputs (₹ amount + when needed)
- B3: Risk profile / investment goals
- C1-C4: Environment confirmation (Supabase project? Python 3.12? Git repo? Node?)

**CoS can produce (once decisions above are made):**
- A2: Stock classification schema → instrument table addition
- A4: Macro regime classifier design → new migration + seed
- A5: Position sizing framework → recommendations table addition
- B1: Bucket architecture → migration 0003
- E1-E4: All schema additions

**Deferred (not needed until later gate):**
- B4 (family personas) → G6
- D2 (platform name) → G6
- C5 (Anthropic API key) → G4
- A7/A8/A9 (contrarian overlay, exit framework, magnitude accuracy) → G4/G5

---

## OPEN DECISIONS (Tarun-owned)

| Decision | Deadline | Impact |
|---|---|---|
| yfinance vs EODHD (A1) | Next session | Gates adapter design, all fundamentals, commercial ToS |
| SEBI compliance path (D1) | Next session | Gates commercial launch scope |
| Personal bucket inputs (B2) | Next session | Gates bucket architecture, Phase 2 schema |
| Investment goals / risk tolerance (B3) | Next session | Gates rebalancing engine objective function |
| Environment status (C1-C4) | Next session | Gates G0 build start date |

---

## COMMERCIAL STATE

- Stream A (Gumroad Starter Pack): STRATEGY_REVIEW_ACTIVE — active in separate session. Not this workspace.
- GSI financial tool commercial path: Confirmed intent (Tarun: "expected to help with commercials"). Commercial path depends on SEBI decision (D1) and data source decision (A1/D4).
- Stream C (financial consulting) via GSI: Available from day 1, no code required. Synthesis Chair recommendation from 2026-05-31 session still valid.

---

## PARALLEL SESSION NOTE

Stream A (governance pack) is active in a separate session. This workspace is the GSI financial tool ONLY. Do not conflate the two in the next session.

---

## FILES CREATED/MODIFIED THIS SESSION

| File | Status | Notes |
|---|---|---|
| `ideas/strategic_analysis.html` | NEW — staged for commit | Interactive 6-framework analysis, 10 sections, Chart.js |
| `graphify-out/GRAPH_REPORT.md` | Modified (auto-graph rebuild) | |
| `graphify-out/graph.html` | Modified (auto-graph rebuild) | |
| `graphify-out/graph.json` | Modified (auto-graph rebuild) | |

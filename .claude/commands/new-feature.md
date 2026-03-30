---
description: Before implementing any new feature, runs through the governance checklist, identifies the relevant skill, and produces a spec that satisfies all 7 policies.
---

Before writing a single line of code for a new feature, work through this checklist:

**Step 1 — Policy check** (read `GSI_GOVERNANCE.md`)
For the feature being requested, answer each:
- Policy 1 (Data Integrity): Does this feature display any dynamic value? If yes, what API call sources it?
- Policy 2 (Architecture): Which files will this touch? Does it maintain module boundaries?
- Policy 3 (UX): Will any new UI element wrap or overflow at 1280px? Does it have a loading state?
- Policy 4 (Regulatory): Does this show signals, recommendations, or named stocks? If yes, where does the SEBI disclaimer appear?
- Policy 5 (Data Coherence): Is this metric shown anywhere else in the app? If yes, will they use the same function?
- Policy 6 (Signal Arbitration): Does this involve BUY/WATCH/AVOID signals? If yes, is the Weinstein override hierarchy preserved?
- Policy 7 (Freshness): Does this show any data with a recency claim? If yes, how is the timestamp verified?

**Step 2 — Skill check** (read `GSI_SKILLS.md`)
Identify which skill(s) apply:
- Adding a KPI metric → Skill 1
- Adding an AI narrative section → Skill 2
- Adding an RSS feed → Skill 3
- Adding an expandable section → Skill 4
- Signal override logic → Skill 5
- yfinance for Indian stocks → Skill 6
- CSS for Streamlit 1.55 → Skill 7
- Regression checks → Skill 8
- Deploying to Cloud → Skill 9
- New GI topic → Skill 10

Read the relevant skill(s) before proceeding.

**Step 3 — Spec**
Produce a one-paragraph spec that includes:
- What the feature does
- Which file and function it lives in
- What data source it uses and at what TTL
- What the pass criterion is
- What regression check will enforce it (R-number or new check)

Get explicit approval of the spec before writing code.

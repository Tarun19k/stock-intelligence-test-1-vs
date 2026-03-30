---
description: Review the current sprint's completed work and plan the next sprint from open items. Reads GSI_session.json and produces a prioritised sprint plan.
---

Read `GSI_session.json` fully. Then:

**1. Sprint retrospective**
List all items completed in the most recent session:
- Version shipped
- Fixes with their audit reference IDs
- Regression baseline before and after
- QA verification status

**2. Open items by priority**
List all open items from `open_items` array, grouped:
- HIGH priority (fix in next sprint)
- MEDIUM priority (next 2 sprints)
- LOW priority (backlog)

For each HIGH item include: ID, title, target version, estimated effort (Low/Medium/High based on scope).

**3. Proposed next sprint scope**
Select the 5–7 most impactful HIGH items that:
- Can be batched logically (e.g., all data consistency fixes together)
- Don't have unresolved dependencies
- Have clear pass criteria

For each proposed item state:
- What file(s) change
- What function(s) change
- Pass criterion for QA

**4. Governance check**
For each proposed item, identify which of the 7 policies in `GSI_GOVERNANCE.md` it relates to. Flag any item that would require a new DO NOT UNDO rule.

Present the sprint plan as a table. Ask for confirmation before starting any work.

---
description: Generate a complete QA test brief for the fixes in the latest version. Reads version.py and GSI_QA_STANDARDS.md to produce a ready-to-send document for the QA analyst.
---

Read `version.py` to identify the most recent version entry and all changes it contains.
Read `GSI_QA_STANDARDS.md` to get the brief template and persona guidance.

For each fix in the latest version, produce a QA brief section following the exact template from GSI_QA_STANDARDS.md:

```
## Fix [N] — [Short name]
Audit ref: [audit ID if applicable]
File changed: [filename]
Function changed: [function name]

### What changed
[One sentence before/after]

### Where to look
Page: [exact page]
Navigate to: [step-by-step]
Section: [exact section name on screen]

### Before (what you would have seen in previous version)
[Exact text, value, or screenshot description]

### After (what you should see now)
[Exact text, value, or screenshot description]

### Pass criteria
[Single unambiguous condition]

### Fail criteria
[What constitutes a failure]

### Note
[Scope boundaries — what is NOT in scope]
```

Number fixes sequentially starting from 1.
At the end, add a "Cross-page spot check" section listing the 6 data consistency readings from GSI_QA_STANDARDS.md Section 9.
Add a "What I need back from QA" summary with must-have and good-to-have items.

Output as a clean markdown document ready to send to a QA analyst.

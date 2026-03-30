# Skill Creator — GSI Dashboard

Build, test, and refine new Claude Code skills for the GSI project using the Anthropic skill methodology.

## When to create a new skill
- A repeated workflow takes >5 minutes to set up from scratch each time
- A domain requires specific knowledge that I shouldn't have to rediscover (legal rules, API patterns)
- A task has clear inputs, outputs, and success criteria
- The skill would be invoked 3+ times in a typical sprint

## Skill structure (SKILL.md format)
```markdown
---
name: skill-name
description: One sentence — when to trigger this skill. Be specific.
---

# Skill Title

## When to use
[Precise trigger conditions]

## Core workflow
[Steps 1-N]

## GSI-specific constraints
[What's different here vs generic use]

## Output format
[What the skill produces]
```

## Testing methodology
1. Write 2-3 realistic test prompts (what a user would actually type)
2. Run once WITH skill active, once WITHOUT (baseline)
3. Compare: does the skill produce noticeably better output?
4. Check: is the skill adding instructions that I would follow anyway?
   If yes → skill is redundant, delete it

## Iteration rules
- Keep instructions lean and explanatory, not prescriptive
- Generalise from patterns, don't overfit to specific examples
- If a skill needs >3 pages of instructions, it's probably two skills
- Descriptions must be specific enough to trigger correctly AND not over-trigger

## GSI skill backlog (skills to build next)
- `perf-profile.md` — Streamlit memory profiling against 1GB limit
- `data-licensing.md` — check data source ToS before adding any new feed
- `accessibility.md` — colour contrast and screen reader audit

## Description optimisation (after a skill is built)
Test trigger accuracy: create 10 should-trigger + 10 should-not-trigger prompts.
If false positive rate >20% → tighten description.
If false negative rate >30% → broaden description.

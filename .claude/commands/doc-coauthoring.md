# Document Co-Authoring — GSI Dashboard

Structured workflow for creating substantial documents: product specs, QA briefs, marketing copy, user guides.

## When to use this skill
- Writing a new GSI governance document
- Drafting a product requirements doc (PRD)
- Creating user-facing documentation or onboarding guides
- Composing marketing copy (landing page, Product Hunt launch post, Reddit post)
- Writing a QA brief (use /qa-brief for the GSI-specific template)

## Three-stage workflow

### Stage 1 — Context gathering
Answer before writing:
- Who is the reader? (developer, retail investor, SEBI auditor, Product Hunt visitor)
- What decision/action should they take after reading?
- What format? (markdown, HTML, plain text, PDF)
- Length constraint?
- Tone? (technical, educational, marketing, regulatory)

### Stage 2 — Structure first, then fill
Build section headers with one-line placeholders.
Confirm structure before writing full content.
Fill section by section — never full rewrite, always surgical edits.

### Stage 3 — Reader testing
Before finalising, simulate a reader who has zero project context:
- What questions would they ask?
- What would confuse them?
- What is missing?

## GSI-specific writing rules
- Any document mentioning stock signals → include educational disclaimer
- Any document for Indian users → include SEBI non-registration notice
- Marketing copy → never say "investment advice", "guaranteed returns", "buy/sell"
- Technical docs → follow CLAUDE.md file structure conventions
- All new governance docs → append-only trail in GSI_AUDIT_TRAIL.md

## Edit protocol
Always use str_replace / Edit tool — never reprint full documents.
This prevents accidental content loss on large files.

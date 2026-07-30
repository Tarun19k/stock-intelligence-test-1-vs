# ADR-001: Product Boundary — Model B (Read-Only Decision-Support Tool)

**Status:** Accepted (2026-07-30, retroactively documented)
**Decision date:** 2026-07-30 (approved same day as OFFSET_HARVEST_YIELD_FOUNDATION.md Prereq 1)

## Context

The source material (`Knowledge Repository/AlphaVeda_idea` PDF, p.46) names four possible
operating models: (A) portfolio education tool, (B) decision-support tool, (C) personalised
advisory tool, (D) execution platform — and explicitly recommends starting with B: "a read-only
portfolio decision-support tool with simulated recommendations and no automatic execution."

## Decision

AlphaVeda's OHY/Trimurti layer adopts Model B. No automatic execution, no personalised advisory
claims — the tool compares options and surfaces evidence; the investor or advisor makes the
decision. This is the same boundary already implicit in AlphaVeda's existing SEBI compliance rules
(`alphaveda/.claude/rules/SEBI_COMPLIANCE.md`: no imperative signal language, no "you should buy X").

## Consequences

- Every Offset/Harvest/Yield engine output must be a category/comparison, never a direct
  instruction (`OFFSET_HARVEST_YIELD_FOUNDATION.md` section 6, "never sell as a direct
  instruction").
- Moving to Model C or D later requires a fresh ADR and fresh compliance review — not a silent
  scope creep.
- Commercial framing (Stream C, financial consulting) must stay "education only, no SEBI RIA" per
  global CLAUDE.md's business-goals mapping — consistent with Model B, not a coincidence.

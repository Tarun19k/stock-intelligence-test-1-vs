// SEBI disclaimer — pinned to bottom of every page via root layout.
// Text is a hardcoded, build-time constant — NOT a runtime env read. This is a
// SEBI-compliance requirement (see alphaveda/.claude/rules/SEBI_COMPLIANCE.md and
// ~/.claude/skills/sebi-compliance-reviewer/SKILL.md): regulatory copy must not be
// mutable via a dashboard edit with zero code review.
//
// Source of truth: alphaveda/constants.py SEBI_DISCLAIMER. This file's constant is
// mechanically derived from it — see alphaveda/scripts/generate_sebi_disclaimer_ts.py.
// Do not hand-edit sebi-disclaimer.generated.ts; regenerate it instead.
//
// NOTE: the Vercel SEBI_DISCLAIMER env var is now unused by this component and is
// deprecated. It has not been removed from Vercel/GHA config in this change — see
// alphaveda/docs/GAP_REGISTER.md NG-4 for the cleanup follow-up.

import { SEBI_DISCLAIMER as disclaimerText } from '@/lib/sebi-disclaimer.generated'

export default function SebiDisclaimer() {
  return (
    <div className="sebi-footer" role="complementary" aria-label="SEBI regulatory disclaimer">
      <span className="sebi-footer__icon" aria-hidden="true">⚠</span>
      {disclaimerText}
    </div>
  )
}

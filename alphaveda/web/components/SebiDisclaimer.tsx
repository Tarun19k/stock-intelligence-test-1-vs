// SEBI disclaimer — pinned to bottom of every page via root layout.
// Throws at module load if env var is not set — Vercel build fails before deploy.
// Text is authoritative in alphaveda/constants.py; update Vercel env var to match.

const disclaimerText = process.env.SEBI_DISCLAIMER
if (!disclaimerText) {
  throw new Error(
    'SEBI_DISCLAIMER env var is not set. Set it in Vercel project settings before deploying. ' +
    'Source of truth: alphaveda/constants.py SEBI_DISCLAIMER.'
  )
}

export default function SebiDisclaimer() {
  return (
    <div className="sebi-footer" role="complementary" aria-label="SEBI regulatory disclaimer">
      <span className="sebi-footer__icon" aria-hidden="true">⚠</span>
      {disclaimerText}
    </div>
  )
}

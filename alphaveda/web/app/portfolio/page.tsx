// TEMPORARILY DISABLED 2026-07-30 — real security finding, acted on immediately.
//
// A background commit-security review flagged broken-access-control and
// information-disclosure on this page. Real, correct finding: unlike
// /instrument or /build-checklist (unauthenticated but showing only synthetic
// or non-financial data), this page shows Tarun's ACTUAL real portfolio
// holdings -- real tickers, real quantities, real values -- to anyone who
// reaches the URL, with zero authentication. That precedent ("no auth is
// fine, low stakes") explicitly does not apply here; this page has real
// personal financial stakes and was shipped without re-deriving that
// distinction. Taking it down immediately rather than leaving real data
// exposed while a proper fix is built.
//
// Next step: real access control (a shared-secret or session-based gate)
// before this route is restored, not just re-enabled as-is.

export const dynamic = 'force-dynamic'

export default function PortfolioPageDisabled() {
  return (
    <div className="av-page" style={{ maxWidth: '600px', margin: '0 auto', padding: '3rem 1rem', textAlign: 'center' }}>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        This page is temporarily disabled while access control is added.
      </p>
    </div>
  )
}

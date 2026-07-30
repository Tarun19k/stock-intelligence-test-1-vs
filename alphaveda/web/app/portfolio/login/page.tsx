import { loginToPortfolio } from './actions'

export const dynamic = 'force-dynamic'

export default async function PortfolioLoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>
}) {
  const { error } = await searchParams

  return (
    <div className="av-page" style={{ maxWidth: '380px', margin: '0 auto', padding: '4rem 1rem' }}>
      <h1 className="av-heading" style={{ fontSize: '1.25rem' }}>Portfolio access</h1>
      <p className="av-subheading">
        This page shows real personal financial data. Enter the access token to continue.
      </p>

      {error && (
        <div className="av-banner av-banner--red" style={{ marginBottom: '1rem' }}>
          Incorrect token. Try again.
        </div>
      )}

      <form action={loginToPortfolio} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <input
          type="password"
          name="token"
          placeholder="Access token"
          required
          autoFocus
          className="mono"
          style={{
            padding: '0.6rem 0.75rem',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            fontSize: '0.9rem',
          }}
        />
        <button
          type="submit"
          style={{
            padding: '0.6rem 0.75rem',
            borderRadius: '6px',
            border: 'none',
            background: 'var(--indigo)',
            color: 'white',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          Unlock
        </button>
      </form>
    </div>
  )
}

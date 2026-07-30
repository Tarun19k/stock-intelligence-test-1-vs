import { redirect } from 'next/navigation'
import { getServerSupabase } from '@/lib/supabase'
import { isPortfolioSessionValid } from '@/lib/portfolio-auth'
import { logoutOfPortfolio } from './login/actions'

export const dynamic = 'force-dynamic'

type Holding = {
  id: string
  ticker: string
  qty: number
  avg_cost: number
  acquired_at: string
  source: string
}

type Tier = 'HIGH' | 'MID' | 'LOW'
const TIER_LABEL: Record<Tier, string> = { HIGH: '> 5% of portfolio', MID: '1–5% of portfolio', LOW: '< 1% of portfolio' }
function tierFor(concentration: number): Tier {
  if (concentration > 5) return 'HIGH'
  if (concentration >= 1) return 'MID'
  return 'LOW'
}

export default async function PortfolioPage() {
  // Restored 2026-07-31 behind real access control after the earlier version
  // (commit 33dc295) shipped with zero auth and was taken down same-day
  // (commit 8e491e0) once a security review flagged it. See lib/portfolio-auth.ts.
  const authorized = await isPortfolioSessionValid()
  if (!authorized) {
    redirect('/portfolio/login')
  }

  const supabase = getServerSupabase()
  const { data: holdings, error } = await supabase
    .from('holdings')
    .select('*')
    .order('qty', { ascending: false })

  if (error) {
    return (
      <div className="av-page">
        <p>Could not load holdings: {error.message}</p>
      </div>
    )
  }

  const rows = (holdings ?? []) as Holding[]
  // Real, objective math -- portfolio value and concentration are arithmetic,
  // not a G2 judgment call. No Offset/Harvest/Yield verdict is computed or
  // shown here -- that stays placeholder-only per Prereq 5/7 until Tarun's
  // methodology closes (see scripts/ohy_synthetic_prototype.py for where
  // that logic lives today, clearly labeled synthetic).
  const withValue = rows.map((h) => ({ ...h, value: h.qty * h.avg_cost }))
  const totalValue = withValue.reduce((sum, h) => sum + h.value, 0)
  const withConcentration = withValue
    .map((h) => {
      const concentration = totalValue ? (100 * h.value) / totalValue : 0
      return { ...h, concentration, tier: tierFor(concentration) }
    })
    .sort((a, b) => b.concentration - a.concentration)

  // Real aggregation for the concentration bar -- top 5 named segments, rest
  // bucketed. Not a new metric, just a visual sum of numbers already computed.
  const top5 = withConcentration.slice(0, 5)
  const otherPct = withConcentration.slice(5).reduce((s, h) => s + h.concentration, 0)
  const otherCount = withConcentration.length - top5.length

  const tierGroups: Record<Tier, typeof withConcentration> = { HIGH: [], MID: [], LOW: [] }
  for (const h of withConcentration) tierGroups[h.tier].push(h)

  return (
    <div className="av-page" style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <div style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Real portfolio data — ingested from broker P&L, account holder: John Doe, 2026-07-30
          </div>
          <h1 style={{ margin: '0.2rem 0 0', fontSize: '1.6rem' }}>Portfolio Health</h1>
        </div>
        <form action={logoutOfPortfolio}>
          <button
            type="submit"
            style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
          >
            Lock this page
          </button>
        </form>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.7rem' }}>
        <div className="av-card" style={{ padding: '0.8rem 1rem' }}>
          <div className="av-stat__value">Rs.{totalValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div className="av-stat__label">Cost-basis value</div>
        </div>
        <div className="av-card" style={{ padding: '0.8rem 1rem' }}>
          <div className="av-stat__value">{rows.length}</div>
          <div className="av-stat__label">Holdings</div>
        </div>
        <div className="av-card" style={{ padding: '0.8rem 1rem' }}>
          <div className="av-stat__value">
            {withConcentration[0] ? `${withConcentration[0].concentration.toFixed(1)}%` : '—'}
          </div>
          <div className="av-stat__label">Largest position</div>
        </div>
      </div>

      <div>
        <div className="av-stat__label" style={{ marginBottom: '0.4rem' }}>Concentration at a glance</div>
        <a href="#holdings-table" style={{ display: 'flex', height: '1.75rem', borderRadius: '4px', overflow: 'hidden', textDecoration: 'none' }}>
          {top5.map((h, i) => (
            <div
              key={h.id}
              title={`${h.ticker}: ${h.concentration.toFixed(1)}%`}
              style={{
                width: `${h.concentration}%`,
                background: `color-mix(in srgb, var(--indigo, #4a5b9e) ${100 - i * 12}%, transparent)`,
                minWidth: h.concentration > 3 ? 'auto' : '2px',
              }}
            />
          ))}
          {otherPct > 0 && (
            <div title={`Other (${otherCount} holdings): ${otherPct.toFixed(1)}%`} style={{ width: `${otherPct}%`, background: 'var(--border)' }} />
          )}
        </a>
        <div className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
          Top 5: {top5.map((h) => `${h.ticker} ${h.concentration.toFixed(1)}%`).join(' · ')}
          {otherCount > 0 && ` · Other (${otherCount}) ${otherPct.toFixed(1)}%`}
        </div>
      </div>

      <div style={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: '8px', padding: '0.7rem 1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Concentration and portfolio value above are real arithmetic on the account holder&apos;s real
        holdings — no
        Offset/Harvest/Yield judgment is applied here. That logic remains placeholder-only
        (see <code>scripts/ohy_synthetic_prototype.py</code>) until Prereq 5/7&apos;s methodology is
        approved. This page has not yet had Financial Council review per Rule E
        (<code>COUNCIL_RULES.md</code>) — flagging, not skipping that gate.
      </div>

      <div id="holdings-table" style={{ overflowX: 'auto' }}>
        <table className="av-table av-table--portfolio">
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }}>Ticker</th>
              <th className="av-col--secondary" style={{ textAlign: 'right' }}>Qty</th>
              <th className="av-col--secondary" style={{ textAlign: 'right' }}>Avg cost</th>
              <th style={{ textAlign: 'right' }}>Value</th>
              <th style={{ textAlign: 'right' }}>Concentration</th>
            </tr>
          </thead>
          <tbody>
            {(['HIGH', 'MID', 'LOW'] as Tier[]).map((tier) =>
              tierGroups[tier].length === 0 ? null : (
                <>
                  <tr key={`${tier}-header`}>
                    <td colSpan={5} className="mono" style={{ background: 'var(--surface2)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-muted)', padding: '0.4rem 0.75rem' }}>
                      {TIER_LABEL[tier]} — {tierGroups[tier].length} holding{tierGroups[tier].length === 1 ? '' : 's'}, {tierGroups[tier].reduce((s, h) => s + h.concentration, 0).toFixed(1)}% of portfolio
                    </td>
                  </tr>
                  {tierGroups[tier].map((h) => (
                    <tr key={h.id}>
                      <td className="mono">
                        {h.ticker}
                        <span className="av-secondary-line">qty {h.qty} · avg Rs.{h.avg_cost.toFixed(2)}</span>
                      </td>
                      <td className="av-col--secondary mono" style={{ textAlign: 'right' }}>{h.qty}</td>
                      <td className="av-col--secondary mono" style={{ textAlign: 'right' }}>{h.avg_cost.toFixed(2)}</td>
                      <td className="mono" style={{ textAlign: 'right' }}>{h.value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                      <td className="mono" style={{ textAlign: 'right' }}>{h.concentration.toFixed(1)}%</td>
                    </tr>
                  ))}
                </>
              )
            )}
          </tbody>
        </table>
      </div>

      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        AlphaVeda is a personal research tool, not a SEBI-registered Research Analyst or Investment
        Adviser. Research purposes only — not investment advice.
      </p>
    </div>
  )
}

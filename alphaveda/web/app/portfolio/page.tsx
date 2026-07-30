import { getServerSupabase } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

type Holding = {
  id: string
  ticker: string
  qty: number
  avg_cost: number
  acquired_at: string
  source: string
}

export default async function PortfolioPage() {
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
    .map((h) => ({ ...h, concentration: totalValue ? (100 * h.value) / totalValue : 0 }))
    .sort((a, b) => b.concentration - a.concentration)

  return (
    <div className="av-page" style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
        <div style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          Real portfolio data — ingested from your broker P&L, 2026-07-30
        </div>
        <h1 style={{ margin: '0.2rem 0 0', fontSize: '1.6rem' }}>Portfolio Health</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.7rem' }}>
        <div className="av-card" style={{ padding: '0.8rem 1rem' }}>
          <div style={{ fontFamily: 'monospace', fontSize: '1.4rem', fontWeight: 600 }}>Rs.{totalValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Cost-basis value</div>
        </div>
        <div className="av-card" style={{ padding: '0.8rem 1rem' }}>
          <div style={{ fontFamily: 'monospace', fontSize: '1.4rem', fontWeight: 600 }}>{rows.length}</div>
          <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Holdings</div>
        </div>
        <div className="av-card" style={{ padding: '0.8rem 1rem' }}>
          <div style={{ fontFamily: 'monospace', fontSize: '1.4rem', fontWeight: 600 }}>
            {withConcentration[0] ? `${withConcentration[0].concentration.toFixed(1)}%` : '—'}
          </div>
          <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Largest position</div>
        </div>
      </div>

      <div style={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: '8px', padding: '0.7rem 1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Concentration and portfolio value above are real arithmetic on your real holdings — no
        Offset/Harvest/Yield judgment is applied here. That logic remains placeholder-only
        (see <code>scripts/ohy_synthetic_prototype.py</code>) until Prereq 5/7&apos;s methodology is
        approved. This page has not yet had Financial Council review per Rule E
        (<code>COUNCIL_RULES.md</code>) — flagging, not skipping that gate.
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <th style={{ textAlign: 'left', padding: '0.5rem' }}>Ticker</th>
              <th style={{ textAlign: 'right', padding: '0.5rem' }}>Qty</th>
              <th style={{ textAlign: 'right', padding: '0.5rem' }}>Avg cost</th>
              <th style={{ textAlign: 'right', padding: '0.5rem' }}>Value</th>
              <th style={{ textAlign: 'right', padding: '0.5rem' }}>Concentration</th>
            </tr>
          </thead>
          <tbody>
            {withConcentration.map((h) => (
              <tr key={h.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '0.5rem', fontFamily: 'monospace' }}>{h.ticker}</td>
                <td style={{ padding: '0.5rem', textAlign: 'right', fontFamily: 'monospace' }}>{h.qty}</td>
                <td style={{ padding: '0.5rem', textAlign: 'right', fontFamily: 'monospace' }}>{h.avg_cost.toFixed(2)}</td>
                <td style={{ padding: '0.5rem', textAlign: 'right', fontFamily: 'monospace' }}>{h.value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                <td style={{ padding: '0.5rem', textAlign: 'right', fontFamily: 'monospace' }}>{h.concentration.toFixed(1)}%</td>
              </tr>
            ))}
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

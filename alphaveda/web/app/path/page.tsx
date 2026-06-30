import { getServerSupabase } from '@/lib/supabase'
import { isCommercial } from '@/lib/commercial'

const PORTFOLIO_VALUE = 725000
const QUARTER_KELLY_FRACTION = 0.25
const MAX_POSITION_PCT = 0.10

type Prediction = {
  id: number
  instrument_id: number
  direction: string
  confidence: number
  magnitude_target: number | null
  downside_target: number | null
  emitted_at: string
}

type Instrument = { id: number; ticker: string; classification: string }

function kellyRupee(confidence: number, magnitude: number, downside: number): number | null {
  if (!magnitude || !downside || downside <= 0) return null
  const p = confidence / 100
  const b = magnitude / downside
  const kelly = p - (1 - p) / b
  if (kelly <= 0) return null
  const quarterKelly = kelly * QUARTER_KELLY_FRACTION
  const capped = Math.min(quarterKelly, MAX_POSITION_PCT)
  return Math.round(capped * PORTFOLIO_VALUE)
}

export const revalidate = 3600

export default async function PathPage() {
  const sb = getServerSupabase()
  const commercial = await isCommercial()

  const [predsRes, instsRes, proposedRes] = await Promise.all([
    sb.from('accuracy_predictions')
      .select('id,instrument_id,direction,confidence,magnitude_target,downside_target,emitted_at')
      .order('emitted_at', { ascending: false })
      .limit(20),
    sb.from('instruments').select('id,ticker,classification'),
    sb.from('signal_weights').select('id', { count: 'exact' }).eq('status', 'PROPOSED'),
  ])

  const predictions: Prediction[] = predsRes.data ?? []
  const instruments: Instrument[] = instsRes.data ?? []
  const proposedCount = proposedRes.count ?? 0

  const instById = new Map(instruments.map((i) => [i.id, i]))

  return (
    <>
      <h1 className="av-heading">Path</h1>
      <p className="av-subheading">
        Kelly-based position sizing — research purposes only
      </p>

      {proposedCount > 0 && (
        <div className="av-banner av-banner--amber">
          ⚠ {proposedCount} PROPOSED weight update{proposedCount !== 1 ? 's' : ''} pending review.
        </div>
      )}

      {commercial && (
        <div className="av-banner av-banner--blue">
          DELIBERATE STATE — Position sizes suppressed in research mode.
          Signal direction and confidence are shown; rupee amounts require a personal-use context.
        </div>
      )}

      <div className="av-card" style={{ overflowX: 'auto' }}>
        {predictions.length === 0 ? (
          <div className="av-empty">
            <p className="av-empty__title">No predictions available</p>
            <p>Signals must be emitted before Kelly sizing can be computed.</p>
          </div>
        ) : (
          <table className="av-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Signal</th>
                <th style={{ textAlign: 'right' }}>Confidence</th>
                <th style={{ textAlign: 'right' }}>Target</th>
                <th style={{ textAlign: 'right' }}>Stop</th>
                <th style={{ textAlign: 'right' }}>
                  {commercial ? 'Size' : 'Kelly (₹)'}
                </th>
                <th>Emitted</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p) => {
                const inst = instById.get(p.instrument_id)
                const rupee = (!commercial && p.magnitude_target && p.downside_target)
                  ? kellyRupee(p.confidence, p.magnitude_target, p.downside_target)
                  : null
                return (
                  <tr key={p.id}>
                    <td className="mono">{inst?.ticker ?? p.instrument_id}</td>
                    <td>
                      <span className={`pill pill--${p.direction === 'BULL' ? 'bull' : 'bear'}`}>
                        {p.direction}
                      </span>
                    </td>
                    <td className="mono" style={{ textAlign: 'right' }}>{p.confidence}%</td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {p.magnitude_target != null ? `${p.magnitude_target.toFixed(1)}%` : '—'}
                    </td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {p.downside_target != null ? `${p.downside_target.toFixed(1)}%` : '—'}
                    </td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {commercial
                        ? <span style={{ color: 'var(--text-muted)' }}>–</span>
                        : rupee != null
                          ? `₹${rupee.toLocaleString('en-IN')}`
                          : '—'}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem' }}>
                      {p.emitted_at.slice(0, 10)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {!commercial && (
        <p style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Portfolio value: ₹{PORTFOLIO_VALUE.toLocaleString('en-IN')} · Quarter Kelly · Max {(MAX_POSITION_PCT * 100).toFixed(0)}% per position
        </p>
      )}
    </>
  )
}

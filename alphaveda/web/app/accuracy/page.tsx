import { getServerSupabase } from '@/lib/supabase'

const STALENESS_DAYS = 90

type Outcome = {
  id: number
  prediction_id: number
  resolved_at: string
  hit: boolean
  return_pct: number
}

type Prediction = {
  id: number
  instrument_id: number
  direction: string
  confidence: number
  emitted_at: string
}

type Instrument = { id: number; ticker: string }

function daysBetween(dateStr: string, now: Date): number {
  return Math.floor((now.getTime() - new Date(dateStr).getTime()) / 86_400_000)
}

export const revalidate = 3600

export default async function AccuracyPage() {
  const sb = getServerSupabase()
  const now = new Date()

  const [outcomesRes, predsRes, instsRes, proposedRes] = await Promise.all([
    sb.from('accuracy_outcomes').select('id,prediction_id,resolved_at,hit,return_pct').order('resolved_at', { ascending: false }).limit(100),
    sb.from('accuracy_predictions').select('id,instrument_id,direction,confidence,emitted_at'),
    sb.from('instruments').select('id,ticker'),
    sb.from('signal_weights').select('id,approved_at', { count: 'exact' }).eq('status', 'PROPOSED'),
  ])

  const outcomes: Outcome[] = outcomesRes.data ?? []
  const predictions: Prediction[] = predsRes.data ?? []
  const instruments: Instrument[] = instsRes.data ?? []
  const proposedCount = proposedRes.count ?? 0

  const predById = new Map(predictions.map((p) => [p.id, p]))
  const tickerById = new Map(instruments.map((i) => [i.id, i.ticker]))

  const totalHits = outcomes.filter((o) => o.hit).length
  const hitRate = outcomes.length > 0 ? (totalHits / outcomes.length) * 100 : null

  const avgReturn = outcomes.length > 0
    ? outcomes.reduce((sum, o) => sum + o.return_pct, 0) / outcomes.length
    : null

  // Staleness: based on most recent weight approval
  const weightRes = await sb.from('signal_weights').select('approved_at').eq('status', 'ACTIVE').order('approved_at', { ascending: false }).limit(1)
  const lastApproval = weightRes.data?.[0]?.approved_at ?? null
  const weightStaleDays = lastApproval ? daysBetween(lastApproval, now) : null
  const weightsStale = weightStaleDays !== null && weightStaleDays > STALENESS_DAYS

  return (
    <>
      <h1 className="av-heading">Accuracy Ledger</h1>
      <p className="av-subheading">
        Prediction outcomes — populates once predictions reach the observation threshold
      </p>

      {proposedCount > 0 && (
        <div className="av-banner av-banner--amber">
          ⚠ {proposedCount} PROPOSED weight update{proposedCount !== 1 ? 's' : ''} pending review.
        </div>
      )}

      {weightsStale && (
        <div className="av-banner av-banner--amber">
          ⚠ Signal weights not reviewed in {weightStaleDays} days (threshold: {STALENESS_DAYS} days).
          Consider reviewing active weights for staleness.
        </div>
      )}

      <div className="av-grid av-grid--4" style={{ marginBottom: '1.5rem' }}>
        <div className="av-card">
          <div className="av-stat__label">Total Resolved</div>
          <div className="av-stat__value">{outcomes.length}</div>
        </div>
        <div className="av-card">
          <div className="av-stat__label">Hit Rate</div>
          <div className="av-stat__value" style={{ color: hitRate != null && hitRate >= 50 ? 'var(--emerald)' : 'var(--terra)' }}>
            {hitRate != null ? `${hitRate.toFixed(1)}%` : '—'}
          </div>
        </div>
        <div className="av-card">
          <div className="av-stat__label">Avg Return</div>
          <div className="av-stat__value" style={{ color: avgReturn != null && avgReturn >= 0 ? 'var(--emerald)' : 'var(--terra)' }}>
            {avgReturn != null ? `${avgReturn.toFixed(2)}%` : '—'}
          </div>
        </div>
        <div className="av-card">
          <div className="av-stat__label">Pending Review</div>
          <div className="av-stat__value" style={{ color: proposedCount > 0 ? 'var(--gold)' : 'var(--text)' }}>
            {proposedCount}
          </div>
        </div>
      </div>

      <div className="av-card" style={{ overflowX: 'auto' }}>
        {outcomes.length === 0 ? (
          <div className="av-empty">
            <p className="av-empty__title">No outcomes yet</p>
            <p>Populates once predictions reach the observation threshold and begin resolving.</p>
          </div>
        ) : (
          <table className="av-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Signal</th>
                <th style={{ textAlign: 'right' }}>Confidence</th>
                <th>Hit</th>
                <th style={{ textAlign: 'right' }}>Return</th>
                <th>Resolved</th>
              </tr>
            </thead>
            <tbody>
              {outcomes.map((o) => {
                const pred = predById.get(o.prediction_id)
                const ticker = pred ? tickerById.get(pred.instrument_id) : null
                return (
                  <tr key={o.id}>
                    <td className="mono">{ticker ?? '—'}</td>
                    <td>
                      {pred
                        ? <span className={`pill pill--${pred.direction === 'BULL' ? 'bull' : 'bear'}`}>{pred.direction}</span>
                        : '—'}
                    </td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {pred ? `${pred.confidence}%` : '—'}
                    </td>
                    <td>
                      <span style={{ color: o.hit ? 'var(--emerald)' : 'var(--terra)', fontWeight: 500 }}>
                        {o.hit ? '✓' : '✗'}
                      </span>
                    </td>
                    <td className="mono" style={{ textAlign: 'right', color: o.return_pct >= 0 ? 'var(--emerald)' : 'var(--terra)' }}>
                      {o.return_pct >= 0 ? '+' : ''}{o.return_pct.toFixed(2)}%
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem' }}>{o.resolved_at.slice(0, 10)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}

import { getServerSupabase } from '@/lib/supabase'

const OBSERVATION_THRESHOLD = 30

type SignalWeight = {
  id: number
  signal_name: string
  weight: number
  status: string
  lynch_class: string
  regime: string
}

type Prediction = {
  id: number
  instrument_id: number
  direction: string
  confidence: number
  emitted_at: string
  lynch_class: string | null
}

type Instrument = { id: number; ticker: string }

export const revalidate = 3600

export default async function SignalsPage() {
  const sb = getServerSupabase()

  const [weightsRes, predsRes, instsRes, proposedRes] = await Promise.all([
    sb.from('signal_weights').select('id,signal_name,weight,status,lynch_class,regime').eq('status', 'ACTIVE').order('weight', { ascending: false }),
    sb.from('accuracy_predictions').select('id,instrument_id,direction,confidence,emitted_at,lynch_class').order('emitted_at', { ascending: false }).limit(50),
    sb.from('instruments').select('id,ticker'),
    sb.from('signal_weights').select('id', { count: 'exact' }).eq('status', 'PROPOSED'),
  ])

  const weights: SignalWeight[] = weightsRes.data ?? []
  const predictions: Prediction[] = predsRes.data ?? []
  const instruments: Instrument[] = instsRes.data ?? []
  const proposedCount = proposedRes.count ?? 0

  const tickerById = new Map(instruments.map((i) => [i.id, i.ticker]))
  const isColdStart = predictions.length < OBSERVATION_THRESHOLD

  return (
    <>
      <h1 className="av-heading">Signals</h1>
      <p className="av-subheading">
        Research signals only — not investment advice
      </p>

      {proposedCount > 0 && (
        <div className="av-banner av-banner--amber">
          ⚠ {proposedCount} PROPOSED weight update{proposedCount !== 1 ? 's' : ''} pending review.
          Weights require approval by an authorised reviewer before activation.
        </div>
      )}

      {isColdStart && (
        <div className="av-banner av-banner--blue">
          COLD START — {predictions.length} of {OBSERVATION_THRESHOLD} observations accumulated.
          Signals are using Bayesian prior weights until the threshold is reached.
        </div>
      )}

      <div style={{ display: 'grid', gap: '1.5rem' }}>
        <div className="av-card">
          <h2 style={{ fontFamily: 'Fraunces, serif', fontSize: '1.1rem', marginBottom: '1rem' }}>
            Recent Predictions
          </h2>
          {predictions.length === 0 ? (
            <div className="av-empty">
              <p className="av-empty__title">No predictions yet</p>
              <p>Select an instrument and segment to generate a signal.</p>
            </div>
          ) : (
            <table className="av-table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Signal</th>
                  <th style={{ textAlign: 'right' }}>Confidence</th>
                  <th>Class</th>
                  <th>Emitted</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((p) => (
                  <tr key={p.id}>
                    <td className="mono">{tickerById.get(p.instrument_id) ?? p.instrument_id}</td>
                    <td>
                      <span className={`pill pill--${p.direction === 'BULL' ? 'bull' : 'bear'}`}>
                        {p.direction}
                      </span>
                    </td>
                    <td className="mono" style={{ textAlign: 'right' }}>{p.confidence}%</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {p.lynch_class ?? '—'}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem' }}>
                      {p.emitted_at.slice(0, 10)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="av-card">
          <h2 style={{ fontFamily: 'Fraunces, serif', fontSize: '1.1rem', marginBottom: '1rem' }}>
            Active Signal Weights
          </h2>
          {weights.length === 0 ? (
            <div className="av-empty">
              <p className="av-empty__title">No active weights</p>
              <p>Run the ingest pipeline to generate weight proposals.</p>
            </div>
          ) : (
            <table className="av-table">
              <thead>
                <tr>
                  <th>Signal</th>
                  <th>Class</th>
                  <th>Regime</th>
                  <th style={{ textAlign: 'right' }}>Weight</th>
                </tr>
              </thead>
              <tbody>
                {weights.map((w) => (
                  <tr key={w.id}>
                    <td className="mono">{w.signal_name}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{w.lynch_class}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{w.regime}</td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {(w.weight * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  )
}

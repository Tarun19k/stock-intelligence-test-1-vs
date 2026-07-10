import { getServerSupabase } from '@/lib/supabase'
import { LexOrRaw } from '@/components/Lex'
import ProbabilityFrame from '@/components/ProbabilityFrame'
import { directionLexKey, lynchClassLexKey, regimeLexKey } from '@/lib/lexicon'

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
  regime_tag: string | null
}

type Instrument = { id: number; ticker: string }

export const revalidate = 3600

// Segment = (lynch_class, regime_tag) — the same grouping used server-side for
// weight cold-start (alphaveda/src/signals/weights.py). A segment with fewer
// than OBSERVATION_THRESHOLD observations has not earned a calibrated confidence
// figure; showing a bare percentage there manufactures false trust (G7 bridge /
// A4). Mirrors the lexicon's ledger.cold pattern ("TOO EARLY" / "New types get
// graded after 30 results.").
function segmentKey(lynchClass: string | null, regimeTag: string | null): string {
  return `${lynchClass ?? 'unknown'}::${regimeTag ?? 'unknown'}`
}

export default async function SignalsPage() {
  const sb = getServerSupabase()

  const [weightsRes, allPredsRes, instsRes, proposedRes] = await Promise.all([
    sb.from('signal_weights').select('id,signal_name,weight,status,lynch_class,regime').eq('status', 'ACTIVE').order('weight', { ascending: false }),
    // No .limit() here: segment observation counts must reflect the full table,
    // not just the most recent page — same unlimited-fetch pattern already used
    // on the Accuracy page for its predictions join.
    sb.from('accuracy_predictions').select('id,instrument_id,direction,confidence,emitted_at,lynch_class,regime_tag').order('emitted_at', { ascending: false }),
    sb.from('instruments').select('id,ticker'),
    sb.from('signal_weights').select('id', { count: 'exact' }).eq('status', 'PROPOSED'),
  ])

  const weights: SignalWeight[] = weightsRes.data ?? []
  const allPredictions: Prediction[] = allPredsRes.data ?? []
  const predictions: Prediction[] = allPredictions.slice(0, 50)
  const instruments: Instrument[] = instsRes.data ?? []
  const proposedCount = proposedRes.count ?? 0

  const tickerById = new Map(instruments.map((i) => [i.id, i.ticker]))
  const isColdStart = allPredictions.length < OBSERVATION_THRESHOLD

  const segmentCounts = new Map<string, number>()
  for (const p of allPredictions) {
    const key = segmentKey(p.lynch_class, p.regime_tag)
    segmentCounts.set(key, (segmentCounts.get(key) ?? 0) + 1)
  }
  function segmentObs(p: Prediction): number {
    return segmentCounts.get(segmentKey(p.lynch_class, p.regime_tag)) ?? 0
  }

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
          COLD START — {allPredictions.length} of {OBSERVATION_THRESHOLD} observations accumulated.
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
                        <LexOrRaw k={directionLexKey(p.direction)} fallback={p.direction} />
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {segmentObs(p) < OBSERVATION_THRESHOLD ? (
                        <span
                          className="pill"
                          style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}
                          title={`${segmentObs(p)} of ${OBSERVATION_THRESHOLD} results for this type — too early to grade`}
                        >
                          TOO EARLY
                        </span>
                      ) : (
                        <ProbabilityFrame pct={p.confidence} />
                      )}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {p.lynch_class
                        ? <LexOrRaw k={lynchClassLexKey(p.lynch_class)} fallback={p.lynch_class} />
                        : '—'}
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
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <LexOrRaw k={lynchClassLexKey(w.lynch_class)} fallback={w.lynch_class} />
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <LexOrRaw k={regimeLexKey(w.regime)} fallback={w.regime} />
                    </td>
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

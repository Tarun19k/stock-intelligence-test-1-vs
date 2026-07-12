import { getServerSupabase } from '@/lib/supabase'
import { isCommercial, isPersonalContext } from '@/lib/commercial'
import Lex, { LexOrRaw } from '@/components/Lex'
import ProbabilityFrame from '@/components/ProbabilityFrame'
import type { LexKey } from '@/lib/lexicon'

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

type KellyResult = { rupee: number | null; band: 'above' | 'within' | 'below' }

// A13 fix (F2, Fable round table 2026-07-10): the Path/Portfolio surface is
// where a user reviews positions they may already hold — a BULL/BEAR verdict
// pill next to a held position reads as an implicit sell/buy instruction even
// with analytical wording (loss-aversion effect, Munger seat). Fix: this
// surface leads with the Kelly band position (ABOVE/WITHIN/BELOW range,
// already analytical, matches lexicon §3 port.above/within/below) and does
// NOT repeat the raw directional verdict pill. The Signals page is
// unaffected — it has no "held position" context, so its verdict pill stays.
function kellyBand(confidence: number, magnitude: number, downside: number): KellyResult {
  if (!magnitude || !downside || downside <= 0) return { rupee: null, band: 'below' }
  const p = confidence / 100
  const b = magnitude / downside
  const kelly = p - (1 - p) / b
  if (kelly <= 0) return { rupee: null, band: 'below' }
  const quarterKelly = kelly * QUARTER_KELLY_FRACTION
  const capped = Math.min(quarterKelly, MAX_POSITION_PCT)
  const rupee = Math.round(capped * PORTFOLIO_VALUE)
  const band: KellyResult['band'] = quarterKelly > MAX_POSITION_PCT ? 'above' : 'within'
  return { rupee, band }
}

const BAND_LEX: Record<KellyResult['band'], LexKey> = {
  above: 'port.above',
  within: 'port.within',
  below: 'port.below',
}

export const revalidate = 3600

export default async function PathPage() {
  const sb = getServerSupabase()
  const commercial = await isCommercial()
  // NG-2 / A5: rupee amounts are derived from Tarun's personal PORTFOLIO_VALUE.
  // Public/unauthenticated visitors — which today means everyone, since there is
  // no auth layer — must see band position only, never the literal figure.
  const showRupee = !commercial && isPersonalContext()

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
        <Lex k="port.subtitle" />
      </p>

      {proposedCount > 0 && (
        <div className="av-banner av-banner--amber">
          ⚠ {proposedCount} PROPOSED weight update{proposedCount !== 1 ? 's' : ''} pending review.
        </div>
      )}

      {!showRupee && (
        <div className="av-banner av-banner--blue">
          DELIBERATE STATE — Position sizes suppressed in research mode.
          Signal direction and confidence are shown; rupee amounts require a personal-use context.
        </div>
      )}

      <div className="av-card" style={{ overflowX: 'auto' }}>
        {predictions.length === 0 ? (
          <div className="av-empty">
            <p className="av-empty__title">No positions yet</p>
            <p>We&apos;re still setting up. Check back soon.</p>
          </div>
        ) : (
          <table className="av-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Position vs. band</th>
                <th style={{ textAlign: 'right' }}>Confidence</th>
                <th style={{ textAlign: 'right' }}>Target</th>
                <th style={{ textAlign: 'right' }}>Stop</th>
                <th style={{ textAlign: 'right' }}>
                  {showRupee ? 'Kelly (₹)' : 'Size'}
                </th>
                <th>Emitted</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p) => {
                const inst = instById.get(p.instrument_id)
                const result = (p.magnitude_target && p.downside_target)
                  ? kellyBand(p.confidence, p.magnitude_target, p.downside_target)
                  : null
                const rupee = showRupee ? (result?.rupee ?? null) : null
                return (
                  <tr key={p.id}>
                    <td className="mono">{inst?.ticker ?? p.instrument_id}</td>
                    <td>
                      {result
                        ? <span className="pill">
                            <LexOrRaw k={BAND_LEX[result.band]} fallback={result.band.toUpperCase()} />
                          </span>
                        : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                    </td>
                    <td style={{ textAlign: 'right' }}><ProbabilityFrame pct={p.confidence} /></td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {p.magnitude_target != null ? `${p.magnitude_target.toFixed(1)}%` : '—'}
                    </td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {p.downside_target != null ? `${p.downside_target.toFixed(1)}%` : '—'}
                    </td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {!showRupee
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

      {showRupee ? (
        <p style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Portfolio value: ₹{PORTFOLIO_VALUE.toLocaleString('en-IN')} · <Lex k="port.method" /> · Max {(MAX_POSITION_PCT * 100).toFixed(0)}% per position
        </p>
      ) : (
        <p style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Position sizing method: <Lex k="port.method" /> · Max {(MAX_POSITION_PCT * 100).toFixed(0)}% per position — band shown, rupee amounts hidden in research mode.
        </p>
      )}
    </>
  )
}

import { getServerSupabase } from '@/lib/supabase'
import Lex, { LexOrRaw } from '@/components/Lex'
import ProbabilityFrame from '@/components/ProbabilityFrame'
import { directionLexKey } from '@/lib/lexicon'

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

  // RF-I coverage check (2026-07-20): computed live, not hardcoded, so this
  // banner self-corrects the moment RF-I is actually fixed rather than
  // needing a manual follow-up edit. Instruments with a prediction in the
  // last 10 days are "covered"; anything less is a real, disclosed gap.
  const recentCutoff = new Date(now.getTime() - 10 * 86_400_000)
  const coveredInstrumentIds = new Set(
    predictions.filter((p) => new Date(p.emitted_at) >= recentCutoff).map((p) => p.instrument_id)
  )
  const coverageGapCount = instruments.length - coveredInstrumentIds.size
  const hasCoverageGap = coverageGapCount > 0

  return (
    <>
      <h1 className="av-heading"><Lex k="ledger.title" /></h1>
      <p className="av-subheading">
        A public record of every call we&apos;ve made and how it turned out
      </p>

      <div className="av-banner av-banner--amber">
        Past performance is not indicative of future results. The success percentage and
        returns below are a historical record only — they do not predict what will happen
        next, and results can get worse as well as better. Negative returns are a normal
        part of this record and carry real downside risk if acted on; nothing here is a
        guarantee or a recommendation.
      </div>

      {hasCoverageGap && (
        <div className="av-banner av-banner--amber">
          ⚠ Known coverage gap under investigation: {coverageGapCount} of {instruments.length} tracked
          stocks have not received a new signal in the last 10 days. The figures below reflect only
          the stocks currently generating signals, not the full tracked list — treat this record as
          provisional until this is resolved.
        </div>
      )}

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
          <div className="av-stat__label"><Lex k="ledger.hit_label" /></div>
          <div className="av-stat__value" style={{ color: hitRate != null && hitRate >= 50 ? 'var(--emerald)' : 'var(--terra)' }}>
            {hitRate != null ? <ProbabilityFrame pct={hitRate} /> : '—'}
          </div>
        </div>
        <div className="av-card">
          <div className="av-stat__label">Avg Return</div>
          <div className="av-stat__value" style={{ color: avgReturn != null && avgReturn >= 0 ? 'var(--emerald)' : 'var(--terra)' }}>
            {avgReturn != null ? `${avgReturn.toFixed(2)}%` : '—'}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Average of past outcomes only — individual results vary and losses are possible.
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
            <p className="av-empty__title">No results yet</p>
            <p>We grade every call once enough time has passed. Check back soon.</p>
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
                        ? <span className={`pill pill--${pred.direction === 'BULL' ? 'bull' : 'bear'}`}>
                            <LexOrRaw k={directionLexKey(pred.direction)} fallback={pred.direction} />
                          </span>
                        : '—'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {pred ? <ProbabilityFrame pct={pred.confidence} /> : '—'}
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

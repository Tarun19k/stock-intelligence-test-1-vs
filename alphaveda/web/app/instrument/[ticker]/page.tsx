import { notFound } from 'next/navigation'
import { getServerSupabase } from '@/lib/supabase'
import Lex, { LexOrRaw } from '@/components/Lex'
import { directionLexKey, lynchClassLexKey, outcomeLexKey } from '@/lib/lexicon'
import PriceSparkline from '@/components/PriceSparkline'
import { getLynchNarrative } from '@/lib/lynch-narratives'
import { OBSERVATION_THRESHOLD as INSTRUMENT_OBSERVATION_THRESHOLD } from '@/lib/calibration'

type Instrument = {
  id: number
  ticker: string
  name: string
  classification: string
  sector: string | null
}
type Price = { close: number; trade_date: string }
type Prediction = {
  id: number
  instrument_id: number
  direction: string
  emitted_at: string
  magnitude_target: number | null
  downside_target: number | null
}

// L1-D (2026-07-26, RF-J): the most recent RESOLVED prior signal for this
// instrument, joined to its outcome — used only to show a past, already-graded
// call ("we said X / it did Y"). Never used for the current open signal above
// (see A13 adaptation note below) — that would be forward guidance, which
// SEBI compliance flags as prohibited.
type ResolvedPriorSignal = {
  outcome_id: number
  resolved_at: string
  hit: boolean
  return_pct: number
  magnitude_hit: boolean | null
  outcome: string | null
  direction: string
  emitted_at: string
  target: number | null
}

function startOfUtcWeek(now: Date): string {
  const start = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()))
  const daysSinceMonday = (start.getUTCDay() + 6) % 7
  start.setUTCDate(start.getUTCDate() - daysSinceMonday)
  return start.toISOString()
}

function formatPrice(close: number): string {
  return close.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export const revalidate = 3600

export default async function InstrumentPage({ params }: { params: Promise<{ ticker: string }> }) {
  const { ticker: rawTicker } = await params
  const ticker = decodeURIComponent(rawTicker).toUpperCase()
  const sb = getServerSupabase()

  const instrumentRes = await sb
    .from('instruments')
    .select('id,ticker,name,classification,sector')
    .eq('ticker', ticker)
    .eq('is_active', true)
    .limit(1)
    .maybeSingle()

  const instrument = instrumentRes.data as Instrument | null
  if (!instrument) notFound()

  const weekStart = startOfUtcWeek(new Date())
  const [priceRes, historyRes, signalRes, outcomesRes, trackedRes, weeklySignalsRes, lastResolvedRes] = await Promise.all([
    sb.from('ohlcv')
      .select('close,trade_date')
      .eq('instrument_id', instrument.id)
      .eq('circuit_flag', false)
      .order('trade_date', { ascending: false })
      .limit(1),
    // Last 30 sessions for the sparkline — ascending so PriceSparkline can
    // read left-to-right without re-sorting.
    sb.from('ohlcv')
      .select('close,trade_date')
      .eq('instrument_id', instrument.id)
      .eq('circuit_flag', false)
      .order('trade_date', { ascending: false })
      .limit(30),
    sb.from('accuracy_predictions')
      .select('id,instrument_id,direction,emitted_at,magnitude_target,downside_target')
      .eq('instrument_id', instrument.id)
      .is('superseded_at', null)
      .order('emitted_at', { ascending: false })
      .limit(1),
    sb.from('accuracy_outcomes')
      .select('id,accuracy_predictions!inner(instrument_id)', { count: 'exact', head: true })
      .eq('accuracy_predictions.instrument_id', instrument.id),
    sb.from('instruments')
      .select('id', { count: 'exact' })
      .eq('is_active', true),
    sb.from('accuracy_predictions')
      .select('id,instrument_id,direction,emitted_at')
      .gte('emitted_at', weekStart)
      .is('superseded_at', null)
      .order('emitted_at', { ascending: false }),
    // Most recent RESOLVED signal for this instrument, for the "we said X /
    // it did Y" comparison — an already-graded past call, never the current
    // open signal's forward target.
    sb.from('accuracy_outcomes')
      .select('id,resolved_at,hit,return_pct,magnitude_hit,outcome,accuracy_predictions!inner(instrument_id,direction,emitted_at,magnitude_target,downside_target)')
      .eq('accuracy_predictions.instrument_id', instrument.id)
      .order('resolved_at', { ascending: false })
      .limit(1),
  ])

  const price = (priceRes.data?.[0] ?? null) as Price | null
  const history = [...((historyRes.data ?? []) as Price[])].reverse() // oldest first for the sparkline
  const signal = (signalRes.data?.[0] ?? null) as Prediction | null
  const resolvedCount = outcomesRes.count ?? 0
  const trackedCount = trackedRes.count ?? 0

  // Supabase's embedded-resource shape for a to-one !inner join can come back
  // as either an object or a single-element array depending on client
  // version — normalize defensively rather than assume one shape.
  const rawLastResolved = lastResolvedRes.data?.[0] as
    | (Record<string, unknown> & { accuracy_predictions: unknown })
    | undefined
  const rawPred = rawLastResolved
    ? (Array.isArray(rawLastResolved.accuracy_predictions)
        ? rawLastResolved.accuracy_predictions[0]
        : rawLastResolved.accuracy_predictions) as
        | { instrument_id: number; direction: string; emitted_at: string; magnitude_target: number | null; downside_target: number | null }
        | undefined
    : undefined
  const lastResolved: ResolvedPriorSignal | null =
    rawLastResolved && rawPred
      ? {
          outcome_id: rawLastResolved.id as number,
          resolved_at: rawLastResolved.resolved_at as string,
          hit: rawLastResolved.hit as boolean,
          return_pct: rawLastResolved.return_pct as number,
          magnitude_hit: (rawLastResolved.magnitude_hit as boolean | null) ?? null,
          outcome: (rawLastResolved.outcome as string | null) ?? null,
          direction: rawPred.direction,
          emitted_at: rawPred.emitted_at,
          target: rawPred.direction === 'BULL' ? rawPred.magnitude_target : rawPred.downside_target,
        }
      : null
  const weeklySignals = (weeklySignalsRes.data ?? []) as Prediction[]
  const latestWeeklyByInstrument = new Map<number, Prediction>()
  for (const prediction of weeklySignals) {
    if (!latestWeeklyByInstrument.has(prediction.instrument_id)) {
      latestWeeklyByInstrument.set(prediction.instrument_id, prediction)
    }
  }
  const positiveCount = [...latestWeeklyByInstrument.values()].filter(
    (prediction) => prediction.direction === 'BULL',
  ).length
  const classDescriptionKey = lynchClassLexKey(instrument.classification, 'description')
  const lynchNarrative = getLynchNarrative(instrument.ticker)

  return (
    <>
      <h1 className="av-heading">{instrument.ticker}</h1>
      <p className="av-subheading"><Lex k="instrument.title" /></p>
      {instrument.sector && (
        <p style={{ marginBottom: '1.5rem' }}>
          {instrument.name} <Lex k="instrument.company_operates_in" /> {instrument.sector}{' '}
          <Lex k="instrument.company_sector_suffix" />
        </p>
      )}

      {/* A13 adaptation (Fable round table 2026-07-10 principle, applied 2026-07-25
          — Varghese/sebi-compliance-reviewer finding): this page is a single-stock
          isolation surface, the exact condition the original A13 comment (see
          web/app/path/page.tsx) flags as risk — a raw BULL/BEAR verdict pill sitting
          in the same stat row as Target/Stop numbers reads as an implicit trade
          instruction even with analytical wording. Path's fix was to drop the raw
          pill entirely in favour of an analytical band framing; that specific
          replacement doesn't exist here (no Kelly/position context on this page),
          so the equivalent move is structural: the direction pill stays in the
          identity/classification grid (legitimate research data, same as /signals),
          and Target/Stop are visually decoupled into their own section below rather
          than sharing a row with the pill — so the page never presents
          "BULL + Target 5% + Stop 2%" as one flat, instruction-shaped unit. */}
      <div className="av-grid av-grid--4" style={{ marginBottom: '1.5rem' }}>
        <div className="av-card">
          <div className="av-stat__label"><Lex k="instrument.live_price" /></div>
          <div className="av-stat__value mono">
            {price ? formatPrice(price.close) : <Lex k="instrument.no_price" />}
          </div>
        </div>

        <div className="av-card">
          <div className="av-stat__label"><Lex k="instrument.current_signal" /></div>
          <div className="av-stat__value">
            {signal ? (
              <span className={`pill pill--${signal.direction === 'BULL' ? 'bull' : 'bear'}`}>
                <LexOrRaw k={directionLexKey(signal.direction)} fallback={signal.direction} />
              </span>
            ) : <Lex k="instrument.no_signal" />}
          </div>
        </div>

        <div className="av-card">
          <div className="av-stat__label"><Lex k="instrument.lynch_class" /></div>
          <div className="av-stat__value">
            <span className="pill">
              <LexOrRaw
                k={lynchClassLexKey(instrument.classification)}
                fallback={instrument.classification}
              />
            </span>
            {classDescriptionKey && (
              <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: '0.875rem', fontWeight: 400, marginLeft: '0.75rem' }}>
                <Lex k={classDescriptionKey} />
              </span>
            )}
          </div>
        </div>

        <div className="av-card">
          <div className="av-stat__label"><Lex k="instrument.accuracy" /></div>
          <div style={{ marginTop: '0.5rem' }}>
            {resolvedCount} of {INSTRUMENT_OBSERVATION_THRESHOLD} <Lex k="instrument.signals_graded" />
            {resolvedCount < INSTRUMENT_OBSERVATION_THRESHOLD && <> — <Lex k="instrument.not_enough_data" /></>}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Past signal accuracy does not guarantee future results.
          </div>
        </div>
      </div>

      {/* Target/Stop live in their own card, separate from the signal pill above —
          see A13 adaptation note. */}
      <div className="av-card" style={{ marginBottom: '1.5rem' }}>
        <div className="av-stat__label" style={{ marginBottom: '0.75rem' }}>Signal Risk Parameters</div>
        <div style={{ display: 'flex', gap: '2.5rem', flexWrap: 'wrap' }}>
          <div>
            <div className="av-stat__label">Target</div>
            <div className="av-stat__value mono">
              {signal?.magnitude_target != null ? `${(signal.magnitude_target * 100).toFixed(1)}%` : '—'}
            </div>
          </div>
          <div>
            <div className="av-stat__label">Stop</div>
            <div className="av-stat__value mono">
              {signal?.downside_target != null ? `${(signal.downside_target * 100).toFixed(1)}%` : '—'}
            </div>
          </div>
        </div>
        {/* SEBI compliance council finding (2026-08-01, Check 6): same inline
            risk-of-loss note added to /path — the risk applies wherever
            Target/Stop render, not just one page. */}
        <p style={{ marginTop: '0.75rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Target and Stop are hypothetical research levels, not price guarantees — actual price
          movement can differ and losses can exceed the stated Stop.
        </p>
      </div>

      {/* L1-D (2026-07-26, RF-J): comparison for the most recent RESOLVED past
          signal only — never for the open signal above (that would be forward
          guidance). Renders nothing if this instrument has no resolved prior
          signal yet, per council condition: check what data is actually
          available before assuming, don't fabricate a comparison. */}
      {lastResolved && (
        <div className="av-card" style={{ marginBottom: '1.5rem' }}>
          <div className="av-stat__label" style={{ marginBottom: '0.75rem' }}>
            Past call, graded — {lastResolved.resolved_at.slice(0, 10)}
          </div>
          <div style={{ display: 'flex', gap: '2.5rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div>
              <div className="av-stat__label">We said</div>
              <div className="av-stat__value mono" style={{ fontSize: '1.75rem' }}>
                {lastResolved.direction === 'BULL' ? '+' : '-'}
                {lastResolved.target != null ? `${(lastResolved.target * 100).toFixed(1)}%` : '—'}
              </div>
            </div>
            <div>
              <div className="av-stat__label">It did</div>
              <div
                className="av-stat__value mono"
                style={{ fontSize: '1.75rem', color: lastResolved.return_pct >= 0 ? 'var(--emerald)' : 'var(--terra)' }}
              >
                {/* RF-K fix (2026-07-26): return_pct is a raw fraction from
                    resolve_outcomes.py (e.g. 0.05 for a 5% move) — multiply by 100
                    to render as a percentage. Matches accuracy/page.tsx's corrected
                    rendering so both pages agree on the same field. */}
                {lastResolved.return_pct >= 0 ? '+' : ''}{(lastResolved.return_pct * 100).toFixed(2)}%
              </div>
            </div>
            <div>
              <div className="av-stat__label"><Lex k="ledger.direction_hit_label" /></div>
              <div className="av-stat__value" style={{ color: lastResolved.hit ? 'var(--emerald)' : 'var(--terra)' }}>
                {lastResolved.hit ? '✓' : '✗'}
              </div>
            </div>
            <div>
              <div className="av-stat__label"><Lex k="ledger.magnitude_hit_label" /></div>
              <div
                className="av-stat__value"
                style={{ color: lastResolved.magnitude_hit == null ? 'var(--text-muted)' : lastResolved.magnitude_hit ? 'var(--emerald)' : 'var(--terra)' }}
              >
                {lastResolved.magnitude_hit == null ? '—' : lastResolved.magnitude_hit ? '✓' : '✗'}
              </div>
            </div>
          </div>
          {lastResolved.outcome && (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
              <LexOrRaw k={outcomeLexKey(lastResolved.outcome)} fallback={lastResolved.outcome} />
            </div>
          )}
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            A single past result, shown for reference only — not a prediction of what happens next.
          </div>
        </div>
      )}

      <div className="av-card" style={{ marginBottom: '1.5rem' }}>
        <div className="av-stat__label">Price History (last {history.length} sessions)</div>
        <PriceSparkline rows={history} />
      </div>

      <div className="av-banner av-banner--blue">
        {positiveCount} of {trackedCount} <Lex k="instrument.aggregate_prefix" /> <Lex k="instrument.aggregate_suffix" />
      </div>

      <section className="av-card">
        <p style={{ marginBottom: '0.75rem' }}><strong><Lex k="instrument.self_check_intro" /></strong></p>
        <ol style={{ paddingLeft: '1.25rem', display: 'grid', gap: '0.5rem' }}>
          <li><Lex k="instrument.self_check.visibility" /></li>
          <li><Lex k="instrument.self_check.repeat" /></li>
          <li><Lex k="instrument.self_check.demand" /></li>
        </ol>
      </section>

      {lynchNarrative && (
        <section className="av-card" style={{ marginTop: '1.5rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Understand this company</h2>

          <h3 style={{ marginBottom: '0.5rem' }}>What the company does</h3>
          <p style={{ marginBottom: '1rem' }}>{lynchNarrative.companyDescription}</p>

          <h3 style={{ marginBottom: '0.5rem' }}>Why it fits this company class</h3>
          <p style={{ marginBottom: '1rem' }}>{lynchNarrative.lynchClassStory}</p>

          <h3 style={{ marginBottom: '0.5rem' }}>Check your understanding</h3>
          <ol style={{ paddingLeft: '1.25rem', display: 'grid', gap: '0.5rem', marginBottom: '1rem' }}>
            {lynchNarrative.selfVerification.map((question) => (
              <li key={question}>{question}</li>
            ))}
          </ol>

          <aside className="av-banner av-banner--blue">
            <strong>How future news will be chosen:</strong>{' '}
            {lynchNarrative.newsFilter}
          </aside>
        </section>
      )}
    </>
  )
}

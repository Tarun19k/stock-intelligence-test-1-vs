import { notFound } from 'next/navigation'
import { getServerSupabase } from '@/lib/supabase'
import Lex, { LexOrRaw } from '@/components/Lex'
import { directionLexKey, lynchClassLexKey } from '@/lib/lexicon'

const INSTRUMENT_OBSERVATION_THRESHOLD = 20

type Instrument = {
  id: number
  ticker: string
  name: string
  classification: string
  sector: string | null
}
type Price = { close: number; trade_date: string }
type Prediction = { id: number; instrument_id: number; direction: string; emitted_at: string }

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
  const [priceRes, signalRes, outcomesRes, trackedRes, weeklySignalsRes] = await Promise.all([
    sb.from('ohlcv')
      .select('close,trade_date')
      .eq('instrument_id', instrument.id)
      .eq('circuit_flag', false)
      .order('trade_date', { ascending: false })
      .limit(1),
    sb.from('accuracy_predictions')
      .select('id,instrument_id,direction,emitted_at')
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
  ])

  const price = (priceRes.data?.[0] ?? null) as Price | null
  const signal = (signalRes.data?.[0] ?? null) as Prediction | null
  const resolvedCount = outcomesRes.count ?? 0
  const trackedCount = trackedRes.count ?? 0
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
        </div>
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
    </>
  )
}

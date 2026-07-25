import Link from 'next/link'
import { getServerSupabase } from '@/lib/supabase'

type Instrument = { id: number; ticker: string }
type OHLCVRow = { instrument_id: number; trade_date: string; close: number }
type Move = { ticker: string; pct: number }

function fmtPct(pct: number): string {
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}

// Real day-over-day % move — deliberately NOT the same as engine.py's
// volatility-normalized signal confidence (RF-I fix). This is a raw price
// move for a market-overview strip, not a trading signal; conflating the
// two would misrepresent what each number means.
export default async function GainersLosersStrip() {
  const sb = getServerSupabase()

  const [instRes, ohlcvRes] = await Promise.all([
    sb.from('instruments').select('id,ticker').eq('is_active', true),
    // Fetch enough non-circuit rows for 2 most-recent observations per active
    // instrument without letting halted, frozen prices shrink the candidate pool.
    sb.from('ohlcv')
      .select('instrument_id,trade_date,close')
      .eq('circuit_flag', false)
      .order('trade_date', { ascending: false })
      .limit(60),
  ])

  const instruments: Instrument[] = instRes.data ?? []
  const tickerById = new Map(instruments.map((i) => [i.id, i.ticker]))

  const rowsByInst = new Map<number, OHLCVRow[]>()
  for (const row of (ohlcvRes.data ?? []) as OHLCVRow[]) {
    const list = rowsByInst.get(row.instrument_id) ?? []
    list.push(row)
    rowsByInst.set(row.instrument_id, list)
  }

  const moves: Move[] = []
  for (const [instId, rows] of rowsByInst) {
    const ticker = tickerById.get(instId)
    if (!ticker || rows.length < 2) continue
    const [latest, prior] = rows // already ordered desc by trade_date
    if (!prior.close) continue
    const pct = ((latest.close - prior.close) / prior.close) * 100
    moves.push({ ticker, pct })
  }

  moves.sort((a, b) => b.pct - a.pct)
  const gainers = moves.filter((m) => m.pct > 0).slice(0, 5)
  const losers = moves.filter((m) => m.pct < 0).slice(-5).reverse()

  if (moves.length === 0) {
    return (
      <div className="av-card">
        <p style={{ color: 'var(--text-muted)' }}>No day-over-day price data yet.</p>
      </div>
    )
  }

  return (
    <div className="av-grid av-grid--2">
      <div className="av-card">
        <div className="av-stat__label">Top Gainers</div>
        <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Day-over-day price moves — not a ranking of investment quality
        </div>
        <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0 0' }}>
          {gainers.map((m) => (
            <li key={m.ticker} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0' }}>
              <Link href={`/instrument/${m.ticker}`} className="mono">{m.ticker}</Link>
              <span className="mono" style={{ color: 'var(--positive, #1a7a3a)' }}>{fmtPct(m.pct)}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="av-card">
        <div className="av-stat__label">Top Losers</div>
        <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Day-over-day price moves — not a ranking of investment quality
        </div>
        <ul style={{ listStyle: 'none', padding: 0, margin: '0.5rem 0 0' }}>
          {losers.map((m) => (
            <li key={m.ticker} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0' }}>
              <Link href={`/instrument/${m.ticker}`} className="mono">{m.ticker}</Link>
              <span className="mono" style={{ color: 'var(--negative, #b3261e)' }}>{fmtPct(m.pct)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

import { getServerSupabase } from '@/lib/supabase'
import { LexOrRaw } from '@/components/Lex'
import { lynchClassLexKey } from '@/lib/lexicon'

type Instrument = { id: number; ticker: string; classification: string }
type OHLCVRow = {
  instrument_id: number
  trade_date: string
  open: number; high: number; low: number; close: number
  volume: number
  circuit_flag: boolean
}
type IngestStatus = { last_run: string; rows_written: number | null; status: string }

function daysBetween(dateStr: string, now: Date): number {
  return Math.floor((now.getTime() - new Date(dateStr).getTime()) / 86_400_000)
}

function fmt(n: number) {
  return '₹' + n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export const revalidate = 3600

export default async function MarketDataPage() {
  const sb = getServerSupabase()
  const now = new Date()

  const [instRes, ohlcvRes, statusRes] = await Promise.all([
    sb.from('instruments').select('id,ticker,classification').eq('is_active', true).order('ticker'),
    sb.from('ohlcv').select('instrument_id,trade_date,open,high,low,close,volume,circuit_flag').order('trade_date', { ascending: false }).limit(500),
    sb.from('ingest_status').select('last_run,rows_written,status').eq('source', 'bhavcopy_nse').order('last_run', { ascending: false }).limit(1),
  ])

  const instruments: Instrument[] = instRes.data ?? []
  const allOhlcv: OHLCVRow[] = ohlcvRes.data ?? []
  const ingestRow: IngestStatus | null = statusRes.data?.[0] ?? null

  const latestByInst = new Map<number, OHLCVRow>()
  for (const row of allOhlcv) {
    if (!latestByInst.has(row.instrument_id)) latestByInst.set(row.instrument_id, row)
  }

  const staleDays = ingestRow ? daysBetween(ingestRow.last_run, now) : null

  return (
    <>
      <h1 className="av-heading">Market Data</h1>
      <p className="av-subheading">
        Latest EOD prices from NSE Bhavcopy — {instruments.length} instruments tracked
      </p>

      {staleDays !== null && staleDays >= 1 && (
        <div className="av-banner av-banner--amber">
          ⚠ Data last updated {staleDays} day{staleDays !== 1 ? 's' : ''} ago ({ingestRow!.last_run}).
          Next ingest runs Mon–Fri after market close.
        </div>
      )}
      {!ingestRow && (
        <div className="av-banner av-banner--red">
          We&apos;re still setting up. Price data will appear here soon — check back shortly.
        </div>
      )}

      <div className="av-card" style={{ overflowX: 'auto' }}>
        {instruments.length === 0 ? (
          <div className="av-empty">
            <p className="av-empty__title">No data yet</p>
            <p>We&apos;re still setting up. Check back soon.</p>
          </div>
        ) : (
          <table className="av-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Class</th>
                <th>Date</th>
                <th style={{ textAlign: 'right' }}>Open</th>
                <th style={{ textAlign: 'right' }}>High</th>
                <th style={{ textAlign: 'right' }}>Low</th>
                <th style={{ textAlign: 'right' }}>Close</th>
                <th style={{ textAlign: 'right' }}>Volume</th>
                <th>Flag</th>
              </tr>
            </thead>
            <tbody>
              {instruments.map((inst) => {
                const row = latestByInst.get(inst.id)
                if (!row) {
                  return (
                    <tr key={inst.id}>
                      <td className="mono">{inst.ticker}</td>
                      <td><LexOrRaw k={lynchClassLexKey(inst.classification)} fallback={inst.classification} /></td>
                      <td colSpan={7} style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                        No data yet
                      </td>
                    </tr>
                  )
                }
                return (
                  <tr key={inst.id}>
                    <td><strong className="mono">{inst.ticker}</strong></td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <LexOrRaw k={lynchClassLexKey(inst.classification)} fallback={inst.classification} />
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem' }}>{row.trade_date}</td>
                    <td className="mono" style={{ textAlign: 'right' }}>{fmt(row.open)}</td>
                    <td className="mono" style={{ textAlign: 'right' }}>{fmt(row.high)}</td>
                    <td className="mono" style={{ textAlign: 'right' }}>{fmt(row.low)}</td>
                    <td className="mono" style={{ textAlign: 'right' }}>{fmt(row.close)}</td>
                    <td className="mono" style={{ textAlign: 'right' }}>
                      {row.volume.toLocaleString('en-IN')}
                    </td>
                    <td>
                      {row.circuit_flag
                        ? <span className="pill pill--circuit">CIRCUIT</span>
                        : '—'}
                    </td>
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

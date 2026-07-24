type Point = { trade_date: string; close: number }

// Zero-dependency inline SVG sparkline — deliberately not a charting library
// (recharts etc.) for a demo-scoped feature: avoids a new npm dependency,
// a new bundle-size cost, and a new supply-chain surface for ~30 lines of
// real value. Revisit if a richer interactive chart (zoom, tooltip, volume
// overlay) is actually needed — this is intentionally the minimal version.
export default function PriceSparkline({ rows }: { rows: Point[] }) {
  if (rows.length < 2) {
    return <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Not enough history for a chart yet.</div>
  }

  // rows must be chronological (oldest first) for the line to read left-to-right.
  const closes = rows.map((r) => r.close)
  const min = Math.min(...closes)
  const max = Math.max(...closes)
  const range = max - min || 1 // avoid divide-by-zero on a flat line

  const width = 320
  const height = 80
  const padding = 4

  const points = closes.map((close, i) => {
    const x = padding + (i / (closes.length - 1)) * (width - padding * 2)
    const y = height - padding - ((close - min) / range) * (height - padding * 2)
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })

  const trendUp = closes[closes.length - 1] >= closes[0]
  const strokeColor = trendUp ? 'var(--positive, #1a7a3a)' : 'var(--negative, #b3261e)'

  return (
    <div>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img"
           aria-label={`Price trend, ${rows[0].trade_date} to ${rows[rows.length - 1].trade_date}`}>
        <polyline points={points.join(' ')} fill="none" stroke={strokeColor} strokeWidth={1.5} />
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
        <span>{rows[0].trade_date}</span>
        <span>{rows[rows.length - 1].trade_date}</span>
      </div>
    </div>
  )
}

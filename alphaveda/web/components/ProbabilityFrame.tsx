'use client'
// A10/A14 — renders a confidence/hit-rate percentage in the current
// language_mode. Simple mode uses the lexicon's natural-frequency framing
// (§5 rule 2: "never a bare verbal label"); Pro mode keeps the raw
// percentage.
//
// A14 (F3, Fable round table 2026-07-10): every place a probability is
// shown also surfaces its complement close by, small and not alarmist
// ("...which also means wrong about 1 in 3 times") — an anchoring
// counterweight so a "right ~2 in 3 times" framing doesn't read as more
// certain than it is. Matches the lexicon's honesty-first tone.

import { naturalFrequency } from '@/lib/lexicon'
import { useLanguageMode } from '@/lib/language-mode'

export default function ProbabilityFrame({ pct }: { pct: number }) {
  const { mode } = useLanguageMode()
  // Round to 1 decimal for display — pct is frequently a raw division result
  // (e.g. 14/30*100 = 46.666666666666664) and was rendering unrounded.
  const display = pct.toFixed(1)

  if (mode === 'pro') {
    return <span className="mono">{display}%</span>
  }

  const { right, wrong } = naturalFrequency(pct)
  return (
    <span>
      <span className="mono">{right} · {display}%</span>
      {wrong && (
        <span style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          (which also means {wrong})
        </span>
      )}
    </span>
  )
}

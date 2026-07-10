'use client'
// A10 — renders a confidence/hit-rate percentage in the current language_mode.
// Simple mode uses the lexicon's natural-frequency framing (§5 rule 2: "never
// a bare verbal label"); Pro mode keeps the raw percentage. The anchoring
// complement ("...which also means wrong about 1 in 3 times") is added in
// A14's commit, on top of this same component.

import { naturalFrequency } from '@/lib/lexicon'
import { useLanguageMode } from '@/lib/language-mode'

export default function ProbabilityFrame({ pct }: { pct: number }) {
  const { mode } = useLanguageMode()

  if (mode === 'pro') {
    return <span className="mono">{pct}%</span>
  }

  const { right } = naturalFrequency(pct)
  return <span className="mono">{right} · {pct}%</span>
}

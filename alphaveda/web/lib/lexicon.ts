// lib/lexicon.ts
// Key-based string architecture generated from the LOCKED copy source-of-truth:
//   alphaveda/tech_stack/files (4)/PLAIN_LANGUAGE_LEXICON.md (v1.0)
// Do NOT hand-edit strings here without updating the lexicon .md first (lexicon §5 rule 7:
// "New strings enter through this table ... before they enter code").
// `hi` (Hindi) is intentionally not modelled yet — the lexicon reserves it as a future column,
// not a rewrite (§2). Adding it later is additive to LexEntry, not a restructuring.
//
// Direction-agnostic by construction: every value here is plain text/data, no color, no
// className, no layout. Presentation components (Lex.tsx, GlossaryModal.tsx) apply currentColor
// / existing CSS variables only — nothing here assumes D1, D2, or D3.

export type LanguageMode = 'simple' | 'pro'

export type GlossaryKey =
  | 'no_call'
  | 'probability'
  | 'lynch_class'
  | 'regime'
  | 'ledger_demoted'
  | 'ledger_cold'
  | 'ledger_ece'
  | 'kelly_band'

export type LexEntry = {
  pro: string
  simple: string
  /** If set, Simple-mode rendering offers a tap-to-learn affordance resolving to this glossary entry. */
  learn?: GlossaryKey
}

export type LexKey =
  | 'signal.up'
  | 'signal.down'
  | 'signal.none'
  | 'signal.class.stalwart'
  | 'signal.class.cyclical'
  | 'signal.class.fast_grower'
  | 'signal.class.slow_grower'
  | 'signal.class.turnaround'
  | 'signal.class.asset_play'
  | 'signal.class.description.slow_grower'
  | 'signal.class.description.stalwart'
  | 'signal.class.description.fast_grower'
  | 'signal.class.description.cyclical'
  | 'signal.class.description.turnaround'
  | 'signal.class.description.asset_play'
  | 'signal.regime.bull'
  | 'signal.regime.bear'
  | 'signal.regime.sideways'
  | 'signal.regime.highvol'
  | 'instrument.title'
  | 'instrument.live_price'
  | 'instrument.current_signal'
  | 'instrument.lynch_class'
  | 'instrument.accuracy'
  | 'instrument.no_price'
  | 'instrument.no_signal'
  | 'instrument.not_enough_data'
  | 'instrument.signals_graded'
  | 'instrument.aggregate_prefix'
  | 'instrument.aggregate_suffix'
  | 'instrument.company_operates_in'
  | 'instrument.company_sector_suffix'
  | 'instrument.self_check_intro'
  | 'instrument.self_check.visibility'
  | 'instrument.self_check.repeat'
  | 'instrument.self_check.demand'
  | 'ledger.title'
  | 'ledger.pass'
  | 'ledger.demoted'
  | 'ledger.cold'
  | 'ledger.hit_label'
  | 'ledger.cold_banner'
  | 'port.title'
  | 'port.band'
  | 'port.above'
  | 'port.within'
  | 'port.below'
  | 'port.judgment'
  | 'port.subtitle'
  | 'port.method'

// ---------------------------------------------------------------------------
// §1 Signal surface, §2 Scorecard surface, §3 Portfolio surface (labels only —
// dynamic values like p 0.68/n=142, ₹ amounts, dates are composed by callers,
// not baked into this table, since those vary per-row).
// ---------------------------------------------------------------------------
export const LEXICON: Record<LexKey, LexEntry> = {
  'signal.up': { pro: 'LEANS UP', simple: 'LOOKS POSITIVE' },
  'signal.down': { pro: 'LEANS DOWN', simple: 'LOOKS NEGATIVE' },
  'signal.none': {
    pro: 'NO CALL',
    simple: 'NO OPINION TODAY',
    learn: 'no_call',
  },
  'signal.class.stalwart': { pro: 'stalwart', simple: 'steady large company', learn: 'lynch_class' },
  'signal.class.cyclical': { pro: 'cyclical', simple: 'it moves with the economy', learn: 'lynch_class' },
  'signal.class.fast_grower': { pro: 'fast_grower', simple: 'fast-growing company', learn: 'lynch_class' },
  'signal.class.slow_grower': { pro: 'slow_grower', simple: 'steady, low-drama company', learn: 'lynch_class' },
  'signal.class.turnaround': { pro: 'turnaround', simple: 'recovering from trouble', learn: 'lynch_class' },
  'signal.class.asset_play': { pro: 'asset_play', simple: 'worth more in assets than price says', learn: 'lynch_class' },
  'signal.class.description.slow_grower': {
    pro: 'Steady, low-drama. Grows like the economy.',
    simple: 'Steady, low-drama. Grows like the economy.',
  },
  'signal.class.description.stalwart': {
    pro: "Big and dependable. Won't 10x, won't collapse either.",
    simple: "Big and dependable. Won't 10x, won't collapse either.",
  },
  'signal.class.description.fast_grower': {
    pro: 'Small and expanding fast. Higher upside, higher chance it stumbles.',
    simple: 'Small and expanding fast. Higher upside, higher chance it stumbles.',
  },
  'signal.class.description.cyclical': {
    pro: "Rises and falls with the economy - buying at the 'boring' point matters more than the story.",
    simple: "Rises and falls with the economy - buying at the 'boring' point matters more than the story.",
  },
  'signal.class.description.turnaround': {
    pro: 'Was in trouble, trying to recover. Watch for proof, not promises.',
    simple: 'Was in trouble, trying to recover. Watch for proof, not promises.',
  },
  'signal.class.description.asset_play': {
    pro: 'Worth more in what it owns than what the stock price says.',
    simple: 'Worth more in what it owns than what the stock price says.',
  },
  'signal.regime.bull': { pro: 'bull regime', simple: 'market rising', learn: 'regime' },
  'signal.regime.bear': { pro: 'bear regime', simple: 'market falling', learn: 'regime' },
  'signal.regime.sideways': { pro: 'sideways', simple: 'market drifting flat', learn: 'regime' },
  'signal.regime.highvol': { pro: 'highvol', simple: 'market unusually jumpy', learn: 'regime' },
  'instrument.title': { pro: 'Instrument detail', simple: 'Stock detail' },
  'instrument.live_price': { pro: 'Latest close', simple: 'Latest price' },
  'instrument.current_signal': { pro: 'Current signal', simple: 'Current signal' },
  'instrument.lynch_class': { pro: 'Lynch class', simple: 'Company type', learn: 'lynch_class' },
  'instrument.accuracy': { pro: 'Instrument accuracy', simple: 'Results for this stock' },
  'instrument.no_price': { pro: 'No price available', simple: 'No price available yet' },
  'instrument.no_signal': { pro: 'No signal available', simple: 'No signal available yet' },
  'instrument.not_enough_data': { pro: 'not enough data yet', simple: 'not enough data yet' },
  'instrument.signals_graded': { pro: 'signals graded', simple: 'signals graded' },
  'instrument.aggregate_prefix': { pro: 'tracked stocks showing a positive signal', simple: 'tracked stocks looking positive' },
  'instrument.aggregate_suffix': { pro: 'this week', simple: 'this week' },
  'instrument.company_operates_in': { pro: 'operates in the', simple: 'operates in the' },
  'instrument.company_sector_suffix': { pro: 'sector.', simple: 'sector.' },
  'instrument.self_check_intro': {
    pro: "This matters as much as the signal above - it's your own judgment, not a recommendation.",
    simple: "This matters as much as the signal above - it's your own judgment, not a recommendation.",
  },
  'instrument.self_check.visibility': {
    pro: "Do you see this company's products/stores/ads around you - and is that more or less than a year ago?",
    simple: "Do you see this company's products/stores/ads around you - and is that more or less than a year ago?",
  },
  'instrument.self_check.repeat': {
    pro: 'Would you (or someone you know) buy from them again?',
    simple: 'Would you (or someone you know) buy from them again?',
  },
  'instrument.self_check.demand': {
    pro: 'Is what they sell something people need more of over time, or is it fading?',
    simple: 'Is what they sell something people need more of over time, or is it fading?',
  },

  'ledger.title': { pro: 'Accuracy Ledger', simple: 'Our scorecard' },
  'ledger.pass': { pro: 'PASS', simple: 'GOOD' },
  'ledger.demoted': { pro: 'DEMOTED', simple: 'UNDER REVIEW', learn: 'ledger_demoted' },
  'ledger.cold': { pro: 'COLD', simple: 'TOO EARLY', learn: 'ledger_cold' },
  'ledger.hit_label': { pro: 'Hit Rate', simple: 'How often right' },
  // Locked source (lexicon §2, ledger.cold learn card): "New types get graded after 30 results."
  // Lead-in phrase — composed by the caller with a trailing "X of Y graded so far" clause.
  'ledger.cold_banner': {
    pro: 'COLD START',
    simple: 'Just getting started',
    learn: 'ledger_cold',
  },

  'port.title': { pro: 'Kelly view', simple: 'Your position sizes' },
  'port.subtitle': { pro: 'Kelly-based position sizing — research purposes only', simple: 'How much of your money each idea might fit — research only' },
  'port.method': { pro: 'Quarter Kelly', simple: 'a cautious slice of the full formula', learn: 'kelly_band' },
  'port.band': { pro: 'Kelly band', simple: 'healthy range', learn: 'kelly_band' },
  'port.above': { pro: 'ABOVE', simple: 'LARGER than range' },
  'port.within': { pro: 'WITHIN', simple: 'HEALTHY' },
  'port.below': { pro: 'BELOW', simple: 'SMALLER than range' },
  'port.judgment': { pro: 'observations for your judgment', simple: 'You decide what to do.' },
}

export function lex(key: LexKey, mode: LanguageMode): string {
  return LEXICON[key][mode]
}

// ---------------------------------------------------------------------------
// Raw-value -> LexKey mappers for existing DB enum strings. Unknown/unmapped
// raw values fall back to `null` so callers can render the raw value as-is
// (fail-open on copy, never fail-closed on data) rather than crash on a
// future enum member the lexicon hasn't caught up to yet.
// ---------------------------------------------------------------------------
export function directionLexKey(direction: string): LexKey | null {
  if (direction === 'BULL') return 'signal.up'
  if (direction === 'BEAR') return 'signal.down'
  return null
}

export function lynchClassLexKey(
  lynchClass: string | null | undefined,
  kind: 'label' | 'description' = 'label',
): LexKey | null {
  if (kind === 'description') {
    switch (lynchClass) {
      case 'slow_grower': return 'signal.class.description.slow_grower'
      case 'stalwart': return 'signal.class.description.stalwart'
      case 'fast_grower': return 'signal.class.description.fast_grower'
      case 'cyclical': return 'signal.class.description.cyclical'
      case 'turnaround': return 'signal.class.description.turnaround'
      case 'asset_play': return 'signal.class.description.asset_play'
      default: return null
    }
  }

  switch (lynchClass) {
    case 'stalwart': return 'signal.class.stalwart'
    case 'cyclical': return 'signal.class.cyclical'
    case 'fast_grower': return 'signal.class.fast_grower'
    case 'slow_grower': return 'signal.class.slow_grower'
    case 'turnaround': return 'signal.class.turnaround'
    case 'asset_play': return 'signal.class.asset_play'
    default: return null
  }
}

export function regimeLexKey(regime: string | null | undefined): LexKey | null {
  switch (regime) {
    case 'bull': return 'signal.regime.bull'
    case 'bear': return 'signal.regime.bear'
    case 'sideways': return 'signal.regime.sideways'
    case 'highvol': return 'signal.regime.highvol'
    default: return null
  }
}

// ---------------------------------------------------------------------------
// Glossary (lexicon §1-3 tap-to-learn column). Static for MVP — lexicon §6.4
// notes these "seed a glossary table" later; a DB table is not required now.
// ---------------------------------------------------------------------------
export type GlossaryEntry = { headline: string; body: string; term: string }

export const GLOSSARY: Record<GlossaryKey, GlossaryEntry> = {
  no_call: {
    headline: 'Why we sometimes say nothing',
    body: "We are not sure here. So we say nothing. A tool that always has an opinion is a tool you can't trust.",
    term: 'Professional term: arbitration threshold / no emission',
  },
  probability: {
    headline: "How often we've been right",
    body: 'In situations just like this, our past calls were correct about this often. It comes from grading every past call in public.',
    term: 'Professional term: calibrated probability',
  },
  lynch_class: {
    headline: 'What kind of company this is',
    body: 'We group companies by how they tend to behave, so the same signal can be read differently for different kinds of businesses.',
    term: 'Professional term: Lynch classification',
  },
  regime: {
    headline: "Market rising / falling / flat / jumpy",
    body: "We describe the market's current behavior, because the same signal is more or less reliable depending on it.",
    term: 'Professional term: market regime',
  },
  ledger_demoted: {
    headline: 'Under review',
    body: 'This kind of call has been less accurate lately — right only 52 of 100. We flag it and treat it as information only, until it earns trust back.',
    term: 'Professional term: demoted signal class',
  },
  ledger_cold: {
    headline: 'Too early to say',
    body: 'New types get graded after 30 results.',
    term: 'Professional term: cold segment / observation threshold',
  },
  ledger_ece: {
    headline: 'Confidence, checked against reality',
    body: 'When we say 68%, situations like it should come true about 68 times in 100. We measure that match constantly.',
    term: 'Professional term: calibration (ECE)',
  },
  kelly_band: {
    headline: 'Healthy size range',
    body: 'For each holding we compute a sensible size, given how often calls like this are right and how much it could fall.',
    term: 'Professional term: Kelly sizing band',
  },
}

// ---------------------------------------------------------------------------
// §4 Compliance strings — ALWAYS present, never toggled by language_mode.
// This module does not replace SebiDisclaimer.tsx (which remains the pinned
// footer, sourced from alphaveda/constants.py SEBI_DISCLAIMER via
// lib/sebi-disclaimer.generated.ts per NG-4 — the Vercel SEBI_DISCLAIMER env
// var was deleted 2026-07-17 as part of RF-D closure). SEBI_LEGAL below is
// kept word-for-word identical to constants.py's canonical text. Exported
// here only so the language test suite (A12) can assert both plain and legal
// framing exist verbatim in the lexicon.
// ---------------------------------------------------------------------------
export const SEBI_PLAIN =
  'We share research and its track record. We never tell anyone what to do with their money.'
export const SEBI_LEGAL =
  'AlphaVeda provides research and analysis only. This is NOT investment advice. ' +
  'Consult a SEBI-registered investment advisor before making any investment decision. ' +
  'Past signal accuracy does not guarantee future returns.'

// ---------------------------------------------------------------------------
// A14 — anchoring counter. Converts a 0-100 confidence/hit-rate percentage into
// a natural-frequency pair ("right ~2 in 3 times" + its complement), matching
// the lexicon's frequency-framing rule (§5 rule 2) and honesty-first tone.
// Judgment call: the lexicon table only hand-picks two exact frequencies
// (0.68 -> 2 in 3, 0.61 -> 3 in 5). Real emitted confidence values (18-50%,
// per the 2026-07-10 live verification) don't land on those exact points, so
// this generalises the same style to any percentage by finding the closest
// simple fraction (denominator 2-10). Flagged for Tarun review below.
// ---------------------------------------------------------------------------
export function naturalFrequency(pct: number): { right: string; wrong: string; pct: number } {
  const p = Math.max(0, Math.min(100, pct)) / 100
  let bestNum = Math.round(p * 10)
  let bestDen = 10
  let bestErr = Math.abs(bestNum / bestDen - p)
  for (let den = 2; den <= 10; den++) {
    const num = Math.round(p * den)
    const err = Math.abs(num / den - p)
    if (err < bestErr - 1e-9) {
      bestErr = err
      bestNum = num
      bestDen = den
    }
  }
  // Reduce fraction for readability (e.g. 4/10 -> 2/5)
  const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b))
  const divisor = gcd(bestNum, bestDen) || 1
  const num = bestNum / divisor
  const den = bestDen / divisor
  const wrongNum = den - num
  return {
    right: num <= 0 ? 'rarely right here' : `right ~${num} in ${den} times`,
    wrong: wrongNum <= 0 ? '' : `wrong about ${wrongNum} in ${den} times`,
    pct: Math.round(pct),
  }
}

import { test, expect, type Page } from '@playwright/test'
import { GLOSSARY, LEXICON, SEBI_PLAIN, lynchClassLexKey } from '../lib/lexicon'
import { fleschKincaidGrade, stripProperNouns } from './helpers/flesch-kincaid'

// A12 — language test suite, ported into Playwright/CI per
// `alphaveda/tech_stack/files (4)/CLAUDE_CODE_ADDENDUM.md` R11 §6(c):
// "the language test suite (jargon scan, FK ≤ 7 brand-stripped, dual SEBI in
// both modes, learn-key resolution) added to the R4/Playwright checks."
//
// Source of the ported checks: `alphaveda/tech_stack/files (4)/design_evals_v2.py`
// (design catalog v2 eval suite, L1-L6). That script scans a static mock HTML
// file; this spec scans the *live* Next.js app across the 4 real routes, so
// checks that scanned "mock_simple" text there scan `page.locator('body').innerText()`
// here — innerText (not textContent) is used deliberately to exclude the
// Next.js `__NEXT_DATA__` script payload, which serializes raw DB field names
// (e.g. "regime", "lynch_class") that would otherwise false-positive the scan.

const ROUTES = ['/', '/signals', '/path', '/accuracy']

async function gotoWithMode(page: Page, route: string, mode: 'simple' | 'pro') {
  await page.addInitScript((m) => {
    window.localStorage.setItem('av_language_mode', m)
  }, mode)
  // language_mode is appended as an explicit query param per the A12 brief
  // ("test against all 4 routes with language_mode=simple explicitly"); the
  // app itself reads mode from localStorage only (lib/language-mode.tsx has
  // no URL-param reader), so the localStorage seed above is what actually
  // drives the mode — the query param documents test intent on top of that.
  const sep = route.includes('?') ? '&' : '?'
  await page.goto(`${route}${sep}language_mode=${mode}`)
  // Confirm hydration landed on the requested mode before asserting anything
  // (LanguageModeProvider always SSRs 'simple' first, then reads localStorage
  // post-mount — see lib/language-mode.tsx).
  const toggleLabel = mode === 'pro' ? 'Pro mode' : 'Simple mode'
  await expect(page.getByRole('button', { name: toggleLabel })).toBeVisible()
}

// ---------------------------------------------------------------------------
// Check 1 — L1: jargon scan. Banned technical tokens must not leak into
// Simple-mode rendered output. List ported verbatim from design_evals_v2.py
// line 16-17.
// ---------------------------------------------------------------------------
const JARGON = [
  'ECE', 'margin', 'Kelly', 'regime', 'calibrat', 'stalwart', 'cyclical ·',
  'fast_grower', 'p 0.', 'n=', 'E1', 'E2', 'bps', 'demoted', 'DEMOTED',
  'NO CALL', 'COLD', 'hit rate', 'ledger',
]

// Word-boundary match, not plain substring — a naive `.includes()` scan false-
// positives on e.g. "ECE" inside "REC[ent]" (r-e-C-E-n-t contains the literal
// substring "ece"). `\b` doesn't work before/after non-word chars like the
// space in "n=" or period in "p 0.", so anchor on whichever side is a real
// word character and leave the punctuated side unanchored.
function jargonRegex(token: string): RegExp {
  const escaped = token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const startsWithWord = /^\w/.test(token)
  const endsWithWord = /\w$/.test(token)
  const left = startsWithWord ? '\\b' : ''
  const right = endsWithWord ? '\\b' : ''
  return new RegExp(`${left}${escaped}${right}`, 'i')
}

for (const route of ROUTES) {
  test(`L1 jargon scan — no banned tokens in Simple mode on ${route}`, async ({ page }) => {
    await gotoWithMode(page, route, 'simple')
    const bodyText = await page.locator('body').innerText()
    const hits = JARGON.filter((j) => jargonRegex(j).test(bodyText))
    expect(hits, `jargon leaked into Simple mode on ${route}: ${JSON.stringify(hits)}`).toEqual([])
  })
}

// ---------------------------------------------------------------------------
// Check 2 — L2: Flesch-Kincaid grade <= 7 on Simple-mode copy, brand names
// excluded. design_evals_v2.py runs this against the static mock HTML's
// Simple-visible text; this codebase has no equivalent static mock, so the
// faithful analogue is the actual Simple-mode copy source: every LEXICON
// `.simple` string plus every GLOSSARY entry (headline + body) — this is the
// full universe of hand-authored plain-language copy A10/A11 shipped. FK
// algorithm and PROPER-noun exclusion list ported 1:1 (see helpers/flesch-kincaid.ts).
// ---------------------------------------------------------------------------
test('L2 Flesch-Kincaid grade of Simple copy <= 7 (brand names excluded)', () => {
  const lexiconSimpleStrings = Object.values(LEXICON).map((e) => e.simple)
  const glossaryStrings = Object.values(GLOSSARY).flatMap((g) => [g.headline, g.body])
  const complianceStrings = [SEBI_PLAIN]
  const fkInputRaw = [...lexiconSimpleStrings, ...glossaryStrings, ...complianceStrings].join('. ')
  const fkInput = stripProperNouns(fkInputRaw)
  const grade = fleschKincaidGrade(fkInput)
  expect(grade, `Simple copy grade ${grade.toFixed(1)} > 7`).toBeLessThanOrEqual(7.0)
})

test('L2 helper unit check — fleschKincaidGrade is exposed and behaves monotonically', () => {
  const simple = fleschKincaidGrade('The cat sat. It was fun.')
  const complex_ = fleschKincaidGrade(
    'The multifactorial calibration methodology necessitates probabilistic recalibration of heterogeneous portfolios.'
  )
  expect(simple).toBeLessThan(complex_)
})

// ---------------------------------------------------------------------------
// Check 3 — L6: dual SEBI disclaimer (plain-language line + legal line) must
// be present in BOTH language modes on every money surface. Ported from
// design_evals_v2.py lines 54-56 (there: count >= 12 occurrences across the
// mock; here: presence on all 4 real routes, in both modes explicitly).
//
// NOTE: SEBI_LEGAL is asserted against the *shipped* disclaimer text
// (SebiDisclaimer.tsx / sebi-disclaimer.generated.ts). As of RF-D closure
// (2026-07-17) lexicon.ts's SEBI_LEGAL is word-for-word identical to the
// shipped text — both trace to the same canonical source, constants.py.
// The substance-only check below ("NOT investment advice") is kept as a
// lighter-weight assertion here; sebi.spec.ts is now the strict exact-match
// oracle for the shipped footer text.
// SEBI_PLAIN is asserted against the literal lexicon.ts string, since that is
// the only source of truth for the plain-language line in this codebase.
// ---------------------------------------------------------------------------
for (const route of ROUTES) {
  for (const mode of ['simple', 'pro'] as const) {
    test(`L6 dual SEBI disclaimer present on ${route} (${mode} mode)`, async ({ page }) => {
      await gotoWithMode(page, route, mode)
      const bodyText = await page.locator('body').innerText()
      expect(bodyText, `legal SEBI line missing on ${route} (${mode})`).toContain('NOT investment advice')
      expect(bodyText, `plain-language SEBI line missing on ${route} (${mode})`).toContain(SEBI_PLAIN)
    })
  }
}

// ---------------------------------------------------------------------------
// Check 4 — L4: learn-key resolution. Every `learn` glossary key referenced
// by a LEXICON entry must resolve to an actual GLOSSARY entry — no dangling
// tap-to-learn targets. Ported from design_evals_v2.py lines 44-48
// (used = g('key') refs in HTML, defined = G dict keys, orphan = used - defined).
// ---------------------------------------------------------------------------
test('L4 learn-key resolution — every LEXICON.learn key exists in GLOSSARY', () => {
  const used = new Set(
    Object.values(LEXICON)
      .map((e) => e.learn)
      .filter((k): k is NonNullable<typeof k> => Boolean(k))
  )
  const defined = new Set(Object.keys(GLOSSARY))
  const orphans = [...used].filter((k) => !defined.has(k))
  expect(orphans, `dangling learn-keys with no GLOSSARY entry: ${JSON.stringify(orphans)}`).toEqual([])
})

test('instrument Lynch descriptions cover every supported classification', () => {
  const classes = ['slow_grower', 'stalwart', 'fast_grower', 'cyclical', 'turnaround', 'asset_play'] as const
  for (const classification of classes) {
    const key = lynchClassLexKey(classification, 'description')
    expect(key, `missing plain-English description for ${classification}`).not.toBeNull()
    expect(LEXICON[key!].simple.length).toBeGreaterThan(0)
  }
})

test('L4 learn-key resolution (E2E) — tap targets on Signals page open a populated glossary card', async ({ page }) => {
  await gotoWithMode(page, '/signals', 'simple')
  const tapTargets = page.locator('button[aria-haspopup="dialog"]')
  const count = await tapTargets.count()
  test.skip(count === 0, 'no tap-to-learn targets rendered — likely empty data set in this environment')
  await tapTargets.first().click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  const dialogText = await dialog.innerText()
  expect(dialogText.trim().length).toBeGreaterThan(0)
  // Dialog content must match one of the known GLOSSARY entries verbatim —
  // proves the click actually resolved to real copy, not a blank/placeholder card.
  const matchesKnownEntry = Object.values(GLOSSARY).some((g) => dialogText.includes(g.headline))
  expect(matchesKnownEntry, `glossary modal content did not match any known GLOSSARY entry: ${dialogText}`).toBe(true)
})

// ---------------------------------------------------------------------------
// Check 5 — directive-verb scan. Banned imperative verbs (buy/sell/trim/exit/
// accumulate) must be absent from all output, except inside the SEBI
// plain-language negation string itself. Ported from design_evals_v2.py
// lines 78-81 (there: strips the `.plainline` div, then regex `\b(buy|sell|
// trim|accumulate|exit)\b` on the remaining text). This app's equivalent of
// the "plainline" container is `.sebi-footer` (the pinned disclaimer) — mirrors
// the existing R4/test_g0_gate.py::test_c6_sebi_substance imperative-language
// pattern used elsewhere in this codebase.
// ---------------------------------------------------------------------------
const DIRECTIVE_VERBS = /\b(buy|sell|trim|accumulate|exit)\b/i

for (const route of ROUTES) {
  test(`directive-verb scan — no imperative verbs outside SEBI line on ${route}`, async ({ page }) => {
    await gotoWithMode(page, route, 'simple')
    const bodyText = await page.locator('body').innerText()
    const footerText = await page.locator('.sebi-footer').innerText().catch(() => '')
    const scanText = footerText ? bodyText.split(footerText).join(' ') : bodyText
    const match = scanText.match(DIRECTIVE_VERBS)
    expect(match, `directive verb found outside SEBI disclaimer on ${route}: ${match?.[0]}`).toBeNull()
  })
}

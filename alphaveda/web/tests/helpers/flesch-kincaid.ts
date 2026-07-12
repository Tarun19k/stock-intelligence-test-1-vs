// A12 — Flesch-Kincaid grade helper, ported faithfully from the L2 check in
// `alphaveda/tech_stack/files (4)/design_evals_v2.py` (lines 21-34):
//
//   def fk(text):
//       sents = max(len(re.findall(r"[.!?]", text)), 1)
//       words = re.findall(r"[A-Za-z']+", text)
//       def syl(w):
//           w=w.lower(); s=len(re.findall(r"[aeiouy]+", w)); return max(s-(1 if w.endswith("e") else 0),1)
//       sy = sum(syl(w) for w in words)
//       return 0.39*len(words)/sents + 11.8*sy/len(words) - 15.59
//   PROPER = ["Reliance Industries","Reliance","HDFC Bank","HDFC","Tata Motors","KPIT Technologies",
//             "AlphaVeda","SEBI","IST"]
//
// Exposed as a standalone module (rather than inlined in the spec) so it can be
// unit-tested directly, per the A12 brief, without spinning up a page.

/** Same brand/proper-noun exclusion list as design_evals_v2.py's PROPER — these
 * are stripped before grading because brand names are not reading difficulty. */
export const FK_EXCLUDED_PROPER_NOUNS = [
  'Reliance Industries',
  'Reliance',
  'HDFC Bank',
  'HDFC',
  'Tata Motors',
  'KPIT Technologies',
  'AlphaVeda',
  'SEBI',
  'IST',
]

export function stripProperNouns(text: string): string {
  let out = text
  for (const w of FK_EXCLUDED_PROPER_NOUNS) out = out.split(w).join(' ')
  return out
}

function countSyllables(word: string): number {
  const w = word.toLowerCase()
  const vowelGroups = w.match(/[aeiouy]+/g)
  const s = vowelGroups ? vowelGroups.length : 0
  return Math.max(s - (w.endsWith('e') ? 1 : 0), 1)
}

/** Flesch-Kincaid grade level, ported 1:1 from design_evals_v2.py's fk(). */
export function fleschKincaidGrade(text: string): number {
  const sentenceMatches = text.match(/[.!?]/g)
  const sentences = Math.max(sentenceMatches ? sentenceMatches.length : 0, 1)
  const words = text.match(/[A-Za-z']+/g) ?? []
  // Deviation from the Python source (which would ZeroDivisionError on empty
  // input): guard word-count-zero explicitly rather than crash the suite.
  if (words.length === 0) return 0
  const totalSyllables = words.reduce((sum, w) => sum + countSyllables(w), 0)
  return (0.39 * words.length) / sentences + (11.8 * totalSyllables) / words.length - 15.59
}

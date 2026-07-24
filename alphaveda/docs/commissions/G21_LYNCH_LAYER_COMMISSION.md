# Content-Producer Commission — G21 Lynch Layer

Per `content-producer/SKILL.md`'s protocol, all 6 required fields:

1. **What:** Per-instrument plain-English company description + `lynch_class` story
   (why this stock is classified stalwart/cyclical/turnaround/etc., in retail-readable
   language) + a 3-question self-verification checklist (do you understand what this
   company does; would you be comfortable holding through a 20% drawdown; does the
   `lynch_class` story match what you already believed about this stock) + a
   news include/exclude filter rule (relevance-ranked, capped at 3 items, never a
   headline stronger than its source — per Munger's guardrail from the original G21
   council review, non-negotiable, applies the moment any news section exists).

2. **For whom:** Retail GSI subscriber viewing `/instrument/[ticker]` — first-week
   investor persona, not the Pro/analyst persona.

3. **Stream:** D (GSI Dashboard).

4. **Voice constraint:** Education-only, SEBI no-advice framing (per
   `sebi-compliance-reviewer`'s 7-check standard — no BUY/SELL/HOLD, no personalised
   advice, disclaimer already inherited globally via `SebiDisclaimer` in `layout.tsx`,
   do not duplicate it inline). Plain-English, grade-6.7 readability target per the
   existing design catalog's `PLAIN_LANGUAGE_LEXICON.md` standard.

5. **Length:** ~400 words per instrument (company description ~150w, `lynch_class`
   story ~150w, checklist + news-filter note ~100w).

6. **Data sources cited** (added 2026-07-24 to this skill's protocol): existing fields
   only — `instruments.name`, `instruments.sector`, `instruments.classification`,
   plus the aggregate watchlist-strip numbers already computed on the instrument page
   (`positiveCount`/`trackedCount`). Zero new ingest dependency — this is explicitly
   why this layer is buildable now while Buffett's (needs G1/fundamentals) and
   Dalio's (needs G13/macro_regime) layers are correctly blocked.

## Acceptance criteria
- One narrative block per active instrument (15 total), each following the exact
  word-count and structure above — not templated boilerplate with the ticker swapped in.
- Zero BUY/SELL/HOLD language — verified via `pre-launch-line-check.py` or equivalent
  grep pass before merge, not eyeballed.
- Each `lynch_class` story is specific to that instrument's real classification
  (stalwart/cyclical/turnaround/fast_grower/slow_grower) — a cyclical's story must not
  read like a stalwart's.
- News filter rule is documented in the component even before any real news feed
  exists (Munger's guardrail applies structurally, not only once news is live).

## Testing guide
1. Word-count check: script counts words per instrument block, flags any outside
   350–450.
2. SEBI language check: run the existing `pre-launch-line-check.py` pattern (or a
   scoped grep for `\b(buy|sell|hold)\b` case-insensitive) against the generated
   content — must return zero hits outside the words appearing inside the SEBI
   disclaimer itself.
3. Spot-check 3 instruments across 3 different `lynch_class` values by hand — confirm
   the story is genuinely differentiated, not palette-swapped.
4. Playwright: render `/instrument/RELIANCE` and `/instrument/TATASTEEL` (a stalwart
   and a cyclical), assert the narrative text differs beyond the ticker/name.

Status: commission drafted, ready to dispatch to `content-producer`. NOT yet executed —
content generation is a separate dispatch from this session's code-mechanization pass.

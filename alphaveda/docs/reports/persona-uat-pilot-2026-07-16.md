# Persona Usability Pilot — AlphaVeda (pre-A16 pre-flight)

**Date:** 2026-07-16
**Tester:** Automated persona pilot (Playwright, live site)
**Site:** https://stock-intelligence-test-1-vs.vercel.app
**Routes walked:** `/` (Market Data), `/signals`, `/path`, `/accuracy`
**Purpose:** Cheap in-character friction/confusion pass before Tarun's real human-validation (A16) test.

## Scope note (honesty)
No durable detailed protocol file existed; the three persona descriptions in the brief were treated as the authoritative scope. This is a heuristic 3-persona walkthrough, not a statistically valid usability study.

## Site state at time of test
- Data **is present** (not the empty-signals state). Market Data banner: "⚠ Data last updated 1 day ago (2026-07-14…)". This is consistent with the **known G23 pipeline-reliability gap** (scheduled ingest fires late / misses runs — already tracked, penalized, fix designed not built). Staleness itself is not a UX bug I invented; where relevant I judged only whether the *state communicates clearly*.
- A **Simple mode / Pro mode** toggle sits in the top nav and persists across routes. Its state materially changes how the Class column renders (plain-English vs. raw enum). Most of my Signals/Path/Accuracy observations were captured with the toggle in **Pro mode** (I had toggled it on `/`); personas 1 and 3 would typically be in the default mode.

---

## Persona 1 — Priya (first-week investor)

**What she did:** Landed on Market Data, scanned the table, clicked a Class chip, toggled Simple mode, then visited Signals, Path, and Accuracy in order.

**What reassured her:**
- Clicking a Class chip ("fast-growing company") opens a friendly dialog: *"What kind of company this is — We group companies by how they tend to behave…"* with a *"Professional term: Lynch classification"* footnote and a "Got it" button. This is genuinely good onboarding — it answers "what am I looking at?" in plain words.
- The pinned disclaimer's lead sentence — *"We share research and its track record. We never tell anyone what to do with their money"* — directly answers her core question ("is this telling me what to do with my money?"). Clear: **no**.
- Signal wording is soft: **"LEANS UP" / "LEANS DOWN"**, not commands. She does not feel instructed.

**What confused her / where she'd bounce:**
- **Inconsistent Class column.** In the default view, some rows are friendly chips ("fast-growing company", "steady large company", "it moves with the economy") but others render as raw enum text she can't parse: **`slow_grower`, `asset_play`, `turnaround`**. Same column, two languages. She can't click the raw ones to get the helpful dialog either.
- **Simple mode doesn't fully simplify.** Even the "simple" state leaves `slow_grower` / `asset_play` / `turnaround` untranslated; toggling to Pro turns *everything* into raw enums (`stalwart`, `cyclical`, `fast_grower`). The mode she's protected by is incomplete.
- **Signals page: "Confidence = COLD" on every row.** Tooltip ("X of 30 results for this type — too early to grade") is only visible on hover; the visible word "COLD" means nothing to her. Every single signal is COLD, so she has no idea if any signal is worth anything.
- **Path page is opaque.** "DELIBERATE STATE — Position sizes suppressed in research mode… rupee amounts require a personal-use context." She won't understand "deliberate state," "suppressed," "Quarter Kelly," or "Position vs. band: BELOW/WITHIN." Target and Stop show **"0.0%"** for every row, which reads as broken.
- **Accuracy: "✓ but negative return."** Rows show a green ✓ (direction correct) next to a **negative** return (e.g. LT LEANS DOWN, ✓, −0.02%). Nothing explains that "Hit" = direction-correct while "Return" = magnitude. She'd read "it was right but I still lost money?" and be confused about what "right" even means here.

**Net:** She *can* work out that the tool is not bossing her around (good), but she'd stall on Signals/Path because nothing is graded and the jargon (COLD, Kelly, BELOW/WITHIN, suppressed) is unexplained at the point of use.

---

## Persona 2 — Rohan (experienced DIY trader, skeptic)

**What he did:** Went straight to Accuracy to check the track record, then back-checked Signals and Path for methodology transparency.

**What builds credibility:**
- A **public per-call ledger** exists (`/accuracy`) showing every resolved call, ✓/✗, and return — not just a headline win-rate. This is more honest than most tip services.
- Methodology is *named*: "Quarter Kelly · Max 10% per position," Lynch classification, cold-start threshold of 30. He'd respect that these are disclosed.
- Soft "LEANS UP/DOWN" language and the hard disclaimer read as compliance-aware, not hype.

**What undermines credibility (his trust breaks here):**
- **Hit Rate renders as `46.666666666666664%`** — a raw unrounded float. To a skeptic this screams "amateur / unfinished / nobody QA'd this." Single most credibility-damaging item on the site. Should be `46.7%`.
- **The track record shows no edge.** Hit Rate is **below 50%** (worse than a coin toss) and **Avg Return is −0.01%** (net negative). Returns are all in the ±0.00–0.02% band — indistinguishable from rounding noise. His verdict: "this ledger honestly demonstrates the model has no demonstrated edge yet." Honest, but not persuasive — and there's no framing (sample-size caveat, "early cold-start period") to contextualize why the numbers are near-zero.
- **Every Signals confidence = COLD.** So the entire live signal set is explicitly "too early to grade." Combined with a sub-50% ledger, he sees nothing yet worth acting on.
- **Confidence is presented two different ways.** Signals shows "COLD"; Path and Accuracy show raw percentages (0%, 51%, 23%…). Same underlying quantity, inconsistent presentation — looks unfinished.
- **0% confidence rows** appear as real rows (DLF 0%) on Path and Accuracy — reads as a bug, not a signal.
- **"Active Signal Weights: No active weights yet. We're still setting up."** He'd read the methodology section as not-yet-live.

**Net:** He'd credit the honesty of a public ledger but conclude there's no proven edge yet, and the float-formatting bug + COLD-everywhere state would confirm his prior that it's "another unfinished signal service." The transparency is real; the *evidence of skill* is not yet there.

---

## Persona 3 — Kavita (anxiety-prone, non-technical, family proxy)

**What she did:** Read slowly from the top; kept looking for reassurance that this is safe/legal and that she won't be blamed.

**What reassured her:**
- The disclaimer is **pinned to the bottom of every one of the 4 pages** (verified), and its plain first line — *"We never tell anyone what to do with their money"* — is exactly the reassurance she needs. It reads human, not lawyerly.
- The Accuracy page's intro is unusually kind to a worried reader: *"…results can get worse as well as better. Negative returns are a normal part of this record and carry real downside risk if acted on; nothing here is a guarantee or a recommendation."* This normalizes losses and pre-empts self-blame — genuinely good for her.
- Empty states are gentle, not alarming: "No data yet", "We're still setting up. Check back soon."
- Nothing on the site pressures her — no countdowns, no "act now," no "BUY."

**What spikes her anxiety:**
- **The negative numbers with no reassurance at the point she sees them.** On Accuracy the tiles show "Hit Rate 46.6…%" and "Avg Return −0.01%", and the table is full of red ✗ and negative returns. The reassuring paragraph is above, but scanning the grid of minuses is unsettling for her specifically.
- **"COLD" everywhere** reads as "something is wrong / cold = broken or bad" to a non-technical reader. She doesn't know it means "not enough data yet."
- **Path page jargon** ("DELIBERATE STATE," "suppressed," "Quarter Kelly," "BELOW") sounds technical and slightly ominous ("suppressed" implies something withheld from her). The 0.0% Target/Stop columns look like an error, which raises "is this thing broken / can I trust it?"
- **The raw float `46.666666666666664%`** would actively worry her — it looks like the site is malfunctioning, and a malfunctioning money tool is a scary thing.

**Net:** Tone and disclaimer placement do a lot of the reassurance job well — she would *not* feel commanded or blamed. But the unpolished numbers (raw float, 0.0% columns, COLD everywhere) read as "is this broken?", and for an anxious user "looks broken" converts directly into "is this a scam / will I get hurt."

---

## Top 5 issues to fix before Tarun's real A16 test (ranked by severity)

1. **[HIGH] Hit Rate renders as raw float `46.666666666666664%`.** One-line formatting fix (→ `46.7%`). Highest damage-per-effort item: it breaks credibility for Rohan and reads as "broken money tool" for Kavita. Fix first.
2. **[HIGH] Class column / Simple mode is inconsistent and incomplete.** Some categories translate to plain English, others stay raw (`slow_grower`, `asset_play`, `turnaround`); Simple mode doesn't cover all enums. Ensure every Lynch category has a plain-English label and dialog, in both modes. Directly blocks Priya and Kavita.
3. **[MEDIUM-HIGH] "Confidence" is presented inconsistently and unexplained.** "COLD" on Signals vs. raw % on Path/Accuracy for the same quantity; 0% rows look like bugs; no visible (non-hover) explanation of what COLD means. Unify the presentation and add an always-visible one-line legend ("COLD = fewer than 30 graded results — too early to grade").
4. **[MEDIUM-HIGH] Path page reads as broken + jargon-heavy.** Target/Stop columns show "0.0%" for every row (should be "–" like Size, to match the deliberate-suppression pattern), and "DELIBERATE STATE / suppressed / Quarter Kelly / BELOW-WITHIN" need a plain-language gloss. Currently reads as an error state, not a designed one.
5. **[MEDIUM] Accuracy ledger needs a "Hit vs. Return" explainer and cold-start context.** Explain that ✓ = direction correct while Return = size of move (resolves Priya's "right but I lost money?"), and add a sample-size caveat so a sub-50% / near-zero-return early ledger reads as "early days, small sample" rather than "no edge / broken." This protects Rohan's trust and Kavita's calm without overclaiming.

---

## SEBI-compliance language check

Cross-checked visible copy on all 4 routes against the prohibited-language list in `alphaveda/.claude/rules/SEBI_COMPLIANCE.md`.

**No violations found.**
- No imperative/prohibited terms in any rendered output: no "BUY", "SELL", "invest in", "put money into", "you should", or "recommended for you". Signal outputs use permitted soft framing ("LEANS UP" / "LEANS DOWN").
- The mandated **SEBI disclaimer is pinned on every one of the 4 pages** (verified in each snapshot) as a non-dismissable bottom complementary region, and contains the required substance ("research and analysis only", "This is NOT investment advice", "Consult a SEBI-registered investment advisor", "Past signal accuracy does not guarantee future returns").
- Layer-4 suppression on `/path` (rupee amounts hidden, direction+confidence only) is consistent with `COMMERCIAL_GATE.md` and is framed as deliberate — compliant. The *only* caveat is UX, not compliance: the "0.0%" Target/Stop columns undercut the "designed state, not degraded fallback" intent from the commercial-gate rule (see issue #4).

**One soft observation (not a violation):** none of the near-zero / negative return figures are dressed up or spun — the ledger is if anything *conservatively* honest. That is compliant and good, but see issue #5 for the framing that keeps honesty from reading as "broken."

---

*Prepared for review. Not committed/pushed — left for Tarun.*

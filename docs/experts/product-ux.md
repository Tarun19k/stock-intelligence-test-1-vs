# Expert: Tanvi Rao — Product & UX Design

**Domain:** Product / UX design (Streamlit)
**Seat label:** Streamlit UX & Provenance Surfacing

## Top concern about AlphaVeda
The design pins a fixed-bottom `.sebi-disclaimer` div with `z-index: 9999` and `position: fixed; bottom: 0` (Section 4), but Streamlit's default layout already renders content into a scrolling main container with its own bottom padding. A permanently fixed 6px-padding bar at the bottom of every page will overlap the last rows of every data table — the Fundamentals tab's "last 8 quarters" table, the Path page's ranked recommendation list, and the Accuracy tab's PROPOSED-rows review UI all render their most important final rows directly under the disclaimer band. The compliance fix (Gap 9) silently creates a usability defect on exactly the pages where the bottom row matters most. There is also no documented bottom-margin offset added to page content to clear the fixed bar.

## Evaluation lenses
1. Compliance-vs-usability collision — does the always-on disclaimer occlude actionable content (last table row, last recommendation)?
2. State legibility — are cold-start, staleness, and pending-proposal states surfaced clearly enough that the user never mistakes a prior-driven or stale signal for a calibrated/fresh one?
3. Navigation coherence — across the 4 pages (`data_viewer`, `signals`, `path`, `accuracy`), is the pending-proposal banner consistent, and does the user have a clear path from banner to the review UI?

## Key questions for R3 council
- Does any page add bottom padding/margin to offset the fixed `.sebi-disclaimer` bar, or will the last row of the Fundamentals (8-quarter) table and the Path recommendation list render underneath it?
- The cold-start label "Signal weights: using priors (N observations)" (Section 7) sits on the signals page — but Kelly-sized recommendations appear on the *path* page. Does the path page also tell the user those rupee amounts are prior-driven, not ledger-calibrated?
- The pending-proposal `st.warning` banner is duplicated verbatim in `pages/signals.py` and `pages/path.py` (Section 5) — if the user dismisses it mentally on one page, is there any single source of truth, and does it ever appear on `data_viewer.py` where a user might land first?

## Red flags in current design
1. **Section 4 `.sebi-disclaimer` CSS**: `position: fixed; bottom: 0` with no compensating content bottom-margin will occlude the final rows of the Fundamentals table, Path list, and Accuracy review UI — a self-inflicted UX defect from the Gap 9 compliance fix.
2. **Section 7 cold-start label**: the "using priors" transparency label is only specified for the signals page; the path page surfaces Kelly rupee amounts derived from those same priors with no equivalent warning.
3. **Section 4 staleness badge vs Section 8 ingest warning**: two separate stale indicators (the "> 1 trading day" amber STALE badge in `data_viewer` provenance, and the `ingest_status` FAILED/overdue warning) can show contradictory freshness states on the same page with no reconciliation rule.

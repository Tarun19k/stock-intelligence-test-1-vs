# AlphaVeda — MVP Specification
# Status: CURRENT — reflects Phases 1–6 + UI-1 as built
# Owner: Tarun Kochhar | Authored: 2026-06-27
# Skills: ui-ux-pro-max + bridge-architect | Model: Sonnet 4.6

---

## 1. Capabilities Matrix

| # | Capability | What it does | Implementation | Gate |
|---|---|---|---|---|
| C1 | **Market Data Ingest** | Daily EOD OHLCV from NSE/BSE Bhavcopy via GHA pipeline; circuit-flag detection; staleness tracking | `src/ingest/bhavcopy.py` + `scripts/ingest.py` + `ingest_status` table | G0 (live seed) |
| C2 | **Signal Engine** | 7-council signal pipeline: momentum, trend, fundamental, streak, calibration, arbitration, Kelly-ready output | `src/signals/ledger.py`, `downside.py`, `arbitration.py`, `weights.py`, `engine.py` | Phase 3 ✓ |
| C3 | **Kelly Position Sizing** | Downside-adjusted Kelly fraction → rupee position size; E1–E4 exit rules; portfolio-value-aware | `src/portfolio/optimizer.py`, `buckets.py` | Phase 4 ✓ |
| C4 | **Signal Accuracy Ledger** | Per-segment outcome tracking; hit-rate vs OBSERVATION_THRESHOLD (30); PROPOSED weight proposals; 90-day review gate | `signal_weights` table; `src/pages/accuracy.py` | Phase 3 ✓ |
| C5 | **SEBI Compliance Layer** | Fixed-bottom non-dismissable disclaimer on every page; no BUY/SELL language; no personalised advice framing; RA boundary enforced | `constants.py → SEBI_DISCLAIMER`; `src/app.py → get_disclaimer_html()`; Varghese 7-check suite | Always on |
| C6 | **Commercial State Gate** | Auto-detects first subscriber via `waitlist.converted_at`; blocks yfinance; suppresses rupee amounts; FMP required when commercial=True | `src/config.py → is_commercial()`; `CommercialLicenseError` in DataProvider | Pre-subscriber |

---

## 2. User Personas

### Persona A — Retail Researcher
**Profile:** Individual investor, 30–55 years, follows NSE/BSE, reads Moneycontrol/Screener. No quant background.
**Goal:** Get a second opinion on whether a stock shows research signals worth investigating further.
**Primary pages:** Data Viewer → Signals.
**Pain:** Signal information is scattered across 5+ sources with no confidence weighting.
**AlphaVeda value:** Single-pane view — instrument data alongside a BULL/BEAR signal with a calibrated confidence bar. Not a tip. A starting point.
**Accessibility needs:** Plain language labels. Cold-start label must not say "Bayesian priors" (UX backlog item — Phase 7).
**SEBI interaction:** Sees disclaimer at page bottom on every interaction. Must never feel like a recommendation.

---

### Persona B — HNI DIY Investor
**Profile:** High-net-worth individual, self-managed portfolio, ₹50L–₹2Cr deployed. Understands risk/reward framing.
**Goal:** Decide how large a position to take if the signal is BULLISH. Wants the math done.
**Primary pages:** Signals → Path.
**Pain:** Position sizing requires Kelly formula inputs (p, b, downside) that are tedious to compute manually.
**AlphaVeda value:** Calibrated probability from ledger + downside target from ATR → Kelly rupee amount, instantly. Pre-commercial state only (post-subscriber: direction shown, rupee suppressed).
**SEBI interaction:** Path page rupee amount carries a deliberate suppression label when commercial (not an error — a designed state).

---

### Persona C — Data-Curious Experimenter
**Profile:** Developer or analyst, wants to understand model quality before trusting signals. Likely evaluating AlphaVeda as a tool.
**Goal:** Verify that the signal engine has enough observation history and decent hit-rates before relying on it.
**Primary pages:** Accuracy Ledger.
**Pain:** Black-box models provide no visibility into how often they're right.
**AlphaVeda value:** Per-segment hit-rate table, observation count vs threshold (30), PROPOSED weight queue for review. Full transparency — the model surfaces its own uncertainty.
**SEBI interaction:** Same non-dismissable footer. Research tool framing.

---

## 3. UI-2 Page Design Brief

Builds on UI-1 (complete — commit f36e6c9):
- Design tokens: `--indigo`, `--gold`, `--emerald`, `--terra`, `--ivory`
- Typography: Fraunces (display), DM Sans (body), DM Mono (data)
- Components: `.av-signal-card`, `.av-signal-chip`, `.av-conf-track`, `.av-sebi-footer`, `.av-kelly`

UI-2 goal: wire these tokens to real data content on each page.

---

### Page 1 — Data Viewer

**Purpose:** Show instrument data — price history, volume, circuit flags.

**Layout (top → bottom):**
1. Page header: `h1` Fraunces italic — "Market Data"
2. Staleness banner (when stale): `st.warning()` — terra-toned; banner text from `get_staleness_banner()`
3. Instrument selector: `st.selectbox()` — DM Mono font for ticker symbols
4. OHLCV table: `st.dataframe()` — `font-data` class; columns: Date / Open / High / Low / Close / Volume / circuit_flag
5. Circuit-flag indicator: inline badge when `circuit_flag=True` — gold border, ⚡ prefix
6. Secondary: fundamentals summary (Q over Q) when available
7. SEBI footer: always present (injected by app.py)

**Empty state:** "Connect to Supabase and seed instruments to view data here." — muted ivory, DM Sans.
**Staleness state:** Banner uses `--terra` accent, softened background (`rgba(192, 80, 58, 0.12)`).
**Cold-start interaction:** Not applicable on this page.

---

### Page 2 — Signals

**Purpose:** Show BULL/BEAR signal output per instrument per segment.

**Layout (top → bottom):**
1. Page header: `h1` Fraunces italic — "Signals"
2. Weight review banner (when PROPOSED weights exist): `st.warning()` — gold-toned; text from `get_weight_review_banner()`
3. Cold-start label (when `segment_obs < 30`): `st.info()` — muted text, non-alarming; text from `get_cold_start_label()`
4. Instrument + segment selectors: two `st.selectbox()` side by side
5. Signal card grid: `signal_card_html()` from `src/styles.py`
   - `.av-instrument` — stock name, DM Sans 500
   - `.av-signal-chip.bull` / `.bear` — emerald / terra
   - `.av-conf-track` + `.av-conf-fill` — confidence bar, 3px height
   - `.av-lynch-class` — segment label below bar
   - `.av-kelly` — rupee figure, DM Mono gold (or `—` when suppressed)
6. SEBI caption: "Signal output is research-only. See SEBI disclaimer below."

**Empty state:** "Select an instrument and segment to view signals." — muted ivory.
**Cold-start state:** info box (ivory/muted), not a warning. Conveys lower confidence, not failure.
**Weight review state:** amber warning bar with count + action prompt.

---

### Page 3 — Path

**Purpose:** Kelly position sizing — what direction and how much.

**Layout (top → bottom):**
1. Page header: `h1` Fraunces italic — "Path"
2. Suppression label (when `is_commercial()=True`): `st.info()` — deliberate state label, not error. Text: "Position size is shown as direction + confidence only."
3. Weight review banner: mirrors Signals page (shared `get_proposed_weights_count()`)
4. Instrument + segment selectors
5. Direction indicator: large Fraunces display, emerald or terra
6. Confidence reading: `.av-conf-track` full-width
7. Kelly rupee amount: `.av-kelly` DM Mono gold — `₹{amount:,}` format; or `—` when suppressed
8. Exit rules panel: E1–E4 indicators in a 2×2 grid — `st.metric()` styled with design tokens
9. SEBI caption

**Empty state:** "Select an instrument and segment to view Kelly sizing path." — muted ivory.
**Suppression state:** `st.info()` banner + direction shown + `—` instead of rupee. Must read as intentional design, not degradation.

---

### Page 4 — Accuracy

**Purpose:** Signal model transparency — hit-rates, observation counts, weight proposals.

**Layout (top → bottom):**
1. Page header: `h1` Fraunces italic — "Accuracy Ledger"
2. Staleness warning (when last review > 90 days): `st.warning()` — terra-toned; text from `get_staleness_warning()`
3. PROPOSED weight summary: metric cards — "N weights pending review"; gold accent
4. Segment hit-rate table: `st.dataframe()` — DM Mono font; columns: Segment / Observations / Hit Rate / Status
5. Observation threshold indicator: progress-style display; shows `X / 30` observations per segment
6. Weight proposal queue: expandable section; rows with PROPOSED weights, approve/archive UI (Phase 7 full interactivity)

**Empty state:** "Accuracy data will populate once predictions reach 30 observations." — muted ivory, with observation count progress.
**Staleness state:** terra-toned warning, clear days-overdue count.
**PROPOSED state:** gold-accented count badge + action prompt.

---

## 4. UX Feature List

### MVP Does

| Feature | Page | Implementation |
|---|---|---|
| Signal research with confidence scoring | Signals | `engine.py` → `signal_card_html()` |
| Staleness banner — data not refreshed | Data Viewer | `get_staleness_banner()` |
| Staleness warning — weights not reviewed | Accuracy | `get_staleness_warning()` |
| Cold-start label — pre-threshold segment | Signals | `get_cold_start_label()` |
| Weight review banner — PROPOSED queue | Signals, Path | `get_weight_review_banner()` |
| Kelly rupee sizing (pre-commercial) | Path | `kelly_position_size()` |
| Rupee suppression label (commercial) | Path | `get_suppression_label()` |
| SEBI disclaimer — every page, fixed-bottom | All | `av-sebi-footer` CSS class |
| Commercial state auto-detection | All | `is_commercial()` → Supabase query |
| Circuit-flag exclusion from accuracy | Backend | `resolve_outcomes.py` |
| Design system — dark theme, branded | All | `src/styles.py` via `get_css()` |

### MVP Does Not (out of scope — Phase 7+)

| Feature | Reason deferred |
|---|---|
| User accounts / authentication | Phase 7 — Supabase Auth |
| Portfolio management / trade execution | Outside SEBI RA boundary |
| Real-time price data | EOD only; paid data gate |
| Multi-instrument comparison view | Phase 7 UI scope |
| Alerts / notifications | Phase 7 — infrastructure |
| Mobile-optimised layout | Phase 7 — responsive pass |
| Weight approval UI (interactive) | Phase 7 — full interactivity |
| Accessible language pass ("Bayesian priors") | Phase 7 UX polish — UX backlog item |

---

## 5. Cold-Start / Empty / Staleness State Map

| State | Trigger | Visual treatment | Location |
|---|---|---|---|
| Empty — no data | G0 not seeded | `st.info()` ivory, centred | Data Viewer, Signals, Path, Accuracy |
| Stale — data not refreshed | `ingest_status` last_run not today | `st.warning()` terra-toned | Data Viewer |
| Cold-start — low observation count | `segment_obs < 30` | `st.info()` non-alarming, muted | Signals |
| Weight overdue — 90-day gate | `last_review_date` > 90 days ago | `st.warning()` terra-toned | Accuracy |
| Weight pending — PROPOSED queue | `get_proposed_weights_count() > 0` | `st.warning()` gold-toned | Signals, Path |
| Commercial — rupee suppressed | `is_commercial()=True` | `st.info()` — deliberate state label | Path |
| Circuit-locked — excluded | `circuit_flag=True` | Badge indicator in OHLCV table | Data Viewer |

---

## 6. SEBI Compliance Summary (Varghese)

All 7 checks from `sebi-compliance-reviewer` SKILL.md pass:
1. Disclaimer present on every page — `PAGE_REQUIRES_DISCLAIMER = True` in all 4 pages
2. No BUY/SELL/HOLD language — signal labels: "BULL" / "BEAR" only
3. No personalised advice — caption on every page: "Signal output is research-only"
4. Past-performance disclaimer — accuracy page carries the 90-day review gate framing
5. RA boundary — no recommendations framing; `SEBI_DISCLAIMER` text explicit
6. Risk disclosure — disclaimer includes risk language (in `constants.py`)
7. Non-dismissable — `av-sebi-footer` is `position: fixed; bottom: 0`; no onclick/button/dismiss in HTML

---

## 7. Definition of MVP Complete

| Gate | Status | Blocker |
|---|---|---|
| Phases 1–6 signed off | ✓ DONE | — |
| UI-1 design system | ✓ DONE | — |
| All 21 seats skill-backed | ✓ DONE | — |
| G0 live DB seed | ✗ BLOCKED | Tarun: `python3 scripts/ingest.py` |
| MVP accessible in browser | ✗ BLOCKED | G0 seed |
| First non-self page load with real data | ✗ BLOCKED | G0 seed |

MVP is code-complete. Single blocker: G0 seed (live Supabase data population).

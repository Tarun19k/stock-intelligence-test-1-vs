# AlphaVeda — central constants
# Single source of truth for all tunable values.
# Design doc: Section 5 (v0.6). Change here = change everywhere.

# ── Fundamentals guard (Buffett) ────────────────────────────────────────────
FUNDAMENTAL_WEIGHT_FLOOR = 0.30
# Combined weight of ROIC + FCF + pledge signals never drops below this
# regardless of ledger accuracy. Prevents short-term accuracy pressure
# from gutting the fundamental layer.

# ── Counter-cyclical / streak guard (Soros) ─────────────────────────────────
STREAK_WINDOW          = 5    # consecutive correct predictions to trigger flag
STREAK_DISCOUNT_FACTOR = 0.7  # confidence multiplier at emit when flag = True
# Fires at emit time (step 3b), BEFORE calibration and Kelly consume confidence.
# PIPELINE CONTRACT: calibration bins must be built from post-discount confidence values.

# ── Accuracy ledger thresholds (Lynch / Munger) ──────────────────────────────
OBSERVATION_THRESHOLD = 30    # min observations per segment before weight proposal
PROPOSAL_MIN_DELTA    = 0.03  # proposal only if new weight differs from active by >= 3%

# ── Cycle phase (Marks) ──────────────────────────────────────────────────────
VIX_CALM_THRESHOLD = 18.0

# ── Signal arbitration (Reddy) ───────────────────────────────────────────────
ARBITRATION_MARGIN = 15.0
# Suppress emission if |weighted_bull - weighted_bear| < ARBITRATION_MARGIN.

# ── Regime freshness (Dalio) ─────────────────────────────────────────────────
REGIME_STALENESS_DAYS = 3

# ── Kelly sizing (Druckenmiller) ─────────────────────────────────────────────
QUARTER_KELLY_FRACTION = 0.25   # use 25% of full Kelly to limit variance
PORTFOLIO_VALUE        = 725000  # ₹7.25L — GSI equity tranche (constants.py is source of truth)
MAX_POSITION_PCT       = 0.10    # ₹72,500 cap per position
MIN_POSITION_PCT       = 0.01    # ₹7,250 — reference only; NOT a floor inside kelly_position_size
SECTOR_CAP_PCT         = 0.35
CASH_FLOOR_PCT         = 0.10

# ── Downside target / ATR (GAP-001 fix) ─────────────────────────────────────
ATR_PERIOD     = 14
ATR_MULTIPLIER = 1.0   # downside_target = ATR(14) / price × ATR_MULTIPLIER

# ── EXIT trigger E2 — bucket-aware (Druckenmiller) ───────────────────────────
E2_CONSECUTIVE_THRESHOLD: dict[str, int] = {
    "near_term":   3,
    "medium_term": 5,
    "long_term":   7,
}
E2_CONFIDENCE_FLOOR = 50  # emits below this do not count toward E2 streak

# ── Commercial gate ──────────────────────────────────────────────────────────
# NEVER derive from env flag — always derive from waitlist.converted_at (fail-closed).
# See src/config.py → is_commercial().
ALPHAVEDA_COMMERCIAL_ENV_KEY = "ALPHAVEDA_COMMERCIAL"  # used only in test overrides

# ── SEBI (Varghese) ──────────────────────────────────────────────────────────
SEBI_DISCLAIMER = (
    "AlphaVeda provides information and analysis only. "
    "This is NOT investment advice. Consult a SEBI-registered "
    "investment advisor before making any investment decision. "
    "Past signal accuracy does not guarantee future returns."
)

# ── Cold-start weights — Bayesian priors (Synthesis Chair / Gap-011) ─────────
# Segment-level defaults used until each segment reaches OBSERVATION_THRESHOLD.
# FUNDAMENTAL_WEIGHT_FLOOR applies: ROIC + FCF + pledge combined >= 0.30.
# Source: Lynch's PEG priority for fast growers; Buffett's ROIC priority for stalwarts.
COLD_START_WEIGHTS: dict[str, dict[str, float]] = {
    "fast_grower": {
        "roic": 0.30, "eps_growth": 0.25, "peg": 0.20,
        "momentum_rsi": 0.15, "pledge": 0.10,
    },
    "stalwart": {
        "roic": 0.35, "fcf": 0.25, "eps_growth": 0.15,
        "momentum_rsi": 0.15, "pledge": 0.10,
    },
    "slow_grower": {
        "fcf": 0.35, "dividend": 0.25, "roic": 0.20,
        "pledge": 0.15, "momentum_rsi": 0.05,
    },
    "cyclical": {
        "macro_regime": 0.35, "roic": 0.20, "momentum_rsi": 0.25,
        "pledge": 0.10, "fcf": 0.10,
    },
    "turnaround": {
        "fcf": 0.30, "debt_equity": 0.25, "roic": 0.20,
        "pledge": 0.15, "momentum_rsi": 0.10,
    },
    "asset_play": {
        "roic": 0.25, "fcf": 0.25, "book_value": 0.25,
        "pledge": 0.15, "momentum_rsi": 0.10,
    },
}

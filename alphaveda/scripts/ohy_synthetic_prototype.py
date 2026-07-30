#!/usr/bin/env python3
"""
OHY Synthetic Prototype — Offset/Harvest/Yield decision loop, offline/synthetic only.

WHAT THIS IS: an executable simulation of the full
Observe -> Offset -> Harvest -> Yield -> Offset-revalidation -> human-decision loop,
using a synthetic (fake) portfolio and PLACEHOLDER thresholds/formulas.

WHAT THIS IS NOT: a real financial recommendation engine. Per the source material
(Portfolio Churn Strategy Design PDF) and OFFSET_HARVEST_YIELD_FOUNDATION.md Prereqs 5/7,
every threshold, cost figure, and tax rule below is explicitly a PLACEHOLDER pending
Tarun's real methodology (G2 decision class — Claude may not finalize this autonomously).
Every placeholder value is tagged PLACEHOLDER in its own variable name or comment.

Run: python3 alphaveda/scripts/ohy_synthetic_prototype.py
No network calls, no database writes, no real holdings used.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import date
from enum import Enum


# ---------------------------------------------------------------------------
# Synthetic golden portfolio — entirely fake data, not read from any real table
# ---------------------------------------------------------------------------

@dataclass
class SyntheticHolding:
    ticker: str
    qty: int
    avg_cost: float
    current_price: float

    @property
    def market_value(self) -> float:
        return self.qty * self.current_price


SYNTHETIC_PORTFOLIO = [
    SyntheticHolding("SYN_RELIANCE", qty=100, avg_cost=2400.0, current_price=3100.0),
    SyntheticHolding("SYN_HDFCBANK", qty=150, avg_cost=1500.0, current_price=1650.0),
    SyntheticHolding("SYN_TATASTEEL", qty=500, avg_cost=110.0, current_price=95.0),
    SyntheticHolding("SYN_LIQUIDFUND", qty=1, avg_cost=150000.0, current_price=150000.0),
]


# ---------------------------------------------------------------------------
# Objective math — portfolio value, concentration. NOT G2 (no judgment call,
# just arithmetic), safe to implement now with real formulas.
# ---------------------------------------------------------------------------

def portfolio_value(holdings):
    return sum(h.market_value for h in holdings)


def concentration_pct(holding, holdings):
    total = portfolio_value(holdings)
    return round(100 * holding.market_value / total, 2) if total else 0.0


# ---------------------------------------------------------------------------
# Severity vocabulary — real, already documented in OFFSET_HARVEST_YIELD_FOUNDATION.md
# section 7 (source p.37-38). Not a placeholder — this enum is already agreed.
# ---------------------------------------------------------------------------

class Severity(Enum):
    DORMANT = 0
    OBSERVED = 1
    MONITORING = 2
    REVIEW = 3
    ACTION_JUSTIFIED = 4
    CRITICAL = 5


# PLACEHOLDER pending Prereq 5 (G2) — this exact number (15%) is not an approved
# threshold, it is the concentration-review number used informally in this
# session's UI mockups. Do not treat as real financial guidance.
PLACEHOLDER_CONCENTRATION_REVIEW_THRESHOLD_PCT = 15.0


# ---------------------------------------------------------------------------
# Offset engine — real contract shape from OFFSET_HARVEST_YIELD_FOUNDATION.md
# section 6. Enum values are real/agreed. The threshold check inside is a
# PLACEHOLDER standing in for Prereq 5's real materiality formula.
# ---------------------------------------------------------------------------

class OffsetOutput(Enum):
    NO_MATERIAL_OFFSET = "no_material_offset"
    MONITOR = "monitor"
    CORRECT_VIA_CASHFLOW = "correct_via_cashflow"
    PARTIAL_REBALANCE = "partial_rebalance"
    BROADER_REALLOCATION = "broader_reallocation"
    URGENT_HUMAN_ESCALATION = "urgent_human_escalation"


@dataclass
class OffsetResult:
    output: str
    severity: str
    evidence: list
    placeholder_note: str


def run_offset_engine(holdings) -> OffsetResult:
    evidence = []
    max_conc_holding = max(holdings, key=lambda h: concentration_pct(h, holdings))
    conc = concentration_pct(max_conc_holding, holdings)
    evidence.append(f"{max_conc_holding.ticker} concentration: {conc}%")

    # PLACEHOLDER decision logic — real materiality test is Prereq 5 (G2)
    if conc >= PLACEHOLDER_CONCENTRATION_REVIEW_THRESHOLD_PCT:
        output = OffsetOutput.PARTIAL_REBALANCE
        severity = Severity.REVIEW
    elif conc >= PLACEHOLDER_CONCENTRATION_REVIEW_THRESHOLD_PCT * 0.7:
        output = OffsetOutput.MONITOR
        severity = Severity.MONITORING
    else:
        output = OffsetOutput.NO_MATERIAL_OFFSET
        severity = Severity.DORMANT

    return OffsetResult(
        output=output.value,
        severity=f"{severity.value} - {severity.name}",
        evidence=evidence,
        placeholder_note="Threshold is PLACEHOLDER pending Prereq 5 (G2) — not a real materiality formula.",
    )


# ---------------------------------------------------------------------------
# Harvest engine — real 6-subtype structure from the Glossary/contract.
# Eligibility check is PLACEHOLDER pending Prereq 5/7 (G2, tax logic explicitly named).
# ---------------------------------------------------------------------------

class HarvestSubtype(Enum):
    GOAL_LIQUIDITY = "goal_liquidity"
    RISK_CONCENTRATION = "risk_concentration"
    TAX_LOSS = "tax_loss"
    TAX_GAIN = "tax_gain"
    INCOME = "income"
    OPPORTUNITY = "opportunity"


class HarvestOutput(Enum):
    NOT_ELIGIBLE = "not_eligible"
    ELIGIBLE_PENDING_COST_CHECK = "eligible_pending_cost_check"
    ELIGIBLE = "eligible"


@dataclass
class HarvestResult:
    subtype: str
    output: str
    unrealised_gain_or_loss: float
    placeholder_note: str


def run_harvest_engine(holdings) -> HarvestResult:
    # Look for a real tax-loss harvest candidate: any holding with an unrealised loss.
    loss_candidates = [h for h in holdings if h.current_price < h.avg_cost]
    if not loss_candidates:
        return HarvestResult(
            subtype=HarvestSubtype.TAX_LOSS.value,
            output=HarvestOutput.NOT_ELIGIBLE.value,
            unrealised_gain_or_loss=0.0,
            placeholder_note="No loss-position candidate in this synthetic portfolio.",
        )

    candidate = loss_candidates[0]
    unrealised = round((candidate.current_price - candidate.avg_cost) * candidate.qty, 2)

    # PLACEHOLDER — real tax-loss set-off rules are Prereq 7 (G2), not implemented here.
    return HarvestResult(
        subtype=HarvestSubtype.TAX_LOSS.value,
        output=HarvestOutput.ELIGIBLE_PENDING_COST_CHECK.value,
        unrealised_gain_or_loss=unrealised,
        placeholder_note=(
            f"{candidate.ticker} shows an unrealised loss of Rs.{unrealised} — "
            "flagged as a REAL tax-loss-harvest CANDIDATE, but no actual tax rule "
            "(set-off ordering, holding-period, carry-forward) is applied. "
            "Prereq 7 (G2) required before this becomes a real recommendation."
        ),
    )


# ---------------------------------------------------------------------------
# Yield engine — category-only allocation per the source's Phase G gate
# ("never individual security picks"). Selection logic is PLACEHOLDER.
# ---------------------------------------------------------------------------

class YieldAllocation(Enum):
    RETAIN_CASH = "retain_cash"
    BROAD_EQUITY = "broad_equity"
    DIVERSIFIED_EQUITY = "diversified_equity"
    LIQUID_SHORT_DURATION = "liquid_short_duration"
    GOAL_RESERVE = "goal_reserve"


@dataclass
class YieldResult:
    allocation_category: str
    available_capital: float
    placeholder_note: str


def run_yield_engine(available_capital: float) -> YieldResult:
    # PLACEHOLDER — real goal-adjusted / risk-adjusted return methodology is Prereq 5 (G2).
    if available_capital <= 0:
        category = YieldAllocation.RETAIN_CASH
    elif available_capital < 100000:
        category = YieldAllocation.LIQUID_SHORT_DURATION
    else:
        category = YieldAllocation.DIVERSIFIED_EQUITY

    return YieldResult(
        allocation_category=category.value,
        available_capital=available_capital,
        placeholder_note="Category selection is PLACEHOLDER pending Prereq 5's real return methodology.",
    )


# ---------------------------------------------------------------------------
# Full loop: Observe -> Offset -> Harvest -> Yield -> Offset revalidation
# This orchestration structure is real (source p.37, already in
# OFFSET_HARVEST_YIELD_FOUNDATION.md section 7) — the loop itself is not a
# placeholder, only the numeric decisions inside each engine are.
# ---------------------------------------------------------------------------

def run_full_decision_loop(holdings):
    print("=" * 70)
    print("OHY SYNTHETIC PROTOTYPE RUN —", date.today().isoformat())
    print("SYNTHETIC DATA ONLY. PLACEHOLDER THRESHOLDS. NOT A REAL RECOMMENDATION.")
    print("=" * 70)

    print("\n--- Step 1: Observe (portfolio state) ---")
    total = portfolio_value(holdings)
    print(f"Synthetic portfolio value: Rs.{total:,.2f}")
    for h in holdings:
        print(f"  {h.ticker}: qty={h.qty}, value=Rs.{h.market_value:,.2f}, "
              f"concentration={concentration_pct(h, holdings)}%")

    print("\n--- Step 2: Run Offset ---")
    offset_result = run_offset_engine(holdings)
    print(f"Output: {offset_result.output}  (severity: {offset_result.severity})")
    print(f"Evidence: {offset_result.evidence}")
    print(f"Note: {offset_result.placeholder_note}")

    print("\n--- Step 3: Run Harvest ---")
    harvest_result = run_harvest_engine(holdings)
    print(f"Subtype: {harvest_result.subtype}, Output: {harvest_result.output}")
    print(f"Note: {harvest_result.placeholder_note}")

    print("\n--- Step 4: Run Yield ---")
    # Available capital = liquid fund holding, as a synthetic funding source example
    available = next((h.market_value for h in holdings if "LIQUIDFUND" in h.ticker), 0.0)
    yield_result = run_yield_engine(available)
    print(f"Allocation category: {yield_result.allocation_category}")
    print(f"Note: {yield_result.placeholder_note}")

    print("\n--- Step 5: Offset revalidation (mandatory, non-optional) ---")
    print("Re-running Offset against the post-Yield hypothetical state...")
    # Real structural requirement from the source (p.37): re-check Offset after
    # Yield's proposed allocation, since it could introduce new concentration.
    revalidation = run_offset_engine(holdings)  # synthetic: same portfolio, no real re-allocation applied
    print(f"Revalidation output: {revalidation.output} (unchanged — no real reallocation was executed)")

    print("\n--- Step 6: Human decision required ---")
    decision_object = {
        "run_date": date.today().isoformat(),
        "portfolio_value": total,
        "offset": asdict(offset_result),
        "harvest": asdict(harvest_result),
        "yield": asdict(yield_result),
        "offset_revalidation": asdict(revalidation),
        "no_action_comparator": "Preserve (Option 0) — always available per source p.37",
        "acceptance_criteria_note": (
            "This decision object is reproducible from the synthetic inputs above "
            "(Prereq 10, criterion 1) and every input has lineage (criterion 2) — "
            "but criteria 5/6 (taxes/costs included, missing-data blocking) are NOT "
            "met since Prereq 5/7 remain unresolved. This object must not be presented "
            "to a real user as a real recommendation."
        ),
    }
    print(json.dumps(decision_object, indent=2))
    return decision_object


def load_portfolio_from_json(path: str):
    """Load a custom synthetic portfolio from a JSON file for interactive testing.

    Expected format:
    [
      {"ticker": "SYN_ANYTHING", "qty": 100, "avg_cost": 500.0, "current_price": 650.0},
      ...
    ]
    Tickers do not need a SYN_ prefix, but keep them clearly fake — this script must
    never be pointed at a real holdings table.
    """
    with open(path) as f:
        raw = json.load(f)
    return [SyntheticHolding(**row) for row in raw]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
        print(f"Loading custom synthetic portfolio from: {custom_path}\n")
        portfolio = load_portfolio_from_json(custom_path)
    else:
        print("No custom portfolio file given — using the built-in synthetic example.")
        print("To test your own scenario: python3 ohy_synthetic_prototype.py <path-to-json>\n")
        portfolio = SYNTHETIC_PORTFOLIO

    run_full_decision_loop(portfolio)

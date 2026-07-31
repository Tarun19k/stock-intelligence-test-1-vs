#!/usr/bin/env python3
"""SYNTHETIC test of the grandfathering formula (OFFSET_HARVEST_YIELD_FOUNDATION.md Sec. 10).

No real holding in the ingested portfolio predates 31-01-2018 (confirmed live via
`SELECT * FROM holdings_lots WHERE buy_date < '2018-01-31'` -> 0 rows, 2026-07-31),
so this exercises the formula against invented pre-2018 scenarios per Tarun's explicit
request ("produce mock data to test it out") -- not real financial data, not written
to any database, clearly labeled as such throughout (NO_HARDCODING.md's own exemption
for labeled synthetic test fixtures).

Formula under test:
  Cost of Acquisition = Min(Sale Price, Max(Actual Purchase Price, FMV on 31-01-2018))
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SyntheticLot:
    label: str
    actual_purchase_price: float
    fmv_20180131: float
    sale_price: float
    scenario_note: str


def grandfathered_cost(actual_purchase_price: float, fmv_20180131: float, sale_price: float) -> float:
    return min(sale_price, max(actual_purchase_price, fmv_20180131))


SYNTHETIC_LOTS = [
    SyntheticLot(
        label="SYN-A (classic grandfathering benefit)",
        actual_purchase_price=50.0,
        fmv_20180131=200.0,
        sale_price=500.0,
        scenario_note="FMV far above purchase price and below sale price -- the textbook case "
                       "the formula exists for. Real gain (500-50=450) gets reduced to a taxable "
                       "gain of only 300 (500-200) by using FMV as the acquisition cost.",
    ),
    SyntheticLot(
        label="SYN-B (FMV exceeds sale price -- capped)",
        actual_purchase_price=50.0,
        fmv_20180131=600.0,
        sale_price=500.0,
        scenario_note="FMV is even higher than what it eventually sold for. The Min() term caps "
                       "acquisition cost at the sale price itself -- this correctly prevents booking "
                       "a taxable LOSS purely from a paper 31-01-2018 valuation, per the formula's "
                       "own design (grandfathering can reduce a gain to zero, never manufacture a loss).",
    ),
    SyntheticLot(
        label="SYN-C (FMV below purchase price -- formula ignores it)",
        actual_purchase_price=300.0,
        fmv_20180131=100.0,
        sale_price=500.0,
        scenario_note="FMV on the cutoff date was LOWER than what was actually paid (bought after a "
                       "run-up, or a stock that dipped by 2018). The Max() term correctly falls back "
                       "to actual purchase price -- grandfathering never makes acquisition cost worse "
                       "than what was really paid.",
    ),
    SyntheticLot(
        label="SYN-D (real loss even after grandfathering)",
        actual_purchase_price=300.0,
        fmv_20180131=250.0,
        sale_price=150.0,
        scenario_note="Sale price is below both actual cost and FMV -- a genuine capital loss. "
                       "Grandfathering doesn't apply upside logic here; Max(300,250)=300, "
                       "Min(150,300)=150, so acquisition cost = sale price = 150, gain/loss = 0, "
                       "not a fabricated loss beyond what real numbers show. (Note: true STCL/LTCL "
                       "in this case is actually computed as sale_price - actual_purchase_price = "
                       "150-300 = -150 under Sec 112A's loss rules, which do NOT use the grandfathering "
                       "Min/Max formula -- that formula is a GAIN-reduction mechanism only. Flagging "
                       "this distinction for Prereq 5/7 code: loss cases must not run through this "
                       "same grandfathered-cost function.)",
    ),
]


def run() -> None:
    print("SYNTHETIC grandfathering formula test -- NOT real financial data\n")
    print(f"{'Scenario':45s} {'Purchase':>10s} {'FMV':>10s} {'Sale':>10s} {'Acq.Cost':>10s} {'Taxable Gain':>13s}")
    print("-" * 100)
    for lot in SYNTHETIC_LOTS:
        cost = grandfathered_cost(lot.actual_purchase_price, lot.fmv_20180131, lot.sale_price)
        gain = lot.sale_price - cost
        print(f"{lot.label:45s} {lot.actual_purchase_price:>10.2f} {lot.fmv_20180131:>10.2f} "
              f"{lot.sale_price:>10.2f} {cost:>10.2f} {gain:>13.2f}")
        print(f"   -> {lot.scenario_note}\n")

    assert grandfathered_cost(50, 200, 500) == 200, "SYN-A failed"
    assert grandfathered_cost(50, 600, 500) == 500, "SYN-B failed"
    assert grandfathered_cost(300, 100, 500) == 300, "SYN-C failed"
    assert grandfathered_cost(300, 250, 150) == 150, "SYN-D failed"
    print("All 4 synthetic scenarios match expected formula output.")
    print("\nReal-portfolio applicability: NONE currently -- 0 of 184 real holding lots have a")
    print("buy_date before 2018-01-31 (verified live, 2026-07-31). This test exists to validate")
    print("the formula's correctness ahead of any future holding that would actually need it.")


if __name__ == "__main__":
    run()

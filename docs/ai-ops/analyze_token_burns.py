#!/usr/bin/env python3
"""Token Burn Log Aggregation — GSI Dashboard.

Reads docs/ai-ops/token-burn-log.jsonl and produces:
  1. Per-sprint est-vs-actual summary table
  2. Per-model average accuracy ratio (actual/est)
  3. Per-mode efficiency (tokens per item)
  4. Overhead as % of total trend
  5. Waste rate by task outcome

Usage:
  python3 docs/ai-ops/analyze_token_burns.py              # full report
  python3 docs/ai-ops/analyze_token_burns.py --check      # parse-only, exit 0 if valid
  python3 docs/ai-ops/analyze_token_burns.py --sprint v5.38  # single sprint
"""
import json
import sys
import os
from collections import defaultdict
from typing import Optional


JSONL_PATH = os.path.join(os.path.dirname(__file__), "token-burn-log.jsonl")


def _parse_ktoken(s: Optional[str]) -> Optional[float]:
    """Convert '8k-12k' or '8k–12k' → midpoint 10.0, '22k' → 22.0, or None.
    Strips leading ~ and handles both hyphen (-) and en-dash (–) separators."""
    if s is None:
        return None
    s = str(s).strip().lower().lstrip("~").replace("k", "")
    # Normalise en-dash → hyphen
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    parts = s.split("-")
    try:
        nums = [float(p.strip()) for p in parts if p.strip()]
        return sum(nums) / len(nums) if nums else None
    except ValueError:
        return None


def _load(sprint_filter: Optional[str] = None):
    if not os.path.exists(JSONL_PATH):
        print(f"ERROR: {JSONL_PATH} not found.", file=sys.stderr)
        sys.exit(1)
    entries = []
    with open(JSONL_PATH) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"ERROR: line {lineno} is not valid JSON: {e}", file=sys.stderr)
                sys.exit(1)
            if sprint_filter and entry.get("sprint") != sprint_filter:
                continue
            entries.append(entry)
    return entries


def _sprint_table(entries):
    rows = []
    for e in entries:
        sprint = e.get("sprint", "?")
        methodology = e.get("actual_tokens_methodology", "?")
        items = e.get("items", [])
        n_items = len(items)
        n_done = sum(1 for it in items if it.get("actual_tokens") is not None)
        est = _parse_ktoken(e.get("totals", {}).get("est_tokens_sum"))
        actual = e.get("totals", {}).get("actual_tokens_sum")
        if isinstance(actual, str):
            actual = _parse_ktoken(actual)
        variance = e.get("totals", {}).get("variance_pct")
        date_closed = e.get("date_closed") or "open"
        rows.append((sprint, n_items, n_done, est, actual, variance, methodology, date_closed))

    print("## Per-sprint est-vs-actual summary")
    print(f"{'Sprint':<12} {'Items':<7} {'Done':<6} {'Est(k)':<9} {'Actual(k)':<11} {'Var%':<8} {'Method':<15} {'Status'}")
    print("-" * 80)
    for sprint, n, done, est, actual, var, method, status in rows:
        est_s = f"{est:.0f}" if est is not None else "—"
        actual_s = f"{actual:.0f}" if actual is not None else "—"
        var_s = f"{var}" if var is not None else "—"
        print(f"{sprint:<12} {n:<7} {done:<6} {est_s:<9} {actual_s:<11} {var_s:<8} {method:<15} {status}")
    print()


def _model_accuracy(entries):
    model_data = defaultdict(list)
    for e in entries:
        for it in e.get("items", []):
            model = it.get("model", "?")
            est = _parse_ktoken(it.get("est_tokens"))
            actual = it.get("actual_tokens")
            if est and actual and actual > 0:
                ratio = (actual / 1000.0) / est  # both in k now
                model_data[model].append(ratio)

    print("## Per-model accuracy ratio (actual / est midpoint)")
    print(f"{'Model':<10} {'N':<5} {'Avg ratio':<12} {'Notes'}")
    print("-" * 45)
    for model in ("haiku", "sonnet", "opus"):
        ratios = model_data.get(model, [])
        if ratios:
            avg = sum(ratios) / len(ratios)
            note = "over-est" if avg < 0.8 else ("under-est" if avg > 1.2 else "calibrated")
            print(f"{model:<10} {len(ratios):<5} {avg:<12.2f} {note}")
        else:
            print(f"{model:<10} {'0':<5} {'—':<12} no actuals yet")
    print()


def _mode_efficiency(entries):
    mode_data = defaultdict(list)
    for e in entries:
        for it in e.get("items", []):
            mode = it.get("mode", "?")
            actual = it.get("actual_tokens")
            if actual:
                mode_data[mode].append(actual / 1000.0)  # convert raw → k

    print("## Per-mode average tokens per item")
    print(f"{'Mode':<20} {'N':<5} {'Avg tokens(k)'}")
    print("-" * 42)
    for mode, vals in sorted(mode_data.items()):
        avg = sum(vals) / len(vals)
        print(f"{mode:<20} {len(vals):<5} {avg:.1f}k")
    if not mode_data:
        print("  (no actuals yet)")
    print()


def _overhead_trend(entries):
    print("## Overhead as % of total (trend)")
    print(f"{'Sprint':<12} {'Reg runs':<10} {'Sync':<7} {'Close':<7} {'Sum':<8} {'Total':<8} {'Overhead%'}")
    print("-" * 65)
    for e in entries:
        sprint = e.get("sprint", "?")
        oh = e.get("overhead", {})
        reg = oh.get("regression_runs_actual") or 0
        sync = oh.get("sync_docs_actual") or 0
        close = oh.get("sprint_close_actual") or 0
        oh_sum = reg + sync + close
        actual_total = e.get("totals", {}).get("actual_tokens_sum")
        if isinstance(actual_total, str):
            actual_total = _parse_ktoken(actual_total)
        if actual_total and actual_total > 0:
            pct = f"{oh_sum / actual_total * 100:.1f}%"
        else:
            pct = "—"
        print(f"{sprint:<12} {reg or '—':<10} {sync or '—':<7} {close or '—':<7} {oh_sum or '—':<8} {actual_total or '—':<8} {pct}")
    print()


def _waste_rate(entries):
    outcome_data = defaultdict(lambda: {"n": 0, "wasted": 0})
    for e in entries:
        for it in e.get("items", []):
            q = it.get("quality") or {}
            outcome = q.get("outcome") or "unknown"
            wasted = q.get("wasted_tokens_est") or 0
            outcome_data[outcome]["n"] += 1
            outcome_data[outcome]["wasted"] += wasted

    print("## Waste rate by outcome")
    print(f"{'Outcome':<20} {'N':<5} {'Total wasted(k)'}")
    print("-" * 38)
    for outcome in ("clean", "minor_rework", "major_rework", "unknown"):
        d = outcome_data.get(outcome, {"n": 0, "wasted": 0})
        print(f"{outcome:<20} {d['n']:<5} {d['wasted'] or '—'}")
    print()


def _variance_alerts(entries):
    """Scan entries for per-item and sprint-level token overruns.

    Per-item:  ⚠ OVER when actual > 1.5× est midpoint.
    Sprint:    ⚠ SPRINT OVER when total actual > 1.5× est (variance > +50%).
    Items and sprints with null actuals are skipped (open sprints).
    """
    any_alert = False
    print("## Variance alerts")

    for e in entries:
        sprint = e.get("sprint", "?")

        # Sprint-level check ───────────────────────────────────────────────────
        totals = e.get("totals", {})
        est_sum = _parse_ktoken(totals.get("est_tokens_sum"))
        raw_actual_sum = totals.get("actual_tokens_sum")
        if isinstance(raw_actual_sum, (int, float)):
            actual_sum_k = raw_actual_sum / 1000.0 if raw_actual_sum > 1000 else float(raw_actual_sum)
        else:
            actual_sum_k = _parse_ktoken(raw_actual_sum)

        if est_sum and actual_sum_k and actual_sum_k > 0:
            sprint_ratio = actual_sum_k / est_sum
            if sprint_ratio > 1.5:
                variance_pct = (sprint_ratio - 1.0) * 100
                print(f"⚠  SPRINT OVER: {sprint}  actual={actual_sum_k:.0f}k  "
                      f"est={est_sum:.0f}k  variance=+{variance_pct:.0f}%  ratio={sprint_ratio:.1f}×")
                any_alert = True

        # Per-item checks ──────────────────────────────────────────────────────
        for it in e.get("items", []):
            item_id = it.get("id", "?")
            est_mid = _parse_ktoken(it.get("est_tokens"))
            actual = it.get("actual_tokens")
            if est_mid is None or actual is None:
                continue  # skip null (open sprint items)
            actual_k = actual / 1000.0 if actual > 1000 else float(actual)
            ratio = actual_k / est_mid
            if ratio > 1.5:
                print(f"  ⚠ OVER  [{sprint}] {item_id:<32} "
                      f"actual={actual_k:.0f}k  est={est_mid:.0f}k  ratio={ratio:.1f}×")
                any_alert = True

    if not any_alert:
        print("  ✓ No overruns detected (all items and sprints within 1.5× estimate)")
    print()


def main():
    sprint_filter = None
    check_only = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--check":
            check_only = True
        elif args[i] == "--sprint" and i + 1 < len(args):
            sprint_filter = args[i + 1]
            i += 1
        i += 1

    entries = _load(sprint_filter)
    if not entries:
        print(f"No entries found{f' for sprint {sprint_filter}' if sprint_filter else ''}.")
        sys.exit(0)

    if check_only:
        print(f"OK — {len(entries)} sprint entr{'y' if len(entries) == 1 else 'ies'} parsed successfully.")
        sys.exit(0)

    label = f" (sprint: {sprint_filter})" if sprint_filter else f" ({len(entries)} sprints)"
    print(f"# Token Burn Analysis{label}\n")
    _sprint_table(entries)
    _variance_alerts(entries)
    _model_accuracy(entries)
    _mode_efficiency(entries)
    _overhead_trend(entries)
    _waste_rate(entries)


if __name__ == "__main__":
    main()

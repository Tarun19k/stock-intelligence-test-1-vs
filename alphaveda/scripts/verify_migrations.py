#!/usr/bin/env python3
"""G-MIG gate: verify all 13 AlphaVeda tables + critical columns exist on live Supabase.
Run before Phase 2. Exit 0 = all pass. Exit 1 = missing tables/columns.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

REQUIRED_TABLES = [
    "instruments", "ohlcv", "fundamentals", "macro_regime",
    "portfolio_buckets", "trade_outcomes", "accuracy_predictions",
    "accuracy_outcomes", "signal_weights", "ingest_status", "waitlist",
]

REQUIRED_COLUMNS = {
    "accuracy_predictions": ["downside_target"],       # migration 0012
    "ohlcv": ["circuit_flag", "deliverable_volume", "licence_class"],  # migration 0013
}


def main():
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print("FAIL: SUPABASE_URL or SUPABASE_SERVICE_KEY not set in .env")
        sys.exit(1)

    sb = create_client(url, key)
    failures = []

    for table in REQUIRED_TABLES:
        try:
            sb.table(table).select("*").limit(0).execute()
            print(f"  OK  {table}")
        except Exception as e:
            print(f"  FAIL {table}: {e}")
            failures.append(table)

    for table, cols in REQUIRED_COLUMNS.items():
        for col in cols:
            try:
                sb.table(table).select(col).limit(0).execute()
                print(f"  OK  {table}.{col}")
            except Exception as e:
                print(f"  FAIL {table}.{col}: {e}")
                failures.append(f"{table}.{col}")

    if failures:
        print(f"\nG-MIG FAIL — {len(failures)} missing: {failures}")
        print("Apply missing migrations via Supabase dashboard SQL editor before continuing.")
        sys.exit(1)
    else:
        print(f"\nG-MIG PASS — all {len(REQUIRED_TABLES)} tables + critical columns present")


if __name__ == "__main__":
    main()

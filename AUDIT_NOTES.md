# GSI v5.7 — Global Readability Audit Fix

## Scope
Scanned the full application for dark backgrounds missing explicit text colors.

## Fixed files
- app.py
- pages/dashboard.py
- pages/global_intelligence.py
- utils.py
- styles.py

## What was fixed
1. Selected ticker badge + empty ticker badge in sidebar
2. Dashboard KPI/signal dark badges
3. Global Intelligence dark cards / nodes / badges
4. Error log cards in utils.py
5. Global CSS defaults:
   - body / main text color
   - KPI cards
   - news cards
   - graph-help blocks

## Goal
Every dark-surface container now has an explicit readable foreground color
instead of inheriting theme defaults.

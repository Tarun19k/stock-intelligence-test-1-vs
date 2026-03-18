# GSI v5.15.2 — Known Issues Log + Regression Suite
Date: 2026-03-18

## What was added

  KNOWN_ISSUES_LOG.md
    14 internal issues (KI-001 to KI-014) documented with:
    symptom, root cause, fix applied, regression check added
    3 external/environment issues (EXT-001 to EXT-003)
    Every bug encountered since v1.0 is captured here.

  regression.py — standalone runnable validation suite
    Run: python regression.py  (from project root)
    166 checks across R1–R13 + R-ZIP categories
    Every check is KI-coded — traces back to the issue that taught it
    R-ZIP check: re-reads zip from disk after packaging (prevents KI-014)
    Suite is self-contained — no Streamlit, no yfinance dependency

## How to use
  Before every release:
    python regression.py           # against project files
  After packaging a zip:
    from regression import verify_zip
    verify_zip('GSI_vX.Y.zip')     # confirms fixes actually in zip

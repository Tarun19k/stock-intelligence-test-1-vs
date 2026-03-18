# GSI v5.8 — Version Sync

## Problem
VERSION_LOG in config.py was frozen at v5.0 (2026-03-14).
Seven patches had been applied in the current session with no log entry.
app.py had a hardcoded "v5.0" string in page_title that never updated.

## Fix
1. config.py — Added 7 missing VERSION_LOG entries (v5.1–v5.7)
   CURRENT_VERSION = VERSION_LOG[-1]["version"]  ← always latest automatically
2. app.py — page_title changed from hardcoded to dynamic:
   BEFORE:  page_title="Global Stock Intelligence v5.0"
   AFTER:   page_title=f"Global Stock Intelligence {CURRENT_VERSION}"

## Going forward
Every patch that changes app behaviour should add one entry to
VERSION_LOG in config.py.  CURRENT_VERSION updates automatically —
no other files need changing.

## Current version: v5.7
## Files changed: 2 (config.py, app.py)

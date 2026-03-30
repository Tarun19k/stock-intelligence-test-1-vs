# Changelog Post — GSI Dashboard

Generate user-facing release notes from version.py VERSION_LOG for each new version.

## When to run
After every sprint close, before or immediately after git push.
Generates: GitHub Release notes, Reddit sprint post, and CHANGELOG.md entry.

## Source of truth
`version.py` → `VERSION_LOG` — the single source of all version notes.
`sync_docs.py` auto-rebuilds `CHANGELOG.md` from this. Do not duplicate manually.

## Output formats

### GitHub Release (markdown)
```markdown
## GSI Dashboard v[X.XX] — [Date]

### What's new
[3-5 bullet points, user-facing language, no internal ticket IDs]

### Fixed
[Bug fixes visible to users]

### Technical
[Architecture changes relevant to developers/contributors]

### Disclaimer
Signal visualisation tool only. Not investment advice.
```

### Reddit sprint post (r/algotrading or personal dev log)
```
**GSI Dashboard v[X.XX] shipped**

[1 paragraph: what changed and why it matters to users]

**Signals working across:** India · USA · Europe · China · Commodities · ETFs
**Tickers:** 559 | **Regression:** 396/396 PASS | **Free:** Yes

[Link to dashboard]
[Link to GitHub]

*Educational tool — not investment advice*
```

### Version badge update
After every release, update README.md badge:
`![Version](https://img.shields.io/badge/version-v5.XX-blue)`
`sync_docs.py` handles this automatically — run it.

## Translation rules (internal → user-facing)
| Internal note | User-facing language |
|---|---|
| "OPEN-009: P(gain) neutral zone" | "Forecast now shows 'Insufficient signal' for borderline predictions" |
| "_is_rate_limited() gate added" | "Improved stability under heavy market data load" |
| "R23b regression checks" | (omit — internal) |
| "pandas 3.0 compatible" | "Improved compatibility with latest Python environment" |
| "SEBI disclaimer added" | "Added regulatory disclosure to all signal sections" |

## Never include in user-facing notes
- Internal ticket IDs (OPEN-XXX, RISK-XXX)
- Regression check counts
- yfinance version details
- "hotfix" framing (implies instability)
- Specific file names unless developer-facing post

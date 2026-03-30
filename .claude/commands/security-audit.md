# Security Audit — GSI Dashboard

Check for OWASP Top 10 vulnerabilities and GSI-specific security risks before any release.

## When to run
- Before every public release / MVP launch
- After any change to unsafe_allow_html f-strings (RISK-T09)
- After adding a new user-facing input (search box, text field)
- After adding any new external data source or RSS feed

## OWASP Top 10 checks for GSI

### A03 — Injection (highest risk for GSI)
Risk: f-strings with `{ticker}` or `{name}` in `unsafe_allow_html=True` blocks.
Check pattern:
```python
# UNSAFE — ticker from user input injected into HTML
st.markdown(f'<div>{ticker}</div>', unsafe_allow_html=True)

# SAFE — sanitised before injection
from utils import sanitise
st.markdown(f'<div>{sanitise(ticker, max_len=20)}</div>', unsafe_allow_html=True)
```
Grep for all `unsafe_allow_html=True` occurrences:
```bash
grep -n "unsafe_allow_html" pages/*.py dashboard.py app.py
```
Every match must either use `sanitise()` / `sanitise_bold()` or use only hardcoded strings.

### A01 — Broken Access Control
GSI is a public read-only app — no auth, no user data, no admin panel.
Risk: LOW. No session data that could be stolen. No write paths.

### A05 — Security Misconfiguration
Check:
- `.streamlit/secrets.toml` in .gitignore ✅ (already confirmed)
- No API keys in source code (grep for `sk-`, `Bearer `, hardcoded URLs)
- `ANTHROPIC_API_KEY` only via `st.secrets["ANTHROPIC_API_KEY"]` — never hardcoded

### A06 — Vulnerable Components
Check `requirements.txt` against known CVEs before any release:
```bash
pip-audit  # or: safety check
```

### A07 — Identification and Authentication Failures
GSI has no auth — not applicable. If auth added in v2+, re-run full A07 check.

### A08 — Software and Data Integrity
RSS feeds: verify all domains are in `_ALLOWED_RSS_DOMAINS` before fetch.
No dynamic code execution from external sources.

### A10 — Server-Side Request Forgery (SSRF)
RSS feed fetching in `market_data.py`:
- `_ALLOWED_RSS_DOMAINS` allowlist is the mitigation.
- Never fetch from user-supplied URLs.
- New RSS domains require allowlist addition (scoped rule in `.claude/rules/market-data.md`).

## GSI-specific checks

### XSS via ticker/name injection (RISK-T09 — open)
```bash
# Find all unsafe_allow_html usages
grep -rn "unsafe_allow_html" . --include="*.py" | grep -v "test\|#"
```
For each: confirm the variable in the f-string is sanitised.
RISK-001 in backlog — this is the key open security risk.

### Dependency supply chain
Before adding any new package:
1. Check PyPI download count (low count = higher risk)
2. Check last release date (unmaintained = higher risk)
3. Add to GSI_DEPENDENCIES.md

## Security audit output
After running checks, update `GSI_RISK_REGISTER.md`:
- Mark RISK-T09 as Mitigated when sanitise() covers all unsafe_allow_html paths
- Add any new risks discovered during audit

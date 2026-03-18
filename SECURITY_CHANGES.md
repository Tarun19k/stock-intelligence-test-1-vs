# Security Hardening — GSI v5.0
## 4 files updated. Replace in repo root.
| Layer | Function | Blocks |
|---|---|---|
| XSS | sanitise() in utils.py | HTML injection via names/titles/news |
| Key injection | safe_ticker_key() | Path/JSON key manipulation |
| SSRF | safe_url() + _is_allowed_rss() | Internal network via RSS URLs |
| Secrets | Validation scan | API keys/passwords in source |
| RCE | Validation scan | eval(), exec(), os.system() |
| Rate abuse | _throttle() | yfinance 429 / DoS |
| Supply chain | Pinned requirements.txt | Auto-upgrade to vulnerable versions |

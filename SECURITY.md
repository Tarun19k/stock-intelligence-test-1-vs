# Security Policy — GSI Dashboard

## Data & Privacy

**No user data is collected or stored.**
- No authentication. No user accounts. No login.
- No personally identifiable information is captured at any point.
- Session state (forecast history, UI preferences) exists only in browser memory
  for the duration of a session and is discarded on close or redeploy.
- No cookies beyond those set by Streamlit's own session management.

**No secrets or API keys.**
- All market data is fetched from Yahoo Finance's public, unauthenticated endpoints via `yfinance`.
- All news is fetched from public RSS feeds.
- No API keys exist in this repository. `secrets.toml` is gitignored.

## Data Sources

| Source | Type | Authentication | Terms |
|---|---|---|---|
| Yahoo Finance (via yfinance) | Market prices, fundamentals | None — public endpoint | Yahoo Finance ToS |
| RSS feeds (Al Jazeera, Reuters, BBC, TOI, ET) | News headlines | None — public feeds | Respective publisher ToS |

Yahoo Finance data is intended for personal and educational use. Do not use this
application for commercial data redistribution.

## Regulatory Disclaimer

This application is a personal financial intelligence tool built for informational
and educational purposes. It is not a registered investment advisor, broker, or
financial service.

- All signals (BUY/WATCH/AVOID) are algorithmically generated from quantitative
  technical indicators. They are not human analyst opinions.
- This application makes no guarantee of accuracy, completeness, or timeliness
  of any data displayed.
- Nothing on this platform constitutes financial advice. Consult a SEBI-registered
  investment advisor before making investment decisions.
- Past performance displayed is not indicative of future results.

## Known Limitations

- **Rate limiting:** Yahoo Finance applies rate limits from datacenter IPs.
  During high-traffic periods, some data may be delayed or unavailable.
  The application handles this gracefully with stale-data fallbacks.
- **Data accuracy:** Fundamental data (P/E, ROE, P/B) for Indian stocks
  (NSE/BSE) is inconsistently available via yfinance and may show N/A.
- **Ephemeral storage:** Forecast history and any session data is lost
  on browser close or application redeploy.

## Reporting Issues

This is a private repository. To report a data accuracy issue, security
concern, or compliance gap, open a GitHub Issue using the `audit_report`
template or contact the repository owner directly.

**Do not** open public issues containing personal data, API credentials,
or specific vulnerability exploit details.

## Deployment Security

- Deployed on Streamlit Community Cloud (Snowflake infrastructure).
- No custom server, no database, no persistent backend.
- All processing is stateless and session-scoped.
- The application does not execute user-provided code.
- XSS mitigations: all user-facing content is passed through `sanitise()`
  and `sanitise_bold()` before rendering in `unsafe_allow_html` blocks.

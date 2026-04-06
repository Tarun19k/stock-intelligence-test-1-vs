# GSI_RISK_REGISTER.md — Risk Register
# Version: v1.0 | Created: 2026-03-31
# Append new risks below. Update Status column only — never delete records.

---

## Format
`| ID | Category | Description | Likelihood | Impact | Status | Mitigation |`

---

## Technical Risks

| ID | Category | Description | Likelihood | Impact | Status | Mitigation |
|---|---|---|---|---|---|---|
| RISK-T01 | Data | yfinance 429 rate limit under concurrent users | High | High | Mitigated | Token bucket + global cooldown gate (_is_rate_limited). Chunk=3, 5s gap, 10s backoff. |
| RISK-T02 | Infrastructure | Streamlit Cloud 1GB RAM breach under load | Med | High | Open | Module-level cache + lazy loading reduces baseline. Memory profile before launch. |
| RISK-T03 | Data | yfinance API schema change (MultiIndex, column renames) | Med | High | Mitigated | GSI_DEPENDENCIES.md C-003: `df['Close'].iloc[:,0]` guard. regression.py R3 catches bad data. |
| RISK-T04 | Infrastructure | App sleeps after 12h inactivity (free tier) | High | Low | Accepted | Acceptable for MVP. Document in README. Cold start <15s acceptable. |
| RISK-T05 | Data | yfinance returns stale/incorrect data for non-US markets | Med | Med | Open | No current validation layer. Future: DataManager M2 DataContract validator (OPEN-007). |
| RISK-T06 | Infrastructure | Forecast session state lost on Streamlit redeploy | High | Med | Accepted | By design — filesystem storage prohibited (Hard Rule 1). Users aware forecasts are session-only. |
| RISK-T07 | Dependency | pandas/Streamlit version incompatibility on upgrade | Med | High | Mitigated | GSI_DEPENDENCIES.md pins. regression.py catches breaking changes. |
| RISK-T08 | Data | Single data source (yfinance) — no fallback | High | High | Open | OPEN-007 DataManager M2 will add fallback. Until then: stale fallback via _ticker_cache. |
| RISK-T09 | Security | XSS via unsanitised {ticker}/{name} in unsafe_allow_html | Med | Med | Mitigated | sanitise()/safe_url() — v5.33: all RSS output in home.py + global_intelligence.py sanitised. safe_ticker_key() before all yf calls. |
| RISK-T10 | Infrastructure | Cold start latency spike after 12h sleep | High | Low | Accepted | Warmth guard defers heavy fetches. Document expected behaviour. |

---

## Legal & Regulatory Risks

| ID | Category | Description | Likelihood | Impact | Status | Mitigation |
|---|---|---|---|---|---|---|
| RISK-L01 | Regulatory | SEBI: displaying BUY/WATCH/AVOID signals without registration | High | Critical | Mitigated | All signal sections have SEBI disclaimer. Framed as "educational signal visualisation". No target prices or entry/exit levels. regression.py R17 enforces disclaimer presence. |
| RISK-L02 | Legal | Yahoo Finance ToS: prohibits data redistribution and commercial use | High | Critical | Accepted (MVP) | Educational framing + disclaimer. "Not for commercial use" label. For commercial launch, must switch to licensed data source (Polygon.io, Quandl). |
| RISK-L03 | Regulatory | yfinance: not endorsed/licensed by Yahoo — research/education only | High | Med | Accepted | yfinance disclaimer in app + docs. Explicit "educational only" framing. |
| RISK-L04 | Regulatory | SEBI Finfluencer rules: social media posts about the tool | Med | High | Mitigated | docs/social-media-guidelines.md created v5.35. Rules: no live signal screenshots, "developer sharing a tool" framing only, no BUY/SELL/target prices in posts. Platform-specific rules for Reddit/PH/Twitter/LinkedIn. |
| RISK-L05 | Privacy | GDPR: analytics data if EU users visit | Low | Med | Open | streamlit-analytics uses no PII. No cookies. If adding Claude API, check Anthropic data processing terms. |
| RISK-L06 | Legal | Open source licence: ensure all dependencies are compatible | Low | Med | Open | Apache 2.0 + MIT dependencies. cvxpy is Apache 2.0. Check before adding new packages. |

---

## Product Risks

| ID | Category | Description | Likelihood | Impact | Status | Mitigation |
|---|---|---|---|---|---|---|
| RISK-P01 | UX | Users misinterpreting educational signals as investment advice | High | Critical | Mitigated | SEBI disclaimer on every signal section. "Educational only" on every page. HELP tooltips explain each signal. |
| RISK-P02 | Product | Feature creep delaying MVP launch | High | Med | Open | /mvp-scope command defines hard in/out scope. Max 9 items per sprint rule enforced. |
| RISK-P03 | Data | Users trust signal accuracy without understanding limitations | Med | High | Partial | HELP_TEXT explains methodology. Forecast accuracy tab shows historical calibration. Needs stronger "data limitations" section. |
| RISK-P04 | Growth | Low user retention due to app sleep (12h free tier) | Med | Med | Accepted | Document sleep behaviour. Consider UptimeRobot ping to keep app warm (check ToS). |
| RISK-P05 | Product | Single developer — no coverage if unavailable | High | Med | Accepted | regression.py + GSI_WIP.md CHECKPOINT protocol reduces bus factor for context. |
| RISK-P06 | Growth | Product Hunt launch fails to drive traffic | Med | Low | Open | Backup: Reddit + HN organic posts don't depend on PH success. |

---

## Operational Risks

| ID | Category | Description | Likelihood | Impact | Status | Mitigation |
|---|---|---|---|---|---|---|
| RISK-O01 | Monitoring | No alerting on production errors | High | Med | Open | streamlit-analytics captures some errors. Add error tracking (Sentry free tier?) for v1.1. |
| RISK-O02 | Context | GSI_session.json becomes stale — context loss between sessions | Med | Med | Mitigated | generate_context.py auto-regenerates GSI_CONTEXT.md on clean regression. Claude Code memory system added 2026-03-31. |
| RISK-O03 | Deployment | Streamlit Cloud deploy fails silently | Low | High | Open | Monitor deploy logs manually post-push. Add GitHub Actions status badge to README. |
| RISK-O04 | Data | RSS feed domains go stale / change URL | Med | Low | Mitigated | _ALLOWED_RSS_DOMAINS allowlist. TechCrunch removed v5.31. Regular feed validation needed. |

---

## Risk Summary Dashboard

| Status | Count |
|---|---|
| Open | 8 |
| Mitigated | 10 |
| Accepted | 6 |
| Closed | 0 |
| **Total** | **24** |

**Critical open risks:** RISK-L02 (Yahoo ToS for commercial use), RISK-P01 (signal misinterpretation)
**Highest priority to close before MVP launch:** RISK-T02 (RAM), RISK-L04 (social media posts)

---

## Version History

| Version | Date | Notes |
|---|---|---|
| v1.0 | 2026-03-31 | Initial register — 24 risks across 4 categories. Established from research + audit history. |

# Risk Register — GSI Dashboard

Surface, assess, and track risks across technical, legal, product, and operational dimensions.

## How to use
Run /risk-register to review and update the full risk register in GSI_RISK_REGISTER.md.
When a new risk is identified during development, add it immediately.
Risks are in GSI_RISK_REGISTER.md — this command is the workflow guide.

## Risk assessment framework
- **Likelihood**: Low / Med / High
- **Impact**: Low / Med / High / Critical
- **Status**: Open / Mitigated / Accepted / Closed

## Risk categories to always check

### Technical risks
- yfinance rate limits under concurrent users
- Streamlit Cloud 1GB RAM breach
- yfinance API schema changes (MultiIndex, column renames)
- pandas/Streamlit version incompatibility
- Cold start latency (12h sleep on free tier)
- Forecast session state loss on Streamlit redeploy

### Legal/regulatory risks
- SEBI: displaying signals without registration
- Yahoo Finance ToS: data redistribution prohibition
- yfinance: commercial use restriction
- GDPR/privacy: analytics data if EU users visit
- Finfluencer rules: social media posts about the tool

### Product risks
- Feature creep delaying MVP launch
- Users misinterpreting educational signals as advice
- Overreliance on yfinance (single data source)
- No auth means no personalisation path to monetise

### Operational risks
- Streamlit Cloud app sleeping during key market hours
- No monitoring/alerting on production errors
- Single developer — no bus factor mitigation
- GSI_session.json becoming the single point of context failure

## When adding a new risk
Format for GSI_RISK_REGISTER.md:
```
| RISK-NNN | Category | Description | Likelihood | Impact | Status | Mitigation |
```
Also add to open_items in GSI_session.json if actionable.

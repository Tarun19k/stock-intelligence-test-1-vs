# Claude API Integration — GSI Dashboard

Guide for integrating Claude API into GSI for AI narrative generation (OPEN-018).

## Project context
- Language: Python 3.14
- Existing AI narrative: rule-based text in `_tab_insights()` in `pages/dashboard.py`
- Target: replace/augment with Claude-generated sector narrative consuming same indicator data
- Constraint: Streamlit Cloud free tier — minimize API call frequency, use caching

## Model defaults for GSI
- **Narrative generation:** `claude-haiku-4-5` (low latency, low cost, adequate for summaries)
- **Complex analysis:** `claude-sonnet-4-6` (sector breadth, multi-stock comparison)
- **Never use Opus** for real-time dashboard calls — too slow and expensive

## Install
```bash
pip install anthropic
```
Add to `requirements.txt`.

## Basic pattern for GSI
```python
import anthropic
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def generate_stock_narrative(ticker, indicators, verdict):
    prompt = f"""
    Stock: {ticker}
    Verdict: {verdict}
    RSI: {indicators['rsi']:.1f}
    MACD signal: {indicators['macd_signal']}
    Weinstein Stage: {indicators['stage']}

    Write 2 sentences of plain-English technical analysis for a retail investor.
    Do not give buy/sell advice. Label output as algorithmically generated.
    """
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

## Caching strategy
Wrap with `@st.cache_data(ttl=3600)` — narrative doesn't need to refresh more than hourly.
Never call on every rerun — gate behind a "Generate AI Summary" button.

## Streamlit Cloud deployment
Set `ANTHROPIC_API_KEY` in Streamlit Cloud secrets (`.streamlit/secrets.toml` locally, never commit).
```toml
# .streamlit/secrets.toml (gitignored)
ANTHROPIC_API_KEY = "sk-ant-..."
```
Access in code: `st.secrets["ANTHROPIC_API_KEY"]`

## Regulatory requirement
Every Claude-generated narrative MUST be labeled:
> "This analysis is algorithmically generated and does not constitute investment advice."

This is a P0 requirement (GSI_GOVERNANCE.md Policy 4).

## Sector breadth narrative (OPEN-018 full fix)
Feed `signal_score()` results for all tickers in a group into a single prompt.
Summarise breadth: % BUY / WATCH / AVOID by group. One Claude call per group per hour max.

# Export to Excel — GSI Dashboard

Generate downloadable Excel reports from stock data, portfolio allocator results, and weekly summaries.

## Dependencies
```
openpyxl>=3.1.0   # formulas + formatting
pandas>=1.4.0     # already in requirements.txt
xlsxwriter        # alternative for charts-in-Excel
```

## GSI export targets
1. **Stock snapshot** — ticker, verdict, KPIs, RSI, MACD, Weinstein stage
2. **Portfolio allocator output** — weights, CVaR, expected return, stress flags
3. **Weekly group summary** — 5d returns heatmap for all tickers in a group
4. **Watchlist export** — GI page watchlist with live prices

## Streamlit download pattern
```python
import io
from openpyxl import Workbook

def build_stock_export(ticker, info, df, verdict):
    wb = Workbook()
    ws = wb.active
    ws.title = ticker
    # headers in row 1, data in row 2
    # Blue text = user-editable inputs, black = calculated
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

st.download_button(
    label="📥 Export to Excel",
    data=build_stock_export(...),
    file_name=f"{ticker}_GSI_{date}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

## Formatting standards (from GSI_SKILLS.md)
- Blue text = hardcoded inputs
- Black text = formulas/calculated values
- No hardcoded numbers in formula cells — reference data cells
- Negative numbers in parentheses, zeros as "-"
- Always include "Educational use only — not investment advice" in A1

## Never
- Never export raw Momentum score as a recommendation
- Never include SEBI-triggering language ("buy this stock")
- Never commit generated .xlsx files to git

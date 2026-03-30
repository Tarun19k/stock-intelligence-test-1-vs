# Export to PDF — GSI Dashboard

Generate downloadable PDF reports: stock analysis, weekly summaries, portfolio reports.

## Dependencies
```
reportlab>=4.0.0   # create PDFs from scratch
pdfplumber         # extract/read existing PDFs if needed
```

## GSI report types
1. **Stock analysis report** — 1-page: verdict, KPI panel, chart snapshot, AI narrative
2. **Weekly market summary** — group heatmap, top movers, index performance
3. **Portfolio allocation report** — weights, CVaR, efficient frontier description

## Streamlit download pattern
```python
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def build_stock_pdf(ticker, name, verdict, summary_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"GSI Dashboard — {name} ({ticker})", styles['Title']),
        Paragraph(f"Signal: {verdict}", styles['Heading2']),
        Spacer(1, 12),
        Paragraph(summary_text, styles['Normal']),
        Spacer(1, 20),
        Paragraph(
            "DISCLAIMER: This report is for educational purposes only and does not "
            "constitute investment advice. Not SEBI-registered.",
            styles['Italic']
        ),
    ]
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

st.download_button("📄 Export PDF", data=build_stock_pdf(...), file_name=f"{ticker}.pdf")
```

## Critical: reportlab Unicode warning
Do NOT use Unicode subscript/superscript characters — they render as solid black boxes.
Use XML markup instead: `<sub>2</sub>`, `<super>2</super>`.

## Mandatory disclaimer on every PDF
"For educational purposes only. Not investment advice. Not SEBI-registered.
Data sourced from Yahoo Finance via yfinance. Verify before making any financial decision."

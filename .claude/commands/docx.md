# DOCX Export — GSI Dashboard

Generate Word document reports from stock analysis, portfolio results, and compliance documentation.

## When to use
- Exporting a stock analysis report in Word format for sharing
- Generating compliance documentation (SEBI disclaimer package, regulatory audit trail)
- Creating QA test briefs in a shareable format
- Producing investor-ready reports from portfolio allocator output

## GSI document types

### Stock Analysis Report (.docx)
Contents: Ticker + verdict banner, KPI table, Weinstein Stage explanation, Elder Triple Screen
result, AI narrative (if enabled), mandatory disclaimer block.

### Compliance Report (.docx)
Contents: SEBI disclaimer text, algorithmic disclosure, data source attribution,
date/version stamp, "Not for redistribution" header.

## Dependencies
```bash
npm install docx  # JavaScript/Node approach (recommended)
# OR
pip install python-docx  # Python approach
```

## Critical docx-js rules (from skill spec)
- Set page size explicitly: US Letter = 12,240 × 15,840 DXA. Never rely on defaults.
- Use Arial font for universal compatibility across Word versions.
- Never use Unicode bullet characters — use `LevelFormat.BULLET` numbering config.
- Tables: use `WidthType.DXA` not `WidthType.PERCENTAGE` (breaks in Google Docs).
- Page breaks go inside Paragraph children, never as standalone elements.
- Heading styles: override using exact IDs ("Heading1", "Heading2") with `outlineLevel`.

## Mandatory content on every GSI document
```
DISCLAIMER: This document is produced by the Global Stock Intelligence Dashboard
for educational purposes only. It does not constitute investment advice, financial
recommendations, or guidance to buy, sell, or hold any security. The GSI Dashboard
is not registered with SEBI, SEC, FCA, or any other regulatory body. Data is sourced
via yfinance from Yahoo Finance and is subject to Yahoo Finance Terms of Service.
Verify all data independently before making any financial decision.
```

## Editing existing .docx files
1. Unpack: extract ZIP → edit XML in word/directory
2. Use Edit tool for string replacement (never rewrite full XML)
3. Repack: validate + zip back to .docx
4. Smart quotes: use entities (&#x2018; &#x2019; &#x201C; &#x201D;)

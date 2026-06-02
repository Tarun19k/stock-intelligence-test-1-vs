# Tickertape.in \- Minimum Required Data Reference

# 1\. Document Purpose

This document defines the minimum set of publicly available data fields to be extracted from Tickertape.in for equity research and stock analysis purposes. It contains NO personally identifiable information (PII). All fields listed in Section 3 are open market data. Fields in Section 4 require explicit user approval before extraction or inclusion, as they may identify specific entities or contain proprietary information.

# 2\. Data Classification Framework

GREEN \- Auto-Extract (No Approval Needed): Public market data with no entity identification. Safe to pull and use directly.  
RED \- Approval Required: Data that identifies specific individuals, named entities, or contains attributed proprietary analysis. Must be reviewed and approved by the user before extraction.

# 3\. AUTO-EXTRACT Fields (GREEN \- No Approval Required)

## 

​​- Stock Symbol / Ticker (e.g., RELIANCE, INFY)  
\- Stock Name (Company Name)  
\- Exchange Listed On (NSE / BSE)  
\- Sector  
\- Industry / Sub-industry  
\- Market Capitalization Category (Large Cap / Mid Cap / Small Cap)  
\- ISIN Code

## 3.2 Price & Market Data

\- Current Market Price (CMP)  
\- Day's Change (INR and %)  
\- 52-Week High  
\- 52-Week Low  
\- All-Time High (ATH)  
\- Day's Volume (shares traded)  
\- Delivery Volume (%)  
\- Market Capitalization (INR Cr)  
\- Free Float Market Cap  
\- Circuit Limit (Upper / Lower %)  
\- Beta (1Y)

## 3.3 Valuation Ratios

\- Price to Earnings (P/E) Ratio  
\- Price to Book (P/B) Ratio  
\- EV/EBITDA  
\- Price to Sales (P/S) Ratio  
\- Earnings Per Share (EPS) \- TTM  
\- Enterprise Value (EV)  
\- PEG Ratio (if available)

## 3.4 Profitability & Financial Health

## ​​3.5 Dividends

\- Dividend Yield (%)  
\- Dividend Per Share (DPS)  
\- Dividend Payout Ratio (%)  
\- Ex-Dividend Date  
\- Dividend History (aggregated, no named recipients)

## 3.6 Stock Scorecard / Health Score

\- Tickertape Scorecard Score (out of 10\)  
\- Solvency Score  
\- Growth Score  
\- Profitability Score  
\- Entry Point / Valuation Score  
\- Performance Score (1M, 3M, 6M, 1Y, 3Y, 5Y returns)

## 3.7 Analyst Ratings (Aggregated Only)

\- Total Number of Analysts Covering the Stock  
\- Number of Buy Recommendations  
\- Number of Hold Recommendations  
\- Number of Sell Recommendations  
\- Consensus Rating (Buy / Hold / Sell)  
\- Aggregated Consensus Target Price (INR) \- average, no individual attribution  
Note: Individual analyst names, firm names, and individual target prices are NOT included here. See Section 4\.

# 4\. APPROVAL-REQUIRED Fields (RED \- User Must Approve)

The following data types from Tickertape.in are classified as sensitive because they identify specific named entities (companies, funds, individuals), or contain proprietary attributed analysis. These must NOT be extracted automatically. A request must be raised to the user and explicit approval obtained before any such data is pulled or stored.

## 4.1 Insider Trading Data

\- Party Name (Insider / Promoter Name) \[APPROVAL REQUIRED\]  
\- Category of Insider (Promoter / KMP / Director) \[APPROVAL REQUIRED\]  
\- Transaction Type (Buy / Sell)  
\- Date of Transaction  
\- Quantity Traded  
\- Average Trade Price (INR)  
\- Value Traded (INR)  
\- Holdings Change (%)  
Note: Transaction type, date, quantity, and price are extractable only with approval, as they are linked to named parties.

## 4.2 Bulk & Block Deals

\- Buying / Selling Entity Name \[APPROVAL REQUIRED\]  
\- Deal Type (Bulk / Block)  
\- Exchange  
\- Quantity  
\- Trade Price (INR)  
\- Deal Value (INR)  
\- Date of Deal

## 4.3 Shareholding Pattern (Named Entity Level)

\- Promoter Names and Individual Holding % \[APPROVAL REQUIRED\]  
\- Named FII / DII Entities and their Stake % \[APPROVAL REQUIRED\]  
\- Named Mutual Fund Holdings \[APPROVAL REQUIRED\]  
Note: Aggregated promoter %, public %, FII %, DII % WITHOUT individual entity names are in Section 3 and are safe to extract.

## 4.4 Individual Analyst Reports & Target Prices

\- Analyst Name \[APPROVAL REQUIRED\]  
\- Brokerage / Research Firm Name \[APPROVAL REQUIRED\]  
\- Individual Analyst Target Price \[APPROVAL REQUIRED\]  
\- Individual Report Date \[APPROVAL REQUIRED\]  
\- Individual Report Rating (Buy / Hold / Sell per analyst) \[APPROVAL REQUIRED\]  
Note: These are proprietary and attributed. Aggregated versions (counts and average) are in Section 3.7.

## 4.5 Peer / Competitor Names

\- Named Peer Companies from Tickertape peer comparison feature \[APPROVAL REQUIRED\]  
Note: Peer financial ratios and metrics (unnamed, sector-average) are safe to extract without approval.

# 5\. Data Usage Rules

1\. All GREEN (Section 3\) fields may be extracted automatically from Tickertape.in for any listed Indian equity.  
2\. All RED (Section 4\) fields must trigger an approval request to the user before any data is pulled, stored, or displayed.  
3\. No PII data (names of individuals, home addresses, personal contact information) shall be extracted under any circumstance.  
4\. Data extracted under this framework is for internal analysis and research only.  
5\. This document applies to the Tickertape.in platform only. Different rules may apply to other data sources.  
6\. Data freshness: All extracted data should be timestamped with the date and time of extraction.  
7\. This document is version-controlled. Any changes to the classification of fields require a new version with user sign-off.

# 6\. Document Metadata

\- Document Title: Tickertape.in \- Minimum Required Data Reference  
\- Version: 1.0  
\- Created: May 16, 2026  
\- Classification: Internal \- Research Use Only  
\- Contains PII: NO  
\- Data Source: Tickertape.in (Anchorage Technologies Private Limited)  
\- Platform Scope: Indian Equities (NSE / BSE)  
\- Review Cadence: Quarterly or upon platform changes  

# MCP Server Builder — GSI Dashboard

Build a Model Context Protocol server to expose GSI signals and market data to AI assistants.

## What this enables
Users can query Claude (or any MCP-compatible AI) directly:
- "What's the Weinstein Stage for RELIANCE.NS?"
- "Show me BUY signals in the Nifty 50 group today"
- "Compare Elder Triple Screen results for AAPL vs MSFT"

## Architecture decision
GSI MCP server = read-only wrapper around existing market_data.py + indicators.py.
No new data fetching logic — reuse existing rate-limited, cached functions.

## Recommended stack
TypeScript (strong SDK support) with Streamable HTTP transport for remote access.
Python FastMCP is acceptable alternative since GSI is Python-native.

## Core tools to expose

```typescript
// Tool: get_signal
// Input: { ticker: string, market: string }
// Output: { verdict: "BUY"|"WATCH"|"AVOID", reason: string, stage: number, score: number }

// Tool: get_group_signals
// Input: { market: string, group: string }
// Output: { tickers: Array<{ticker, verdict, score}>, breadth: {buy_pct, watch_pct, avoid_pct} }

// Tool: get_market_status
// Input: { market: string }
// Output: { is_open: boolean, country: string, next_open: string }

// Tool: list_markets
// Output: { markets: string[], total_tickers: number }
```

## Rate limiting constraint
MCP server MUST respect existing _is_rate_limited() gate.
Never bypass the token bucket — MCP calls go through market_data.py functions.
Add per-tool TTL caching at MCP layer (signals TTL=300s, live price TTL=5s).

## Deployment
- Local: stdio transport — `mcp-server-gsi` runs alongside Streamlit app
- Remote (future): Streamable HTTP on separate endpoint

## Development phases
1. **MVP**: 4 read-only tools (get_signal, get_group_signals, get_market_status, list_markets)
2. **v2**: Forecast queries, portfolio allocator access
3. **v3**: Write tools (store forecast, add to watchlist) — requires auth

## Testing
Use MCP Inspector for validation.
Create 10+ eval queries covering: Indian tickers, US tickers, group breadth, market status, edge cases (delisted ticker, market closed).

## Legal note
MCP server exposes yfinance data. Same ToS constraints apply — educational/personal use only.
Do not expose MCP server publicly without proper data licensing.

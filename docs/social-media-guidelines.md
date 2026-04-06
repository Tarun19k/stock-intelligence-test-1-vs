# GSI Dashboard — Social Media Guidelines

**Version:** v5.35  
**Date:** 2026-04-06  
**Purpose:** Mitigate RISK-L04 — SEBI Finfluencer Rules. Applies to all public posts, shares, and promotional content about the GSI Dashboard by any team member or contributor.

---

## Section 1 — Approved Content

What is safe to share publicly:

- **Tool architecture and methodology diagrams** — screenshots of the signal framework explanation (Weinstein stages, Elder screens, MACD logic) with no live ticker data visible.
- **Anonymised or historical examples** — screenshots using well-known historical events (e.g., a 2020 crash example) where the outcome is already public knowledge. Never use today's live data.
- **Portfolio allocation theory** — Mean-CVaR framework explanation, risk/return scatter charts with synthetic or clearly labeled demo data.
- **Developer progress updates** — "Built X feature this week", architecture decisions, tech stack choices, UI/UX improvements.
- **Demo-mode screenshots** — a dedicated demo ticker (e.g., a synthetic or clearly-labeled placeholder) that does not reflect any live signal.
- **Open-source methodology references** — links to academic papers or public sources that underpin the indicators used.

**Approved caption framing:**
> "I built a tool that applies [X methodology] to stock data — here's how the signal framework works."  
> "Sharing a developer update: the dashboard now shows [feature]. Educational project, not investment advice."

---

## Section 2 — Prohibited Content

Never share the following in any public post, comment, DM, or community thread:

- **Live BUY/WATCH/AVOID signals for any specific ticker.** Example of what is prohibited: "RELIANCE.NS is showing a BUY signal right now on GSI." This constitutes a specific investment recommendation under SEBI finfluencer rules regardless of any disclaimer.
- **Screenshots showing a named live ticker with its current signal verdict.** Even if cropped, a visible ticker + signal combination is prohibited.
- **Any target price, entry level, or exit level** — even framed as "the tool calculates X". Publishing a model output that implies a price target triggers SEBI's unregistered investment advisor rules.
- **Screenshots with yfinance price labels on live data.** This also risks violating Yahoo Finance ToS (RISK-L02) which prohibits redistribution of price data.
- **Statements implying the tool is profitable or has generated returns.** Example: "GSI predicted the NIFTY rally." Backtests are private until independently audited.
- **Endorsements or testimonials framed as "this tool made me money."** Prohibited under SEBI, SEC, and FCA rules.
- **Any claim that signals constitute "research" in the SEBI-registered sense.** GSI is an educational tool, not a SEBI-registered research analyst product.

---

## Section 3 — Platform-Specific Rules

### Reddit (r/IndiaInvestments, r/Stocks, r/algotrading, etc.)
- Post category: developer sharing a self-built tool. Use the "Tool" or "Discussion" flair where available.
- Do not post in threads asking "what should I buy?" or "is [stock] a good investment?" — replying with GSI signal output in this context is a finfluencer act.
- If asked "what does your tool say about X?", respond with: "I can't share live signals publicly — the tool is for personal educational use. Happy to discuss the methodology."
- Include the standard disclaimer in the first comment: "Educational tool. Not investment advice. I am not a SEBI-registered investment advisor."

### Product Hunt
- Tagline must not mention "signals", "alerts", or "buy/sell". Use: "Multi-market stock analysis dashboard for independent learners."
- Gallery screenshots: methodology diagrams and UI only — no live ticker signals.
- The "Makers" comment must include the SEBI disclaimer and global regulatory note.

### Twitter/X
- Threads about methodology, architecture, or feature releases are approved.
- Never quote-tweet a market news story alongside a signal output, even implicitly.
- Do not participate in $TICKER cashtag threads where the context is trading decisions.

### LinkedIn
- Developer narrative posts are approved: "Built this dashboard over 6 months — here's what I learned about rate limiting / signal design / etc."
- Do not tag financial influencers or investment firms in posts showing signal outputs.
- The post must not appear in LinkedIn's "Financial Advice" content category — frame it under "Software Development" or "Data Science."

---

## Section 4 — SEBI Finfluencer Rules

SEBI's finfluencer circular (SEBI/HO/OIAE/OIAE_IAD-1/P/CIR/2023/0131, August 2023) applies to anyone who publishes content about securities on social media, regardless of whether they are registered or charging fees.

Key obligations that apply to GSI:

- **Registration threshold:** SEBI does not exempt free tools. Publishing live BUY/WATCH/AVOID signals for Indian listed securities (NSE/BSE tickers) on any public platform — including Reddit, Twitter, YouTube, WhatsApp groups — constitutes unregistered investment advisory activity.
- **"Educational" framing is necessary but not sufficient.** The content of each post is evaluated, not just the disclaimer. A post showing "INFY.NS: BUY" with a disclaimer does not become compliant.
- **Association prohibition:** SEBI-registered entities (brokers, RIAs) may not associate with unregistered finfluencers. Do not partner with or accept sponsorship from registered entities until GSI's regulatory posture is formally reviewed.
- **Permitted content under SEBI:** Explaining how a publicly documented methodology (RSI, MACD, Weinstein stages) works in general terms, without applying it to a specific live security on a public channel.
- **Enforcement risk:** SEBI has issued show-cause notices to tool builders whose dashboards were shared publicly even without explicit "buy this stock" language. The combination of live data + signal verdict + public post is the trigger.

For global users sharing about GSI:
- **SEC (USA):** Investment advisor registration triggered by managing or advising others on securities. Sharing a methodology tool is generally lower risk, but publishing live signals for US tickers publicly is a gray area under the Investment Advisers Act.
- **MiFID II / FCA (UK/EU):** "Investment research" definition is broad. Same precautions apply — methodology posts are safer than live signal posts.
- **CSRC (China):** Strictest jurisdiction. Do not publish any content combining Chinese-market tickers with signal verdicts.

**Default rule for all jurisdictions:** When in doubt, post the methodology, not the output.

---

## Section 5 — Launch Sequence

The agreed launch order is private beta first, then public channels (S-04):

1. **Private beta** — Share with a closed group of 5–10 trusted users. No public posts. Collect feedback and identify signal quality issues before any public exposure. Beta users must agree not to re-share screenshots publicly.
2. **Reddit soft launch** — Post in r/algotrading and r/IndiaInvestments with developer framing. Methodology screenshots only. Monitor for 2 weeks before broader promotion.
3. **Product Hunt launch** — Only after Reddit feedback is stable and no P0/P1 issues are open. Coordinate the launch day post with the approved gallery assets (methodology diagrams, no live signals).
4. **LinkedIn and Twitter/X** — Follow-on after Product Hunt. Repurpose the Product Hunt maker comment as the basis for posts.

Do not skip steps or run steps in parallel. The private beta step exists specifically to surface signal accuracy issues that would be amplified by a public launch.

---

## Footer

This document is an internal operational guideline for the GSI Dashboard project. It does not constitute legal advice. For formal legal review of SEBI finfluencer compliance, consult a SEBI-registered compliance professional before any public launch involving Indian-market securities signals.

**SEBI circular reference:** SEBI/HO/OIAE/OIAE_IAD-1/P/CIR/2023/0131 (August 2023).  
**Related risks:** RISK-L04 (SEBI finfluencer), RISK-L02 (Yahoo Finance ToS / data redistribution).  
**Owner:** GSI Lead Developer.  
**Next review:** Before any public launch event.

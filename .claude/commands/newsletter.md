# Newsletter & Community Communications — GSI Dashboard

Draft user-facing communications: weekly signal briefs, launch announcements, sprint updates.

## Communication types

### Weekly Signal Brief (community newsletter)
Format: Short email / Reddit post / Substack draft
Audience: Subscribed users, Reddit community
Content: Market breadth snapshot, notable signals this week, feature highlight, disclaimer
Tone: Data-led, educational, humble. Never: "buy this", "we predicted X"

Template:
```
📊 GSI Weekly — [Date]

**Market Breadth (Week ending [Date])**
India (Nifty 50): 31 BUY / 12 WATCH / 7 AVOID
USA (S&P 500 tracked): 24 BUY / 18 WATCH / 8 AVOID
[etc.]

**Interesting signals this week**
[2-3 tickers with notable Weinstein stage transitions — educational context only]

**Feature update**
[One paragraph on what shipped or changed]

**Disclaimer**: Educational signal visualisation only. Not investment advice.
Not SEBI-registered. Data via yfinance. Verify independently.

[Link to dashboard]
```

### Launch Announcement (Product Hunt / Reddit)
See /market-position for full templates.

### Sprint Retrospective Post (developer blog / GitHub)
Format: Technical post for developer community
Template (3P format — Progress / Plans / Problems):
```
**Progress**: What shipped in v[X.XX]
**Plans**: What's next (v[X.XX+1] sprint goals)
**Problems**: Known issues, limitations, design trade-offs
```

### Incident / Downtime Notice
```
GSI Dashboard — [Issue type] — [Date]

Status: [Investigating / Identified / Monitoring / Resolved]
Impact: [What users see]
Cause: [Root cause once known]
Resolution: [What was done]
Timeline: [Detected → Resolved]
```

## Tone rules for all GSI communications
- Lead with data, not marketing language
- Every signal mentioned = disclaimer nearby
- "We" = the tool/project, not investment advice provider
- Celebrate technical milestones, not "prediction accuracy"
- Be honest about limitations (yfinance delay, free tier constraints)

# 21-Day Revenue Plan — Spec
**Status:** ACTIVE
**Created:** 2026-05-18 (session_032)
**Owner:** Tarun Kochhar
**Revenue target:** First paying transaction within 21 days

---

## Revenue Streams (ranked by time-to-first-revenue)

| Stream | Days to first revenue | Revenue type | Blocking dependency |
|---|---|---|---|
| Financial consulting (1:1) | 1–7 days | One-time session fee ₹500–1,500 | None — warm network first |
| Digital products (ebooks/templates) | 3–10 days | One-time sale ₹99–499 | SuperProfile setup + Razorpay KYC |
| Affiliate commissions | 7–14 days | CPA ₹300–500/activated account | Link embed in content |
| Paid Zoom workshops | 7–14 days | ₹499–999/session | Calendly + payment link |
| GSI subscription (multi-user) | 30–45 days | MRR ₹499–999/user | OPEN-003 (Supabase) |
| Dropshipping (Ringo) | 14–21 days | Variable margin | Sourcing decision |

---

## Platform Stack

| Purpose | Platform | Cost | Notes |
|---|---|---|---|
| Link-in-bio storefront | SuperProfile (free) | ₹0 | UPI native, instant INR payouts |
| Payment backbone | Razorpay Payment Pages | ₹0 + 2% fee | Welcome Offer: first ₹5k/mo free |
| DM automation | LinkDM (free) | ₹0 | 1,000 DMs/mo; upgrade to ManyChat Pro at 500/mo |
| Email list building | Beehiiv (Launch free) | ₹0 | Up to 2,500 subs; monetise via SuperProfile not Beehiiv |
| Consulting scheduling | Calendly (free) | ₹0 | 1 event type on free plan |
| Global digital products | Payhip (free tier) | ₹0 + 5% | Razorpay integration = UPI from Indian buyers |
| Course delivery (Phase 2) | Teachable Starter | $29/mo | Only global platform with India payouts via teachable:pay |

---

## Asset → Commercial Binding

| Asset | Role | Revenue path |
|---|---|---|
| GSI Dashboard | Product + credibility anchor | Subscription (₹499–999/mo) → requires OPEN-003 |
| @thefinancialcoacher | Lead gen + product delivery | DM funnel → consulting → GSI demo → subscriber |
| @tarunkochhar | Warm audience cross-promotion | Drive traffic to @thefinancialcoacher |
| Org-corpus + conflict analysis | B2B consulting methodology | Engagement deliverable for enterprise clients (Phase 3) |
| Agentic infrastructure | Consulting differentiation | "I use AI-native tools to run my analysis" — trust signal |
| Crochet counter | Lifestyle pillar (10% content) | Brand authenticity; potential digital product (patterns, tutorials) |

---

## 21-Day Execution Sequence

### Days 1–3: Infra
- Set up @thefinancialcoacher (bio, highlights, LinkDM keyword triggers)
- Razorpay KYC + first Payment Page (ebook or consulting fee)
- SuperProfile storefront (link-in-bio: guide PDF + Calendly + GSI waitlist)
- Linktree pointing to SuperProfile
- 1-page lead magnet PDF (Canva: "5 Things Every Indian Investor Must Know")

### Days 4–7: Content launch
- 3 Reels (Basics / Mindset / Tools pillar rotation)
- 1 carousel (Budgeting — Pillar 2)
- Behind the Build Reel #1: why this account exists
- DM personally to 5 warm-network contacts: "I'm launching financial coaching — interested in a free session?"

### Days 8–14: Funnel activation
- First DM-trigger Reel ("Comment GUIDE")
- 2–3 discovery calls from DM leads (free — relationship building)
- Pillar 4 carousel referencing GSI Dashboard
- Deploy first paid offer to qualifying leads (₹500–999 consulting session)

### Days 15–21: Revenue activation
- Launch ebook on SuperProfile + Razorpay (₹299–499)
- Embed affiliate links (Zerodha / Groww) in 2 Reels
- Offer GSI Dashboard beta access to 3–5 consulting call leads (waitlist)
- Revenue tally + week 3 retrospective

---

## Open Decisions (required before executing)

| # | Decision | Recommended answer |
|---|---|---|
| D1 | WhatsApp in DM funnel? | No — LinkDM Free to start |
| D2 | Link-in-bio destination | SuperProfile (UPI-native, free) |
| D3 | GSI subscription price | ₹499/mo individual, ₹2–5K/mo B2B |
| D4 | OPEN-003 timing | Next sprint (see open-003-supabase-plan.md) |
| D5 | Notion MCP | Set up next session (~15 min) |

---

## Next Action

Invoke `writing-plans` skill to generate the day-by-day implementation plan with task assignments. This is the final item before the business goal identification blocker is lifted.

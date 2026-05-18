# @thefinancialcoacher 21-Day Revenue Launch — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate the first paying transaction within 21 days from @thefinancialcoacher using a sequenced platform stack and content funnel.

**Architecture:** Three-layer funnel — Instagram content drives DM leads → DM leads qualify into consulting calls or digital product sales → consulting leads graduate to GSI Dashboard waitlist. Revenue compounds across layers without requiring any single layer to be fully built before the next starts.

**Spec source:** `docs/superpowers/specs/21day-revenue-plan.md`
**GTM reference:** `docs/program/thefinancialcoacher-gtm.md`
**OPEN-003 reference:** `docs/program/open-003-supabase-plan.md`

**Open decisions (confirm before Day 1):**

| # | Decision | Answer locked |
|---|---|---|
| D1 | WhatsApp in DM funnel? | **No** — LinkDM Free |
| D2 | Link-in-bio destination | **SuperProfile** |
| D3 | GSI subscription price | **₹499/mo individual · ₹2–5K/mo B2B** |
| D4 | OPEN-003 timing | **Next sprint** (not this 21-day window) |
| D5 | Notion MCP | **Set up in first Claude session** |

---

## File / Asset Map

Before executing, know what gets created and where it lives:

| Asset | Location | Owner | Blocking |
|---|---|---|---|
| Lead magnet PDF | Canva → export → SuperProfile | Tarun | Days 3–7 content |
| SuperProfile page | superprofile.ai/thefinancialcoacher | Tarun | Digital product sales |
| Razorpay Payment Page | razorpay.com dashboard | Tarun | All paid transactions |
| Calendly booking link | calendly.com | Tarun | Consulting calls |
| Beehiiv newsletter | beehiiv.com | Tarun | Email list |
| LinkDM keyword config | linkd.me | Tarun | DM funnel automation |
| Reel scripts (×3) | Claude → Tarun drafts in phone notes | Both | Week 1 content |
| Carousel copy (×1) | Claude → Canva | Both | Week 1 content |
| Ebook draft (6–8 pages) | Claude drafts → Tarun reviews → Canva | Both | Week 3 revenue |
| Affiliate links | Zerodha + Groww referral portals | Tarun | Week 3 content |
| GSI waitlist form | Google Sheet (manual phase) | Tarun | Beta onboarding |
| @tarunkochhar cross-promo story | Instagram | Tarun | Week 2 traffic |

---

## Days 1–3: Infrastructure

**Target by end of Day 3:** All platforms live, payment processing enabled, lead magnet ready.

---

### Task 1: @thefinancialcoacher Instagram profile

**Owner:** Tarun | **Time:** 45 min

- [ ] **Step 1: Write bio copy (Claude generates, Tarun approves)**

  Use this bio (150 chars max, fits Instagram):
  ```
  📊 Financial clarity for busy Indians
  🧠 Market signals · Budget systems · Real strategies
  🔗 Free guide + book a call 👇
  ```

- [ ] **Step 2: Set profile photo**

  Use a clean headshot (not a logo). Consistent with @tarunkochhar if already set.

- [ ] **Step 3: Set account to Creator (not Personal)**

  Settings → Account → Switch to Professional → Creator → Personal Finance.

- [ ] **Step 4: Set link-in-bio to SuperProfile URL**

  Format: `superprofile.ai/thefinancialcoacher` (set this after Task 2, come back).

- [ ] **Step 5: Create 3 highlight covers in Canva**

  Titles: `FREE GUIDE` · `COACHING` · `GSI TOOL`
  Background: dark navy `#0d1b2a`. Text: white, bold.

- [ ] **Step 6: Verify**

  Profile visible, bio readable in 3 seconds, link-in-bio resolves.

---

### Task 2: SuperProfile storefront

**Owner:** Tarun | **Time:** 30 min

- [ ] **Step 1: Create account at superprofile.ai**

  Username: `thefinancialcoacher`

- [ ] **Step 2: Connect UPI / bank account**

  Required for instant INR payouts. Have IFSC + account number ready.

- [ ] **Step 3: Add three blocks to the page**

  Block 1 — Free guide:
  ```
  Title: "5 Things Every Indian Investor Must Know"
  Type: Free download (PDF)
  CTA button: "Download Free Guide"
  ```
  Block 2 — Consulting call:
  ```
  Title: "1:1 Financial Clarity Call — 30 min"
  Type: Link → Calendly booking URL
  Price: ₹999 (Razorpay link — from Task 3)
  ```
  Block 3 — GSI Dashboard Waitlist:
  ```
  Title: "GSI Dashboard — Early Access Waitlist"
  Type: Link → Google Form (Task 6)
  CTA: "Join the waitlist (free)"
  ```

- [ ] **Step 4: Set page live and copy URL**

  Paste into @thefinancialcoacher bio.

- [ ] **Step 5: Verify**

  Open SuperProfile on mobile. All three blocks visible and tappable.

---

### Task 3: Razorpay KYC + first Payment Page

**Owner:** Tarun | **Time:** 60–90 min (KYC may take 1 business day to clear)

- [ ] **Step 1: Create Razorpay account**

  razorpay.com → Sign Up → Individual / Sole Proprietor.

- [ ] **Step 2: Complete KYC**

  Documents needed: PAN card + bank account details + address proof.
  Note: KYC clears in 24–48 hours. Start on Day 1 even if Day 3 content comes later.

- [ ] **Step 3: Create first Payment Page — consulting session**

  Dashboard → Payment Pages → Create →
  ```
  Title: "1:1 Financial Clarity Call — 30 min"
  Amount: ₹999
  Description: "Book a 30-min 1:1 session. Post-payment, you'll receive a Calendly link to schedule."
  Collect fields: Name, Email, Phone
  ```

- [ ] **Step 4: Copy Payment Page URL**

  Paste into SuperProfile Block 2 (consulting call).

- [ ] **Step 5: Test payment flow with ₹1 test transaction**

  Razorpay has a test mode — use it. Verify email confirmation fires.

- [ ] **Step 6: Verify**

  Payment Page loads on mobile. ₹999 is the amount shown. UPI option is visible.

---

### Task 4: Calendly setup

**Owner:** Tarun | **Time:** 20 min

- [ ] **Step 1: Create account at calendly.com**

  Connect Google Calendar for availability.

- [ ] **Step 2: Create one event type (free plan allows 1)**

  ```
  Event name: "Financial Clarity Call"
  Duration: 30 min
  Platform: Google Meet (auto-generated link)
  Buffer: 15 min before + after
  Available: Mon–Sat, 7–9pm IST (adjust to your schedule)
  ```

- [ ] **Step 3: Set confirmation message**

  ```
  "Thanks for booking! Please make the payment at [Razorpay link] to confirm your slot.
  You'll receive a Google Meet link 1 hour before the call."
  ```

- [ ] **Step 4: Copy booking link**

  Paste into SuperProfile Block 2 as the primary CTA.

---

### Task 5: Lead magnet PDF — "5 Things Every Indian Investor Must Know"

**Owner:** Both | **Time:** 60 min (Claude generates content, Tarun designs in Canva)

- [ ] **Step 1: Claude generates the 1-page content outline**

  Ask Claude: "Write the content for a 1-page lead magnet PDF titled '5 Things Every Indian Investor Must Know'. Target audience: salaried Indian professional, 28–35, earning ₹8–25L/year, limited investing knowledge. Each point should be a concrete action or mindset shift, not vague advice. 80 words max per point."

- [ ] **Step 2: Tarun reviews and edits the 5 points**

  Apply personal voice. Remove anything that sounds generic or corporate.

- [ ] **Step 3: Build in Canva**

  Template search: "1-page cheat sheet dark" or "investor guide".
  Brand colours: `#0d1b2a` background, `#4fc3f7` accent.
  Font: Montserrat Bold for headers, regular for body.
  Add at bottom: `@thefinancialcoacher · superprofile.ai/thefinancialcoacher`

- [ ] **Step 4: Export as PDF**

  Canva → Share → Download → PDF Standard.

- [ ] **Step 5: Upload to SuperProfile Block 1**

  Type: Free download. Require email to download (enables Beehiiv capture).

- [ ] **Step 6: Verify**

  Download the PDF yourself on mobile. Check it renders cleanly on a phone screen.

---

### Task 6: GSI waitlist Google Form

**Owner:** Tarun | **Time:** 15 min

- [ ] **Step 1: Create Google Form**

  Title: "GSI Dashboard — Early Access Waitlist"
  Fields:
  ```
  1. Full Name (short answer, required)
  2. Email address (short answer, required)
  3. How did you find us? (dropdown: Instagram / Consulting call / Friend / Other)
  4. Would ₹499/month work for you? (multiple choice: Yes · No · Maybe / Tell me more)
  ```

- [ ] **Step 2: Set confirmation message**

  ```
  "You're on the list! We'll email you when beta access opens.
  Expected: June–July 2026. You'll be among the first 20."
  ```

- [ ] **Step 3: Link response sheet to a dedicated Google Sheet**

  Responses → Spreadsheet. Name it `GSI Waitlist — Master`.

- [ ] **Step 4: Copy form link**

  Paste into SuperProfile Block 3.

- [ ] **Step 5: Verify**

  Submit a test response. Check it appears in the Google Sheet.

---

### Task 7: LinkDM keyword triggers

**Owner:** Tarun | **Time:** 20 min

- [ ] **Step 1: Create account at linkd.me**

  Connect @thefinancialcoacher Instagram.

- [ ] **Step 2: Create trigger 1 — keyword: GUIDE**

  ```
  Trigger word: GUIDE
  DM response:
  "Hey [name]! Here's your free guide — 5 Things Every Indian Investor Must Know 📊
  [SuperProfile PDF link]
  
  If you want to talk through your own financial situation, book a free 15-min intro call here:
  [Calendly link]"
  ```

- [ ] **Step 3: Create trigger 2 — keyword: COACH**

  ```
  Trigger word: COACH
  DM response:
  "Hey [name]! Happy to help. I offer 30-min 1:1 financial clarity sessions for ₹999.
  Book here and you'll get a confirmation + Google Meet link:
  [Razorpay Payment Page link]
  
  Any questions, just reply here."
  ```

- [ ] **Step 4: Create trigger 3 — keyword: ACCESS**

  ```
  Trigger word: ACCESS
  DM response:
  "Hey [name]! The GSI Dashboard is in private beta. Join the waitlist and I'll personally
  reach out when your access is ready:
  [Google Form link]
  
  Takes 30 seconds."
  ```

- [ ] **Step 5: Test all three triggers**

  From a secondary Instagram account, comment GUIDE / COACH / ACCESS on any post.
  Verify DMs fire within 60 seconds.

---

### Task 8: Beehiiv newsletter setup

**Owner:** Tarun | **Time:** 20 min

- [ ] **Step 1: Create account at beehiiv.com**

  Plan: Launch (free, up to 2,500 subs).
  Publication name: "The Financial Coacher"
  Subdomain: `thefinancialcoacher.beehiiv.com`

- [ ] **Step 2: Set welcome email**

  ```
  Subject: "Welcome — here's your free guide"
  Body:
  "Hey [first name],
  
  Thanks for joining. As promised, here's the guide:
  [PDF link or SuperProfile link]
  
  Every week, I'll send one insight on investing, budgeting, or the markets.
  No fluff. Under 5 minutes.
  
  — Tarun
  @thefinancialcoacher"
  ```

- [ ] **Step 3: Connect Beehiiv signup form to SuperProfile**

  SuperProfile → Integrations → Beehiiv → connect.
  (If direct integration unavailable: use a Beehiiv embed link as Block 1 CTA instead of direct PDF.)

- [ ] **Step 4: Verify**

  Subscribe with your own email. Confirm welcome email arrives within 2 minutes.

---

## Days 4–7: Content Launch

**Target by end of Day 7:** 4 pieces of content published, 5 warm-network DMs sent, first consulting inquiry received.

---

### Task 9: Reel #1 — Behind the Build (Day 4)

**Owner:** Both | **Time:** 90 min total (30 min script + 45 min shoot + 15 min edit)

- [ ] **Step 1: Claude generates Reel script**

  Use the hook-body-CTA format from `docs/program/thefinancialcoacher-gtm.md` Template 1.
  Topic: "Why I built my own stock market dashboard and why it changed how I invest."
  Hook: Start mid-action (opening a laptop showing the GSI dashboard).
  Duration: 45–60 seconds.

- [ ] **Step 2: Tarun records**

  Shoot in portrait (9:16). Good lighting — ring light or window. Plain background.
  Speak naturally; one or two takes. Imperfect is authentic.

- [ ] **Step 3: Edit in CapCut or Instagram native editor**

  Add captions (auto-generated, then fix errors).
  Add background music: lo-fi/instrumental, low volume.
  Add on-screen text for the key stat or quote.

- [ ] **Step 4: Write caption**

  ```
  I spent months looking at 50+ dashboards and none of them showed me what I actually needed.

  So I built one.

  9 markets. 559 stocks. Real signals — not noise.

  If you want to see it in action, comment ACCESS and I'll send you the waitlist link.

  #investing #stockmarket #personalfinance #indianinvestor #financialindependence
  ```

- [ ] **Step 5: Schedule or post**

  Post time: Tuesday or Thursday, 7–9pm IST for maximum reach.

- [ ] **Step 6: Verify**

  Post is live. LinkDM trigger for ACCESS is active. Captions are error-free.

---

### Task 10: Reel #2 — Basics pillar (Day 5)

**Owner:** Both | **Time:** 90 min

- [ ] **Step 1: Claude generates script**

  Topic from Pillar 1 (Financial Basics): "The one number every Indian investor must track before buying any stock."
  Hook: "Most people buy stocks without looking at this number. I'll show you in 60 seconds."
  Key stat: Share P/E ratio explanation + India context (Nifty average P/E ~22).

- [ ] **Step 2: Tarun records and edits**

  Same format as Reel #1. On-screen text to show the number prominently.

- [ ] **Step 3: Write caption**

  ```
  Before you buy any stock, check this one number.

  Most people skip it. That's why they buy at the wrong time.

  Drop GUIDE in the comments — I'll send you a free cheat sheet with the 5 things every Indian investor needs to know.

  #stockmarket #investing #nifty50 #beginnerinvestor #india
  ```

- [ ] **Step 4: Post**

  Wednesday or Friday, 7–9pm IST.

---

### Task 11: Carousel — Budgeting pillar (Day 6)

**Owner:** Both | **Time:** 60 min

- [ ] **Step 1: Claude generates 7-slide carousel copy**

  Topic: "The 50-30-20 rule — and why it doesn't work for most Indian salaries."
  Slide structure:
  ```
  Slide 1 (hook): "Everyone tells you 50-30-20. Here's why it fails for most Indians."
  Slide 2: What the rule says (needs / wants / savings)
  Slide 3: Why it breaks in India (rent costs, family obligations, irregular income)
  Slide 4: The modified version — 40-20-20-20 (needs / wants / savings / family)
  Slide 5: How to apply it in 15 minutes this weekend
  Slide 6: The one tool that helps you track it automatically
  Slide 7 (CTA): "Comment GUIDE for the free investor checklist. Follow for more."
  ```

- [ ] **Step 2: Build in Canva**

  Template: 1:1 square carousel.
  Brand: `#0d1b2a` background, `#4fc3f7` accent, Montserrat.
  Consistent slide layout: big number/headline top, explanation below, brand mark on all slides.

- [ ] **Step 3: Export and post**

  Save as images, upload as carousel post.

---

### Task 12: Reel #3 — Mindset pillar (Day 7)

**Owner:** Both | **Time:** 90 min

- [ ] **Step 1: Claude generates script**

  Topic: "The investing mistake I made that cost me ₹80,000 — and the mindset shift that fixed it."
  Personal story format. Honest and specific. CTA: comment COACH.

- [ ] **Step 2: Tarun edits script with real numbers**

  Replace the placeholder loss amount with a real experience if possible. Authenticity converts.

- [ ] **Step 3: Record, edit, post**

  Same format. Post Sunday 7–9pm IST.

---

### Task 13: Warm-network DMs (Day 4–5)

**Owner:** Tarun | **Time:** 30 min

- [ ] **Step 1: Identify 5 contacts**

  People who: (a) ask you about money/investing, (b) are salaried 25–40, (c) you have a warm relationship with.
  Write their names in a note before sending anything.

- [ ] **Step 2: Send personalised DMs (do NOT copy-paste identically)**

  Template:
  ```
  "Hey [name], I'm launching a financial coaching account — @thefinancialcoacher.
  I'm offering free 15-min intro calls this week to test the format.
  Would you be interested? No pressure — just genuine curiosity."
  ```

- [ ] **Step 3: Track responses in a note or Google Sheet**

  Column A: Name | Column B: Sent date | Column C: Response | Column D: Status (interested / not / booked)

- [ ] **Step 4: Follow up on interested responses**

  Send Calendly link directly. No Razorpay yet — these are free discovery calls.

- [ ] **Step 5: Verify**

  5 DMs sent. At least 1 response received by Day 7.

---

### Task 14: @tarunkochhar cross-promotion story (Day 7)

**Owner:** Tarun | **Time:** 15 min

- [ ] **Step 1: Post a story on @tarunkochhar**

  ```
  "I've been quietly building something. 
  If you're curious about investing, markets, and real financial strategy — 
  I've launched @thefinancialcoacher.
  
  Link in bio."
  ```

  Add link sticker → superprofile.ai/thefinancialcoacher

- [ ] **Step 2: Verify**

  Story is live. Link sticker resolves. Highlight cover added to @tarunkochhar if relevant.

---

## Days 8–14: Funnel Activation

**Target by end of Day 14:** 2–3 discovery calls completed, first paid consulting transaction, 50+ Reel views on DM-trigger content.

---

### Task 15: DM-trigger Reel ("Comment GUIDE") — Day 8

**Owner:** Both | **Time:** 90 min

- [ ] **Step 1: Claude generates script**

  This Reel exists specifically to drive GUIDE comments. High-value hook, educational value front-loaded, explicit CTA at 45-second mark and in caption.

  Topic: "The 3 questions I ask before investing in any Indian stock."
  Hook: "Most Indian investors never ask these. I do — every time."
  CTA at end: "Comment GUIDE and I'll send you my full 5-point investor checklist."

- [ ] **Step 2: Record, edit, post**

  Post Tuesday or Thursday, 7–9pm IST for peak engagement.

- [ ] **Step 3: Monitor GUIDE comments for first 2 hours**

  Verify LinkDM is firing automatically. Respond manually to any comments that say GUIDE but are slightly misspelled (GUID, GUIDEE) — LinkDM won't catch these.

- [ ] **Step 4: Verify**

  5+ GUIDE comments within 24 hours = funnel is working.

---

### Task 16: Run 2–3 free discovery calls (Days 8–12)

**Owner:** Tarun | **Time:** 30 min per call

- [ ] **Step 1: Prepare call framework (Claude generates, Tarun edits)**

  ```
  Discovery call structure (30 min):
  Min 0–5:   Introductions. What they do, what their money situation looks like.
  Min 5–15:  The main pain. Ask: "What's the one money thing keeping you up at night?"
             Let them talk. Don't solve yet.
  Min 15–20: Your framework. Share one insight specific to their situation.
             Reference GSI dashboard signal if relevant.
  Min 20–25: Next steps. If there's a fit: "I offer 30-min paid sessions for ₹999.
             Would that be useful?" If not: refer them to the free guide.
  Min 25–30: Close. "I'll send you a follow-up note with the one thing we discussed."
  ```

- [ ] **Step 2: Send post-call note within 1 hour**

  Template:
  ```
  "Hey [name], great talking today. The one thing I'd focus on first: [specific insight].
  
  If you want to go deeper, here's the booking link: [Razorpay Payment Page]
  
  And if you'd like early access to the dashboard we discussed: [Google Form link]"
  ```

- [ ] **Step 3: Log the call in your tracking sheet**

  Name | Date | Key pain | Outcome (booked paid / joining waitlist / not a fit) | Notes

---

### Task 17: GSI Dashboard credibility carousel — Day 10

**Owner:** Both | **Time:** 60 min

- [ ] **Step 1: Claude generates 7-slide carousel copy**

  Topic: "I built a stock market dashboard that tracks 559 stocks across 9 markets. Here's what it showed me last week."
  Use real signals from GSI (screenshot or describe).
  Slide 7 CTA: "Comment ACCESS for the beta waitlist."

- [ ] **Step 2: Include one real GSI screenshot**

  Take a clean screenshot of the GSI dashboard (good signal state, no error messages).
  Slide 3 or 4 — show it in context of the signal discussion.

- [ ] **Step 3: Build in Canva and post**

  Same brand format. Post Wednesday, 7–9pm IST.

---

### Task 18: First paid consulting offer (Days 10–14)

**Owner:** Tarun | **Time:** 15 min per offer sent

- [ ] **Step 1: Identify 2–3 qualifying leads from discovery calls**

  Qualifying criteria: expressed clear pain, engaged during call, didn't object to ₹999 price.

- [ ] **Step 2: Send personalised offer message**

  ```
  "Hey [name], based on our conversation, I think a focused 30-min session on
  [specific topic they mentioned] would get you to a clear decision faster.
  
  My rate is ₹999 for 30 min. Here's the link to book:
  [Razorpay Payment Page URL]
  
  Payment confirms the slot. I'll send a Google Meet link the morning of the call."
  ```

- [ ] **Step 3: Wait 24–48 hours. If no response, follow up once.**

  ```
  "Hey [name], just checking — did the booking link work okay?
  Happy to answer any questions before you book."
  ```

- [ ] **Step 4: Log payment received**

  When Razorpay confirms payment: mark as WON in tracking sheet.
  This is the first paying transaction. Record date, amount, source.

---

## Days 15–21: Revenue Activation

**Target by end of Day 21:** Ebook live on SuperProfile, affiliate links embedded in 2 Reels, 3–5 waitlist signups, revenue tally completed.

---

### Task 19: Ebook — "The Indian Investor's Playbook" (Days 15–18)

**Owner:** Both | **Time:** 3–4 hours total across 2 sessions

- [ ] **Step 1: Claude drafts ebook outline (Session 1)**

  Target: 8–10 pages. PDF format.
  ```
  Page 1: Cover — "The Indian Investor's Playbook"
           Subtitle: "5 frameworks every salaried professional needs"
           By Tarun Kochhar · @thefinancialcoacher
  Page 2: Who this is for (Priya, Arjun personas)
  Page 3: Framework 1 — The modified 40-20-20-20 budget
  Page 4: Framework 2 — The 3 questions before any stock purchase
  Page 5: Framework 3 — Reading a P/E ratio without a finance degree
  Page 6: Framework 4 — The Weinstein Stage method (simplified — reference GSI)
  Page 7: Framework 5 — When to sell (most guides skip this)
  Page 8: Resources + next steps (Calendly · SuperProfile · GSI waitlist)
  ```

- [ ] **Step 2: Claude writes first draft of all 8 pages**

  Request in Claude: "Write the full content for this ebook based on the outline above.
  Voice: direct, conversational, no jargon. India-specific examples throughout.
  Word count: 1,200–1,500 words total."

- [ ] **Step 3: Tarun reviews and adds personal examples**

  Most critical pages: 3, 5, 7 — these need real Tarun voice and specific India numbers.

- [ ] **Step 4: Build in Canva**

  Template: "Ebook PDF" or "Report".
  Branding consistent with lead magnet.
  Export: PDF Print (higher quality than PDF Standard).

- [ ] **Step 5: Upload to SuperProfile as a paid product**

  ```
  Title: "The Indian Investor's Playbook"
  Price: ₹299
  Delivery: Instant download
  Description: "5 frameworks. 10 pages. The investing clarity you've been missing."
  ```

- [ ] **Step 6: Create Razorpay Payment Page for ebook**

  Same pattern as consulting payment page. Amount: ₹299.
  Link to this from SuperProfile.

- [ ] **Step 7: Verify**

  Purchase the ebook yourself (use Razorpay test mode). Confirm download works.
  Post announcement on @thefinancialcoacher — caption: "The playbook is live."

---

### Task 20: Affiliate link Reels (Days 16–17)

**Owner:** Both | **Time:** 90 min per Reel

- [ ] **Step 1: Get affiliate links**

  Zerodha: zerodha.com/open-account → referral program.
  Groww: groww.in/refer-and-earn.
  Both are free to join. Save your unique referral URLs.

- [ ] **Step 2: Reel #5 — Zerodha affiliate**

  Topic: "How I place my trades — and why I use Zerodha."
  Honest comparison. Mention what you actually use and why.
  Caption: "Open your free Zerodha account → link in bio (affiliate link — I earn a small fee if you activate)."
  Disclosure in caption is required — be explicit about affiliate relationship.

- [ ] **Step 3: Reel #6 — Groww affiliate**

  Topic: "Best app for SIP investing in India — my honest review."
  Caption: Same disclosure pattern.

- [ ] **Step 4: Update SuperProfile with affiliate links**

  Add a new block: "Open a free trading account" → Zerodha link.
  Second block: "Start your first SIP" → Groww link.

- [ ] **Step 5: Verify**

  Affiliate links resolve. Disclosures are in caption. Razorpay not used here — affiliate = CPA, no upfront payment from viewer.

---

### Task 21: GSI Dashboard beta invitations (Days 18–20)

**Owner:** Tarun | **Time:** 30 min

- [ ] **Step 1: Pull waitlist Google Sheet**

  Filter: column D (₹499/month → Yes or Maybe).

- [ ] **Step 2: Send personalised beta invite to top 3–5 leads**

  ```
  "Hey [name], you're on the GSI Dashboard waitlist.
  
  I'm opening up beta access to 5 people before public launch.
  
  What that means:
  - Free access for 30 days
  - Direct WhatsApp/call with me to share feedback
  - First-mover pricing locked in when we go live (₹399/mo vs ₹499 standard)
  
  Interested? Just reply YES and I'll send you the link + a quick onboarding note."
  ```

- [ ] **Step 3: Collect YES responses**

  For each YES: send the GSI Dashboard URL + a 5-minute guided tour voice note or screen recording.
  Log in tracking sheet: Name | Beta start date | Feedback received | Conversion likelihood.

- [ ] **Step 4: Note: OPEN-003 is not required for this step**

  Beta access = current live dashboard URL. No auth, no subscription gate.
  The value exchange is feedback + priority pricing commitment.

---

### Task 22: Week 3 revenue tally + retrospective (Day 21)

**Owner:** Both | **Time:** 45 min

- [ ] **Step 1: Claude builds tally template, Tarun fills numbers**

  ```
  === @thefinancialcoacher — Day 21 Revenue Tally ===

  Stream                  | Target         | Actual | Gap
  ------------------------|----------------|--------|----
  Consulting sessions     | 1–3 × ₹999    | ₹___   | ___
  Ebook sales             | 5–10 × ₹299   | ₹___   | ___
  Affiliate activations   | 3–5 × ₹300–500| ₹___   | ___
  TOTAL                   | ₹4,000–8,000  | ₹___   | ___

  Funnel metrics:
  - Followers gained: ___
  - Profile visits (Instagram Insights): ___
  - GUIDE comments triggered: ___
  - Waitlist signups: ___
  - Discovery calls held: ___
  - Paid consulting sales: ___
  - Ebook downloads: ___
  ```

- [ ] **Step 2: Identify what worked and what didn't**

  For each stream: Was the conversion step the bottleneck, or the awareness step?
  (e.g., 0 ebook sales but 200 guide downloads = pricing or copy issue, not awareness)

- [ ] **Step 3: Set Week 4–8 priorities based on tally**

  If consulting > ebook: double down on discovery calls, de-prioritise ebook marketing.
  If affiliate > consulting: create more comparison/review Reels.
  If waitlist > 10 leads: escalate OPEN-003 sprint priority.

- [ ] **Step 4: Commit retrospective note to docs/**

  File: `docs/program/thefinancialcoacher-week3-retro.md`
  Keep it under 200 words — decision outputs, not narrative.

---

## Success Criteria — What Day 21 Looks Like

| Metric | Minimum (plan succeeded) | Stretch |
|---|---|---|
| First paid transaction | ₹1 received | ₹5,000+ total |
| Consulting sessions sold | 1 | 3+ |
| Ebook downloads (paid) | 1 | 10+ |
| Affiliate activations | 0 | 3+ |
| GSI waitlist signups | 3 | 10+ |
| Beehiiv subscribers | 20 | 100+ |
| Instagram followers (@thefinancialcoacher) | 50 | 200+ |

**The blocker is lifted when one paying transaction clears — regardless of amount.**

---

## Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Razorpay KYC takes >3 days | Medium | Start Day 1. Use UPI QR code manually if KYC delays. |
| No GUIDE comments on first trigger Reel | Medium | Seed with 2–3 comments from secondary accounts. DM 10 followers directly to watch and comment. |
| Discovery calls don't convert to paid | Medium | Lower price to ₹499 for first 3 paid sessions — build testimonials, then raise. |
| Ebook doesn't sell | Low | Price it down to ₹99. Remove friction. Rename it "cheat sheet" not "playbook" if needed. |
| Affiliate links not approved | Low | Zerodha and Groww both have instant referral program access — no approval needed. |
| @tarunkochhar audience doesn't cross over | Low | Cross-post 1 Reel directly on @tarunkochhar with explicit tag. Warm audience > cold. |

---

*Plan version: 1.0 — created 2026-05-18 (session_032). Source: docs/superpowers/specs/21day-revenue-plan.md*

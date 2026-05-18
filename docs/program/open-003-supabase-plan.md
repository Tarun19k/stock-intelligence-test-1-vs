# OPEN-003: Cross-Session Persistence & Auth Layer
**Status:** PLANNING — not started
**Priority:** DOUBLE-CRITICAL — blocks Phase 2 (admin/client separation) AND 21-day subscription revenue model
**Effort:** High (3–5 sessions)
**Created:** 2026-05-18
**Depends on:** None (greenfield addition)
**Blocks:** ASSESS-P2-01, ASSESS-P2-02, GSI subscriber onboarding

---

## 1. Why This Exists

GSI currently has no memory between sessions. Every redeploy wipes the filesystem. Streamlit Cloud is stateless by design. This means:

- Forecasts are lost on reload
- Portfolio positions can't be saved
- There is no concept of "users" — everyone sees the same app
- No subscription model is possible without knowing who is logged in

OPEN-003 adds the persistence and auth layer that makes all of the above possible.

---

## 2. Yahoo Finance ToS — Plain English

### What the conflict is

Yahoo Finance says: you can use their data for **personal/educational purposes**, but you **cannot redistribute it commercially**.

"Redistribute commercially" in practice means: charging money to give people access to a product that runs on Yahoo Finance data.

### Why it's only a problem NOW

Before this sprint: GSI was a free, public demo tool. Nobody paid to use it. No ToS conflict.

Now: The plan is to put GSI behind a subscription paywall. Someone pays ₹499/month → they get access to a dashboard powered by Yahoo Finance price feeds → that is commercial redistribution of Yahoo Finance data → that violates ToS.

It was harmless before because there was no commercial transaction. The subscription model creates the conflict.

### What happens if ignored

- Best case: Yahoo continues aggressive rate-limiting (already happening) and eventually blocks the app's IP range permanently.
- Medium case: A C&D letter requiring removal of the paywall or shutdown of the app.
- Worst case: Legal action (unlikely for a small India-market app, but not zero).
- Real practical risk: If the Instagram coaching content publicises "subscribe to get market intelligence signals" and it traces to Yahoo Finance data, it creates a visible target.

### The cleanest workaround: charge for the layer, not the data

Yahoo prohibits charging for access to their data. They do not prohibit building a tool that uses their data freely, where users pay for the **analysis, expertise, and delivery layer** on top.

**Reframing the subscription:**
> "You're not paying for market data. The data is free — anyone can get it from Yahoo Finance. You're paying for the signal engine (RSI, Weinstein Stage, momentum scoring), the curated watchlist for 9 markets, and direct access to Tarun's portfolio analysis sessions."

This is how most fintech apps in India operate at the indie/startup stage — they use YF data but sell the interpretation, not the data itself. It is a grey area, but a widely used and defensible one.

### Longer-term clean solution

Switch paying subscriber data feeds to a licensed source. Options:
- **Polygon.io Starter**: $29/month, 15-minute delayed data, unlimited API calls, commercial use licensed
- **NSE India licensed APIs**: For India-market-only signals, NSE has official data partnerships via vendors (Upstox Data API, Angel One SmartAPI, Zerodha Data) — some have free tiers for limited use
- **Alpha Vantage Premium**: ~$50/month, global markets, commercial license

The migration path: free tier stays on YF · paying subscribers get data from a licensed source. One source switch in `market_data.py` — the rest of the app is source-agnostic.

---

## 3. The GSI Waitlist — Who, What, Why

### Who goes into the waitlist

Three entry points:

1. **Instagram DM funnel**: Anyone who comments GUIDE / COACH / ACCESS on a Pillar 4 or Tools post → qualifies via DM → added to waitlist if they express interest in the dashboard
2. **Consulting call leads**: Anyone Tarun speaks with who asks "how do I get access to that dashboard?"
3. **Link in bio / Linktree**: Anyone who clicks the GSI Waitlist link from the @thefinancialcoacher profile

### What they get

| Tier | What they receive | Timing |
|---|---|---|
| Waitlist (free) | Position confirmed, early access promise, occasional progress updates | Now |
| Beta (first 20) | Free access for 30 days, direct feedback session with Tarun, features shaped by their input, first-mover pricing locked in | When OPEN-003 ships |
| Early subscriber (first 50) | 50% off first 3 months, named in launch post, priority support | At public launch |
| Standard subscriber | Full platform access at standard pricing | Post-launch |

### What they give in return

- **Email address** (lead capture — the most valuable asset at launch)
- **Interest signal** (validates the product before you build it)
- **Willingness-to-pay signal**: If the DM or waitlist form asks "We're planning ₹499/month — does that work for you?" the response data shapes pricing
- **Beta feedback** (for the first 20): Real usage insights that improve the product before public launch
- **Social proof**: Beta users who get results become testimonials and referrals

### The waitlist as a pre-revenue move

The waitlist proves demand **without requiring Supabase to be built yet**. Collect emails in a Google Sheet or Notion database today. OPEN-003 only needs to be ready for actual onboarding (beta phase). That buys 3–4 weeks to build it properly.

---

## 4. Architecture Options — No-Cost to Low-Cost

### Option A: Supabase Free Tier (RECOMMENDED)

**What it is:** Managed Postgres database + auth + row-level security + real-time. Open source, hosted, no ops burden.

**Free tier limits:**
- 500MB database storage
- 50,000 monthly active users
- 2 projects
- Unlimited API requests
- Auth (email/password, Google OAuth) included free

**At 50–200 subscribers:** Free tier covers everything. Upgrade to $25/month Pro plan only when storage exceeds 8GB or MAU exceeds 50K — neither will happen in the first year.

**Cost at launch:** ₹0/month.

**Why it's the right answer:** Professional, secure, battle-tested, Postgres (not a NoSQL workaround), row-level security means one database safely serves multiple users with zero risk of cross-user data leakage.

---

### Option B: PocketBase (Self-Hosted)

**What it is:** Open source backend — SQLite database + auth + admin UI + REST API. Single binary, runs anywhere.

**Hosting options at no cost:**
- Railway.app free tier (500 hours/month — sufficient for a low-traffic app)
- Fly.io free tier (3 shared-CPU VMs, 256MB RAM each)

**Cost:** ₹0/month (on free hosting tiers). Slightly more ops burden than Supabase (you manage the instance).

**When to choose this:** If Supabase's managed nature is a concern, or if the app needs to run fully on-premise for data governance reasons. Not needed here.

---

### Option C: Google Sheets as a Database (Manual, Zero Infra)

**What it is:** Google Sheets + Google Sheets API as a lightweight user database.

**What it can store:** User email, subscription status (Y/N), subscription start date, plan tier, notes.

**What it cannot do:** Row-level security, real-time, complex queries, proper auth.

**When it makes sense:** Waitlist phase only — before OPEN-003 is built. Store waitlist leads in a Sheet today. No code required. Export to Supabase when you're ready to onboard.

**Cost:** ₹0.

---

### Option D: Custom SQLite on Streamlit Cloud

**Why it doesn't work:** Streamlit Cloud wipes the filesystem on every redeploy. SQLite is a local file. Any data written to SQLite is gone on the next deploy. This is explicitly noted in the DO-NOT-UNDO rules (forecast.py section).

---

### Decision

**Use Supabase Free Tier.** It is the only option that gives: persistent storage + proper auth + row-level security + zero cost at the scale we need. PocketBase is a reasonable backup if Supabase has downtime or service issues. Google Sheets covers the waitlist phase before any code is written.

---

## 5. Schema Design

```sql
-- Users (managed by Supabase Auth — this table extends it)
CREATE TABLE user_profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id),
    email       TEXT NOT NULL,
    display_name TEXT,
    plan_tier   TEXT DEFAULT 'free' CHECK (plan_tier IN ('free', 'beta', 'standard', 'b2b')),
    subscribed_at TIMESTAMPTZ,
    subscription_active BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Forecasts (cross-session persistence — replaces session_state storage)
CREATE TABLE forecasts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES user_profiles(id),
    ticker      TEXT NOT NULL,
    forecast_date DATE NOT NULL,
    horizon     TEXT NOT NULL,  -- '1w' | '1m' | '3m'
    direction   TEXT NOT NULL,  -- 'bullish' | 'bearish' | 'neutral'
    target_price NUMERIC,
    stated_assumptions TEXT,
    outcome_score NUMERIC,      -- null until resolved
    resolved_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio positions (user's tracked holdings)
CREATE TABLE portfolio_positions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES user_profiles(id),
    ticker      TEXT NOT NULL,
    quantity    NUMERIC,
    avg_cost    NUMERIC,
    added_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, ticker)
);

-- Waitlist (collected before auth is live)
CREATE TABLE waitlist (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT UNIQUE NOT NULL,
    source      TEXT,           -- 'instagram_dm' | 'consulting_call' | 'linktree'
    persona     TEXT,           -- 'priya' | 'arjun' | 'ravi' | 'neha' | null
    price_ok    BOOLEAN,        -- response to "₹499/month — does that work?"
    notes       TEXT,
    joined_at   TIMESTAMPTZ DEFAULT NOW()
);
```

**Row-level security policies (critical — prevents cross-user data leakage):**
```sql
-- Users can only read/write their own data
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_profile" ON user_profiles USING (auth.uid() = id);

ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_forecasts" ON forecasts USING (auth.uid() = user_id);

ALTER TABLE portfolio_positions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_positions" ON portfolio_positions USING (auth.uid() = user_id);
```

---

## 6. Streamlit Integration Architecture

### Auth flow

```
User visits app
  → Supabase auth check (JWT in st.session_state)
  → Not logged in: show login/signup form
  → Logged in: load user profile + plan tier
    → free tier: show public dashboard
    → standard/beta: show full dashboard with persistence
```

### New module: `auth.py`

```python
# auth.py — Supabase auth wrapper for Streamlit
from supabase import create_client, Client
import streamlit as st
from config import SUPABASE_URL, SUPABASE_ANON_KEY

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_current_user():
    """Returns user dict or None."""
    token = st.session_state.get("sb_token")
    if not token:
        return None
    try:
        return get_supabase().auth.get_user(token).user
    except Exception:
        return None

def render_auth_gate():
    """Show login/signup form. Returns True if user is authenticated."""
    user = get_current_user()
    if user:
        return True
    # ... render email/password form
    return False
```

### Persistence hooks in existing modules

- `forecast.py`: Replace `st.session_state["forecasts"]` writes with Supabase inserts (falls back to session state if unauthenticated)
- `portfolio.py`: Add `save_positions(user_id, positions)` and `load_positions(user_id)` via Supabase
- `app.py`: Add `render_auth_gate()` call before protected routes

### Backwards compatibility

Anonymous (unauthenticated) users continue to see the full public dashboard — all existing functionality preserved. Persistence features are additive, not a replacement. No regression risk to existing 454 checks.

---

## 7. Implementation Sequence

### Phase A: Supabase setup (Session 1, ~45 min, no code changes)
1. Create Supabase project at supabase.com (free tier)
2. Run schema SQL from Section 5 in the Supabase SQL editor
3. Enable email auth in Supabase dashboard
4. Copy `SUPABASE_URL` and `SUPABASE_ANON_KEY` to Streamlit Cloud secrets + local `.env`
5. Add `supabase` to `requirements.txt` (pin to `>=2.4.0`)
6. Add R-new regression check: `supabase` in requirements.txt

### Phase B: Auth layer (Session 1–2, ~2 hours)
1. Write `auth.py` module
2. Wire into `app.py` — protect routes for `standard`/`beta` plan tiers
3. Add login/signup UI (minimal — email + password, no social auth yet)
4. Regression: all 454 checks pass; new auth checks added

### Phase C: Forecast persistence (Session 2, ~1.5 hours)
1. Modify `forecast.py` — dual-write: session state (anonymous) + Supabase (authenticated)
2. Add `load_forecasts(user_id)` on login → restore prior session forecasts
3. Regression: existing forecast checks pass

### Phase D: Portfolio persistence (Session 3, ~2 hours)
1. Add `save_positions()` / `load_positions()` to `portfolio.py`
2. Wire into Portfolio Allocator page — auto-save on position change
3. Regression: all checks pass

### Phase E: Waitlist → onboarding flow (Session 3, ~1 hour)
1. Add waitlist signup form (email + price sensitivity question)
2. Write to `waitlist` table
3. Admin view in Supabase dashboard (no custom UI needed — Supabase has a built-in table viewer)
4. First beta invite: manual email to each waitlist entry

---

## 8. What Doesn't Need Supabase

| Feature | Why it doesn't need Supabase |
|---|---|
| Signal computation (RSI, Weinstein, momentum) | Stateless — computed fresh on every load |
| Market data fetching | Yahoo Finance / cached in st.cache_data |
| Top Movers | Computed from batch fetch, no per-user state |
| Global Intelligence signals | Stateless computation |
| Dashboard charts | Plotly, no persistence |

Supabase only touches: user identity, forecast history, portfolio positions, subscription status. Everything else stays as-is.

---

## 9. Cost Summary

| Phase | Supabase cost | Notes |
|---|---|---|
| Waitlist (0 users) | ₹0 | Google Sheets suffices, no Supabase needed |
| Beta (1–20 users) | ₹0 | Free tier covers this comfortably |
| Launch (1–200 subscribers) | ₹0 | Free tier: 50K MAU, 500MB storage |
| Scale (200–1,000 subscribers) | ₹0–₹2,100/month | Pro plan ($25/mo) only if storage approaches 8GB |
| Data licensing (if/when needed) | ₹2,400–₹4,200/month | Polygon.io Starter; offset by subscription revenue |

At 50 subscribers paying ₹499/month = ₹24,950 MRR. Supabase cost: ₹0. Net margin on infra: 100%.

---

## 10. Pre-Implementation Checklist (Premortem Gate)

Before writing any code for OPEN-003, the following must be true:

- [ ] Supabase project created and schema applied
- [ ] `SUPABASE_URL` and `SUPABASE_ANON_KEY` in Streamlit secrets AND local `.env`
- [ ] `.env` added to `.gitignore` (must not commit credentials)
- [ ] Sprint manifest written (`GSI_SPRINT_MANIFEST.json`) with token budget
- [ ] Regression baseline confirmed at 454 (or current passing count)
- [ ] Yahoo Finance ToS framing decision made (charge for the layer, not the data)
- [ ] GSI subscription pricing set (needed before any onboarding flow is built)

---

*Plan version: 1.0 — created session_032 (2026-05-18). Execute only after premortem gate above is fully checked.*

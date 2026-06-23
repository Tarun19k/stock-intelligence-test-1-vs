"""AlphaVeda waitlist signup page — revenue gate.
Run standalone: streamlit run alphaveda/waitlist_signup.py
Or integrated into app.py navigation as 'Early Access' page.
Writes to waitlist table on live Supabase.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from constants import SEBI_DISCLAIMER

st.set_page_config(
    page_title="AlphaVeda — Early Access",
    page_icon="📊",
    layout="centered",
)

# Pinned SEBI disclaimer — required on every page
st.markdown(f"""
<style>
  .sebi-disclaimer {{
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #fff3cd; color: #664d03;
    padding: 6px 16px; font-size: 11px;
    border-top: 1px solid #ffc107; z-index: 9999;
  }}
</style>
<div class="sebi-disclaimer">
  ⚠ {SEBI_DISCLAIMER}
</div>
""", unsafe_allow_html=True)

st.title("AlphaVeda — Early Access")
st.markdown(
    "**Confidence-scored, regime-aware signals for NSE/BSE portfolios.**  \n"
    "Built on 24-segment accuracy tracking. Not advice — research."
)

st.divider()
st.subheader("Join the waitlist")

with st.form("waitlist_form"):
    name = st.text_input("Name")
    email = st.text_input("Email *", placeholder="you@example.com")
    price_feedback = st.radio(
        "How does ₹999/month sound for confidence-scored signals?",
        options=["fair", "too_high", "too_low"],
        horizontal=True,
    )
    referred_by = st.text_input("How did you hear about AlphaVeda?", placeholder="Optional")
    submitted = st.form_submit_button("Join waitlist →")

if submitted:
    if not email or "@" not in email:
        st.error("Please enter a valid email address.")
    else:
        try:
            from supabase import create_client
            sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
            row = {
                "email": email.strip().lower(),
                "name": name.strip() if name else None,
                "price_feedback": price_feedback,
                "referred_by": referred_by.strip() if referred_by else None,
            }
            sb.table("waitlist").upsert(row, on_conflict="email").execute()
            st.success("You're on the list. We'll reach out when early access opens.")
            st.balloons()
        except Exception as e:
            st.error(f"Signup failed — please try again. ({e})")

st.divider()
st.caption(
    "AlphaVeda is a personal research tool. "
    "All outputs are for informational purposes only — not investment advice."
)

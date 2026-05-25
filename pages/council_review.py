# pages/council_review.py
# Depends on: config, utils
# Called from: app.py → "🏛️ Council Review" route
# Entry point: render_council_review(cur_sym, cb)
#
# GSI Council Review — 7-lens educational simulation + Synthesis Chair conflict arbiter.
# SEBI: Educational simulation only. Not investment advice. Not SEBI-registered.

import streamlit as st
from utils import sanitise

_SEBI_DISCLAIMER = (
    "Educational simulation only. Not investment advice. Not SEBI-registered. "
    "Do not make investment decisions based on this content."
)

_COUNCIL_INTRO = (
    "The Council Review applies 7 distinct investor frameworks to the same asset or portfolio. "
    "Each framework reflects a different analytical lens — value, macro, growth, risk-cycle, "
    "mental models, reflexivity, and asymmetric momentum. "
    "Where frameworks diverge significantly, the Synthesis Chair summarises the unresolved tension."
)

_PERSONAS = [
    {
        "id": "buffett",
        "name": "Warren Buffett",
        "lens": "Value · Moat · Owner Earnings",
        "icon": "🏦",
        "color": "#1a6b3c",
        "questions": [
            "Does this business have a durable competitive moat?",
            "Is the management allocating capital rationally?",
            "What is the intrinsic value vs. current price?",
            "Would I be comfortable holding this for 10 years?",
        ],
    },
    {
        "id": "munger",
        "name": "Charlie Munger",
        "lens": "Mental Models · Quality · Inversion",
        "icon": "🧠",
        "color": "#2d6a9f",
        "questions": [
            "What could go wrong? (Invert the thesis.)",
            "Is this a good business, or just a cheap one?",
            "What are the incentive structures for management?",
            "Is there latent complexity that will compound badly?",
        ],
    },
    {
        "id": "dalio",
        "name": "Ray Dalio",
        "lens": "Macro · Debt Cycle · All Weather",
        "icon": "🌐",
        "color": "#7b3fa0",
        "questions": [
            "Where are we in the long-term debt cycle?",
            "Is this asset positively or negatively correlated with inflation?",
            "Does this fit the current macroeconomic regime?",
            "What is the risk-adjusted return relative to gold/bonds?",
        ],
    },
    {
        "id": "lynch",
        "name": "Peter Lynch",
        "lens": "Growth · GARP · Ten-Bagger",
        "icon": "📈",
        "color": "#b85c00",
        "questions": [
            "Does the company have a simple, understandable story?",
            "Is the PEG ratio attractive for the growth rate?",
            "Is this a growth story that institutions haven't discovered yet?",
            "What is the earnings growth trajectory vs. valuation?",
        ],
    },
    {
        "id": "marks",
        "name": "Howard Marks",
        "lens": "Risk · Credit Cycle · Second-Level Thinking",
        "icon": "🎯",
        "color": "#8b0000",
        "questions": [
            "What is the consensus view — and where is the crowd wrong?",
            "Where are we in the risk/credit cycle?",
            "What is the downside scenario, and is it priced in?",
            "Is there a margin of safety for the risk being taken?",
        ],
    },
    {
        "id": "soros",
        "name": "George Soros",
        "lens": "Reflexivity · Regime Change · Macro Reversals",
        "icon": "🔄",
        "color": "#4a3728",
        "questions": [
            "Is the current narrative self-reinforcing (reflexivity)?",
            "Is there a regime change signal — fundamentals shifting the story?",
            "What is the feedback loop between price and perception?",
            "Is the market in boom-bust or correction mode?",
        ],
    },
    {
        "id": "druckenmiller",
        "name": "Stan Druckenmiller",
        "lens": "Asymmetric Momentum · Liquidity · Macro Sizing",
        "icon": "⚡",
        "color": "#0a4d6b",
        "questions": [
            "Is the liquidity environment supportive of this position?",
            "What is the asymmetric upside/downside — is the bet skewed right?",
            "Is there a catalyst that could move price significantly?",
            "At what size does this position make sense vs. portfolio risk?",
        ],
    },
]


def _render_header():
    st.markdown(
        '<h2 style="color:#c8d6f0;font-weight:700;margin-bottom:4px">'
        '🏛️ Council Review</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<span style="background:#1a2a1a;border:1px solid #00c853;'
        'color:#00c853;font-size:0.72rem;font-weight:700;'
        'padding:2px 8px;border-radius:4px;margin-right:8px">PRO</span>'
        '<span style="color:#8899aa;font-size:0.85rem">Multi-lens educational simulation</span>',
        unsafe_allow_html=True,
    )
    st.caption(_COUNCIL_INTRO)
    st.markdown(
        f'<div style="background:#1a1a1a;border:1px solid #ff8f00;'
        f'border-radius:6px;padding:8px 12px;margin:8px 0;'
        f'font-size:0.75rem;color:#ff8f00">'
        f'⚠️ {_SEBI_DISCLAIMER}</div>',
        unsafe_allow_html=True,
    )


def _render_mode_selector():
    mode = st.radio(
        "Analysis mode",
        ["Single Asset", "Portfolio Review", "Allocation Brief"],
        horizontal=True,
        label_visibility="collapsed",
    )
    return mode


def _render_asset_input(cur_sym: str) -> str:
    ticker = st.text_input(
        "Asset ticker or name",
        placeholder=f"e.g. RELIANCE.NS, INFY.NS, NIFTY50{cur_sym}",
        help="Enter a ticker symbol to frame the council questions around it.",
    ).strip()
    return sanitise(ticker) if ticker else ""


def _render_portfolio_input() -> str:
    portfolio = st.text_area(
        "Portfolio (one line per position: TICKER, %, notes)",
        placeholder="RELIANCE.NS, 20%, core holding\nHDFCBANK.NS, 15%, financial sector\nINFY.NS, 10%, tech exposure",
        height=140,
    ).strip()
    return portfolio


def _render_allocation_brief() -> str:
    brief = st.text_area(
        "Allocation brief (describe the thesis or allocation question)",
        placeholder="I am considering a 60% equity / 30% bond / 10% gold allocation. "
                    "India markets, 3-year horizon, moderate risk appetite.",
        height=100,
    ).strip()
    return brief


def _persona_card(persona: dict, subject: str, mode: str):
    color = persona["color"]
    name = persona["name"]
    icon = persona["icon"]
    lens = persona["lens"]
    questions = persona["questions"]

    subject_line = (
        f"**{subject}**" if subject
        else "_No asset specified — showing framework questions_"
    )

    with st.expander(f"{icon} {name} — {lens}", expanded=False):
        st.markdown(
            f'<div style="border-left:3px solid {color};'
            f'padding-left:10px;margin-bottom:8px">'
            f'<span style="color:#8899aa;font-size:0.78rem">'
            f'Algorithmically generated from quantitative signals. '
            f'Not a human analyst opinion.</span></div>',
            unsafe_allow_html=True,
        )

        if subject:
            st.markdown(
                f"**{name}'s lens applied to:** {subject_line}"
                f" _(educational framework only)_"
            )

        st.markdown("**Framework questions to consider:**")
        for q in questions:
            st.markdown(f"- {q}")

        st.markdown(
            f'<div style="font-size:0.72rem;color:#556677;margin-top:8px">'
            f'{_SEBI_DISCLAIMER}</div>',
            unsafe_allow_html=True,
        )


def _render_conflict_banner(subject: str):
    st.markdown(
        '<div style="background:#1a0a0a;border:1px solid #ff1744;'
        'border-radius:8px;padding:12px 16px;margin:12px 0">'
        '<div style="color:#ff1744;font-weight:700;font-size:0.9rem;margin-bottom:6px">'
        '⚡ Synthesis Chair — Framework Tension Detected</div>'
        '<div style="color:#c8d6f0;font-size:0.82rem">'
        'The value frameworks (Buffett / Munger) and the macro / reflexivity frameworks '
        '(Dalio / Soros) frequently produce directional disagreement on the same asset. '
        'Value says: price relative to intrinsic value. Macro says: regime and cycle position. '
        'These are not reconcilable — they answer different questions. '
        'Use both lenses independently, then decide which risk matters most to your horizon.'
        '</div>'
        '<div style="color:#8899aa;font-size:0.72rem;margin-top:8px">'
        'The Synthesis Chair does not produce a verdict. It surfaces the unresolved tension '
        'so you can make an informed judgment. '
        + _SEBI_DISCLAIMER +
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_council_grid(subject: str, mode: str):
    st.markdown("---")
    st.markdown("### 7-Lens Framework Review")
    st.caption(
        "Each card applies one investor's analytical framework to the subject. "
        "Expand to read the questions. "
        "Algorithmically generated educational content — not analyst opinions."
    )

    cols = st.columns(2)
    for i, persona in enumerate(_PERSONAS):
        with cols[i % 2]:
            _persona_card(persona, subject, mode)

    _render_conflict_banner(subject)


def render_council_review(cur_sym: str = "₹", cb: int = 0):
    _render_header()
    st.divider()

    mode = _render_mode_selector()
    st.markdown("---")

    subject = ""
    if mode == "Single Asset":
        subject = _render_asset_input(cur_sym)
        if subject:
            st.markdown(
                f'<div style="background:#0a1628;border:1px solid #2d5fa0;'
                f'border-radius:6px;padding:8px 12px;margin:8px 0;'
                f'font-size:0.82rem;color:#7ab3e0">'
                f'Applying 7 frameworks to: <strong>{subject}</strong></div>',
                unsafe_allow_html=True,
            )

    elif mode == "Portfolio Review":
        portfolio_text = _render_portfolio_input()
        if portfolio_text:
            lines = [l.strip() for l in portfolio_text.splitlines() if l.strip()]
            subject = f"{len(lines)}-position portfolio"
            st.markdown(
                f'<div style="background:#0a1628;border:1px solid #2d5fa0;'
                f'border-radius:6px;padding:8px 12px;margin:8px 0;'
                f'font-size:0.82rem;color:#7ab3e0">'
                f'Reviewing portfolio: <strong>{subject}</strong></div>',
                unsafe_allow_html=True,
            )

    elif mode == "Allocation Brief":
        brief_text = _render_allocation_brief()
        if brief_text:
            subject = "allocation thesis"
            st.markdown(
                '<div style="background:#0a1628;border:1px solid #2d5fa0;'
                'border-radius:6px;padding:8px 12px;margin:8px 0;'
                'font-size:0.82rem;color:#7ab3e0">'
                'Applying 7 frameworks to: <strong>allocation brief</strong></div>',
                unsafe_allow_html=True,
            )

    _render_council_grid(subject, mode)

    st.divider()
    st.caption(
        "🏛️ Council Review is an educational feature that applies documented investor "
        "frameworks as analytical lenses. It does not produce buy/sell signals. "
        + _SEBI_DISCLAIMER
    )

"""AlphaVeda design system — CSS tokens, typography, component styles.

Colour palette (Tarun-approved):
  indigo  #1A1F3C — brand dark, card surfaces
  gold    #E8A020 — brand accent, data values
  emerald #2D7A72 — bullish signals, positive indicators
  terra   #C0503A — bearish signals, negative indicators
  ivory   #F5F3EC — primary text on dark

Typography:
  Fraunces — display headings (optical serif, premium)
  DM Sans  — body text (clean, legible)
  DM Mono  — data values, prices, numeric tables
"""
from __future__ import annotations

_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;"
    "1,9..144,300&"
    "family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&"
    "family=DM+Mono:wght@400;500&"
    "display=swap"
)

_CSS = f"""
<style>
@import url('{_FONTS_URL}');

/* ── Design tokens ─────────────────────────────────────────────── */
:root {{
  --indigo:        #1A1F3C;
  --gold:          #E8A020;
  --emerald:       #2D7A72;
  --terra:         #C0503A;
  --ivory:         #F5F3EC;

  --bg-page:       #0D1020;
  --bg-card:       #1A1F3C;
  --bg-elevated:   #232844;
  --bg-sidebar:    #11142A;

  --text-primary:  #F5F3EC;
  --text-muted:    rgba(245, 243, 236, 0.55);
  --text-dim:      rgba(245, 243, 236, 0.30);
  --text-data:     #E8A020;

  --signal-bull:   #2D7A72;
  --signal-bull-fg:#4EADA5;
  --signal-bear:   #C0503A;
  --signal-bear-fg:#D9705A;

  --border:        rgba(245, 243, 236, 0.08);
  --border-gold:   rgba(232, 160, 32, 0.28);
  --border-focus:  rgba(232, 160, 32, 0.55);

  --font-display:  'Fraunces', Georgia, serif;
  --font-body:     'DM Sans', system-ui, sans-serif;
  --font-data:     'DM Mono', 'Courier New', monospace;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.40);
}}

/* ── App shell ─────────────────────────────────────────────────── */
.stApp {{
  background-color: var(--bg-page) !important;
  font-family: var(--font-body);
  color: var(--text-primary);
}}

.main .block-container {{
  max-width: 1100px;
  padding-top: 1.5rem;
  padding-bottom: 52px;   /* clear SEBI footer */
}}

/* ── Sidebar ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
  background-color: var(--bg-sidebar) !important;
  border-right: 1px solid var(--border) !important;
}}

[data-testid="stSidebar"] .stRadio > div {{
  gap: 4px;
}}

[data-testid="stSidebar"] .stRadio label {{
  display: block;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--text-muted);
  cursor: pointer;
  transition: background 180ms ease, color 180ms ease;
}}

[data-testid="stSidebar"] .stRadio label:hover {{
  background: rgba(245, 243, 236, 0.06);
  color: var(--text-primary);
}}

/* active nav item */
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio input:checked + div {{
  color: var(--gold);
  font-weight: 500;
}}

/* brand mark in sidebar */
[data-testid="stSidebar"]::before {{
  content: "AlphaVeda";
  display: block;
  padding: 20px 16px 12px;
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 300;
  font-style: italic;
  color: var(--gold);
  letter-spacing: 0.01em;
  border-bottom: 1px solid var(--border-gold);
  margin-bottom: 12px;
}}

/* ── Typography ────────────────────────────────────────────────── */
h1 {{
  font-family: var(--font-display);
  font-size: 1.875rem;
  font-weight: 300;
  font-style: italic;
  color: var(--ivory);
  letter-spacing: -0.01em;
  line-height: 1.2;
  margin-bottom: 0.25rem;
}}

h2 {{
  font-family: var(--font-display);
  font-size: 1.375rem;
  font-weight: 300;
  color: var(--ivory);
  line-height: 1.3;
}}

h3, h4 {{
  font-family: var(--font-body);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}}

p, .stMarkdown p {{
  font-family: var(--font-body);
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--text-primary);
}}

/* monospace data values */
code, pre, .stCode {{
  font-family: var(--font-data) !important;
  font-size: 0.875rem !important;
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  color: var(--gold) !important;
}}

/* ── Metrics ───────────────────────────────────────────────────── */
[data-testid="metric-container"] {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  box-shadow: var(--shadow-card);
}}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {{
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{
  font-family: var(--font-data);
  color: var(--ivory);
}}

/* ── Tables ────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
  font-family: var(--font-data);
  font-size: 0.8125rem;
}}

/* ── Selectbox / inputs ─────────────────────────────────────────── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {{
  background-color: var(--bg-elevated) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-body);
}}

/* ── Buttons ───────────────────────────────────────────────────── */
.stButton button {{
  font-family: var(--font-body);
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-gold);
  background: transparent;
  color: var(--gold);
  transition: background 180ms ease;
}}

.stButton button:hover {{
  background: rgba(232, 160, 32, 0.10);
}}

/* ── Status / info boxes ─────────────────────────────────────────── */
[data-testid="stAlert"] {{
  background: var(--bg-elevated);
  border-left-color: var(--gold);
  font-family: var(--font-body);
  border-radius: var(--radius-sm);
}}

/* ── SEBI footer bar ─────────────────────────────────────────────── */
.av-sebi-footer {{
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: var(--bg-sidebar);
  border-top: 1px solid var(--border-gold);
  padding: 5px 20px;
  font-family: var(--font-body);
  font-size: 0.6875rem;
  color: var(--text-muted);
  z-index: 9999;
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  gap: 8px;
}}

.av-sebi-footer::before {{
  content: "⚠";
  color: var(--gold);
  font-size: 0.75rem;
  flex-shrink: 0;
}}

/* ── Signal card ─────────────────────────────────────────────────── */
.av-signal-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 10px;
  box-shadow: var(--shadow-card);
  transition: border-color 200ms ease;
}}

.av-signal-card:hover {{
  border-color: var(--border-gold);
}}

.av-signal-chip {{
  display: inline-block;
  padding: 2px 9px;
  border-radius: var(--radius-sm);
  font-family: var(--font-body);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}}

.av-signal-chip.bull {{
  background: rgba(45, 122, 114, 0.18);
  color: var(--signal-bull-fg);
  border: 1px solid rgba(45, 122, 114, 0.35);
}}

.av-signal-chip.bear {{
  background: rgba(192, 80, 58, 0.18);
  color: var(--signal-bear-fg);
  border: 1px solid rgba(192, 80, 58, 0.35);
}}

.av-instrument {{
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 0.9375rem;
  color: var(--ivory);
}}

.av-kelly {{
  font-family: var(--font-data);
  font-size: 1.0625rem;
  color: var(--gold);
  letter-spacing: -0.01em;
}}

.av-lynch-class {{
  font-family: var(--font-body);
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: capitalize;
}}

.av-conf-track {{
  background: rgba(245, 243, 236, 0.07);
  border-radius: 2px;
  height: 3px;
  width: 100%;
  overflow: hidden;
  margin: 10px 0;
}}

.av-conf-fill {{
  height: 3px;
  border-radius: 2px;
}}

.av-conf-fill.bull {{
  background: linear-gradient(90deg, var(--emerald) 0%, #3FB8AE 100%);
}}

.av-conf-fill.bear {{
  background: linear-gradient(90deg, var(--terra) 0%, #D9705A 100%);
}}

/* ── Divider ─────────────────────────────────────────────────────── */
hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.25rem 0;
}}

/* ── Spinner / progress ──────────────────────────────────────────── */
[data-testid="stSpinner"] {{
  color: var(--gold) !important;
}}
</style>
"""


def get_css() -> str:
    """Return the full AlphaVeda CSS string for st.markdown injection."""
    return _CSS


def signal_card_html(
    instrument: str,
    direction: str,
    confidence: float,
    kelly_rupees: float | None,
    lynch_class: str,
) -> str:
    """Render a signal card as an HTML string.

    Args:
        instrument: Stock symbol or name (e.g. "RELIANCE").
        direction: "BULL" or "BEAR".
        confidence: Calibrated probability 0–100.
        kelly_rupees: Position size in rupees; None when suppressed (commercial gate).
        lynch_class: Lynch category (e.g. "fast_grower", "stalwart").
    """
    chip = "bull" if direction == "BULL" else "bear"
    kelly_str = f"₹{kelly_rupees:,.0f}" if kelly_rupees is not None else "—"
    conf_pct = max(0, min(100, int(confidence)))
    class_label = lynch_class.replace("_", " ").title()
    return (
        f'<div class="av-signal-card">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
        f'<span class="av-instrument">{instrument}</span>'
        f'<span class="av-signal-chip {chip}">{direction}</span>'
        f"</div>"
        f'<div class="av-conf-track">'
        f'<div class="av-conf-fill {chip}" style="width:{conf_pct}%;"></div>'
        f"</div>"
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span class="av-lynch-class">{class_label}</span>'
        f'<span class="av-kelly">{kelly_str}</span>'
        f"</div>"
        f"</div>"
    )

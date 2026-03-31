# pages/observability.py
# Depends on: market_data, config, version
# Entry point: render_observability() — called from app.py routing (direct URL only)
#
# Founder-only internal page. Not in public nav — hidden via existing CSS.
# Access: gated by st.secrets["DEV_TOKEN"] + PIN entry.
# Two tabs:
#   App Health  — live cache warmth, rate-limit state, hit/miss ratios, latency
#   Program     — sprint velocity, open items, audit counts, compliance status

import re
import json
import os
import pytz
from datetime import datetime

import streamlit as st

from config import MARKET_SESSIONS, CURRENT_VERSION
from market_data import get_health_stats, get_rate_limit_state, is_ticker_cache_warm
from version import VERSION_LOG

# ── Gate helpers ───────────────────────────────────────────────────────────────

def _get_dev_token() -> str:
    try:
        return st.secrets.get("DEV_TOKEN", "")
    except Exception:
        return ""


def _render_gate() -> bool:
    """Show PIN entry. Returns True when unlocked."""
    st.markdown("### App internals")
    st.caption("This page is not public.")
    pin = st.text_input("Access code", type="password", key="obs_pin_input")
    if st.button("Unlock", key="obs_unlock_btn"):
        token = _get_dev_token()
        if token and pin == token:
            st.session_state["obs_unlocked"] = True
            st.rerun()
        else:
            st.error("Wrong code.")
    return False


# ── Market status helpers ──────────────────────────────────────────────────────

def _market_status_rows() -> list:
    """Return list of (market, tz, open_time, close_time, is_open) tuples."""
    rows = []
    for market, sess in MARKET_SESSIONS.items():
        tz_name = sess.get("tz", "UTC")
        tz      = pytz.timezone(tz_name)
        now     = datetime.now(tz)
        if now.weekday() >= 5:
            rows.append((market, tz_name, sess["open"], sess["close"], False))
            continue
        o_h, o_m = sess["open"]
        c_h, c_m = sess["close"]
        open_dt  = now.replace(hour=o_h, minute=o_m, second=0, microsecond=0)
        close_dt = now.replace(hour=c_h, minute=c_m, second=0, microsecond=0)
        is_open  = open_dt <= now < close_dt
        rows.append((market, tz_name, sess["open"], sess["close"], is_open))
    return rows


# ── Tab: App Health ────────────────────────────────────────────────────────────

@st.fragment(run_every=10)
def _tab_app_health() -> None:
    st.caption("Refreshes every 10 seconds.")

    stats = get_health_stats()
    rl    = get_rate_limit_state()

    # Row 1 — rate limit + cache warmth
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Rate limit",
        "cooling down" if rl["in_cooldown"] else "clear",
        delta=f"{rl['seconds_remaining']}s left" if rl["in_cooldown"] else None,
        delta_color="inverse",
    )
    c2.metric("Consecutive 429s", rl["consecutive_429s"])
    c3.metric("Cache entries",    stats["cache_size"])
    c4.metric(
        "Cache hit rate",
        f"{stats['hit_rate_pct']}%",
        delta=f"{stats['cache_hits']} hits / {stats['cache_misses']} misses",
    )

    st.divider()

    # Row 2 — fetch latency
    c5, c6 = st.columns(2)
    c5.metric("Avg fetch time",  f"{stats['avg_fetch_ms']} ms")
    c6.metric("P95 fetch time",  f"{stats['p95_fetch_ms']} ms")

    samples = stats["latency_samples"]
    if samples:
        import plotly.graph_objects as go
        fig = go.Figure(go.Scatter(
            y=samples,
            mode="lines+markers",
            line={"color": "#4C9BE8", "width": 1.5},
            marker={"size": 4},
            name="fetch ms",
        ))
        fig.update_layout(
            title="Fetch latency: last 20 samples (ms)",
            height=200,
            margin={"t": 36, "b": 24, "l": 32, "r": 8},
            yaxis_title="ms",
            xaxis_title="sample",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e0e0e0", "size": 11},
        )
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    st.divider()

    # Row 3 — error counts
    errors = stats["error_counts"]
    st.markdown(f"**Fetch errors: {stats['total_errors']} total**")
    if errors:
        err_rows = sorted(errors.items(), key=lambda x: x[1], reverse=True)
        cols = st.columns(min(4, len(err_rows)))
        for i, (sym, cnt) in enumerate(err_rows[:8]):
            cols[i % len(cols)].metric(sym, cnt)
    else:
        st.caption("No fetch errors recorded this session.")

    st.divider()

    # Row 4 — market open/closed status
    st.markdown("**Market sessions**")
    market_rows = _market_status_rows()
    hdr_cols = st.columns([2, 2, 1, 1, 1])
    hdr_cols[0].caption("Market")
    hdr_cols[1].caption("Timezone")
    hdr_cols[2].caption("Open")
    hdr_cols[3].caption("Close")
    hdr_cols[4].caption("Status")
    for market, tz_name, open_t, close_t, is_open in market_rows:
        row = st.columns([2, 2, 1, 1, 1])
        row[0].write(market)
        row[1].caption(tz_name)
        row[2].caption(f"{open_t[0]:02d}:{open_t[1]:02d}")
        row[3].caption(f"{close_t[0]:02d}:{close_t[1]:02d}")
        row[4].write("OPEN" if is_open else "closed")


# ── Tab: Program ───────────────────────────────────────────────────────────────

def _read_file_safe(path: str) -> str:
    """Read a repo-root governance doc. Returns empty string if missing."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _parse_audit_counts(text: str) -> dict:
    """Count audit finding statuses from GSI_AUDIT_TRAIL.md."""
    fixed   = len(re.findall(r"\bFIXED\b",   text))
    partial = len(re.findall(r"\bPARTIAL\b", text))
    open_   = len(re.findall(r"\bOPEN\b",    text))
    return {"fixed": fixed, "partial": partial, "open": open_,
            "total": fixed + partial + open_}


def _parse_risk_counts(text: str) -> dict:
    """Count risk statuses from GSI_RISK_REGISTER.md."""
    mitigated = len(re.findall(r"\bMitigated\b", text, re.IGNORECASE))
    open_     = len(re.findall(r"\bOpen\b",      text, re.IGNORECASE))
    return {"mitigated": mitigated, "open": open_}


def _parse_sprint_velocity(text: str) -> list:
    """Extract sprint rows from GSI_SPRINT.md Done section. Returns list of dicts."""
    pattern = r"\|\s*(v\d+\.\d+[^\|]*?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
    rows    = []
    for m in re.finditer(pattern, text):
        rows.append({
            "sprint":   m.group(1).strip(),
            "planned":  int(m.group(2)),
            "delivered": int(m.group(3)),
        })
    return rows[-8:]  # last 8 sprints max


def _inline_compliance_check() -> dict:
    """Run the 8 compliance checks inline. Returns dict of name → bool."""
    try:
        db  = _read_file_safe("dashboard.py")
        gi  = _read_file_safe("pages/global_intelligence.py")
        md  = _read_file_safe("market_data.py")
        ind = _read_file_safe("indicators.py")
        return {
            "SEBI disclaimer":         "SEBI-registered investment advisor" in db,
            "Algo disclosure":         "algorithmically generated" in db.lower(),
            "No raw score":            "Momentum: {score}/100" not in db,
            "No red flags fallback":   '"No major red flags at this time."' not in db,
            "ROE null guard":          "roe_str" in db,
            "Next steps removed":      len(re.findall(r"(?<!def )_render_next_steps_ai\(\)", gi)) == 0,
            "RATES CONTEXT":           "RATES CONTEXT" in ind,
            "Rate limit gate":         "_is_rate_limited()" in md,
        }
    except Exception:
        return {}


def _tab_program() -> None:
    # Sprint manifest
    manifest_text = _read_file_safe("GSI_SPRINT_MANIFEST.json")
    if manifest_text:
        try:
            manifest = json.loads(manifest_text)
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Sprint",  manifest.get("sprint", "—"))
            mc2.metric("Status",  manifest.get("status", "—"))
            mc3.metric("Baseline checks", manifest.get("baseline_before", "—"))
            checks      = manifest.get("checks", [])
            tier_a      = [c for c in checks if c.get("tier") == "A"]
            tier_b      = [c for c in checks if c.get("tier") == "B"]
            st.caption(f"{len(tier_a)} Tier A gates · {len(tier_b)} Tier B checks · "
                       f"{len(manifest.get('file_change_log', []))} files logged")
        except Exception:
            st.caption("Manifest present but could not parse.")
    else:
        st.caption("No sprint manifest found.")

    st.divider()

    # Audit trail counts
    audit_text = _read_file_safe("GSI_AUDIT_TRAIL.md")
    audit      = _parse_audit_counts(audit_text)
    st.markdown("**Audit trail**")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Fixed",   audit["fixed"])
    a2.metric("Partial", audit["partial"])
    a3.metric("Open",    audit["open"])
    a4.metric("Total",   audit["total"])

    st.divider()

    # Risk register counts
    risk_text = _read_file_safe("GSI_RISK_REGISTER.md")
    risk      = _parse_risk_counts(risk_text)
    st.markdown("**Risk register**")
    r1, r2 = st.columns(2)
    r1.metric("Mitigated", risk["mitigated"])
    r2.metric("Open",      risk["open"])

    st.divider()

    # Sprint velocity chart
    sprint_text = _read_file_safe("GSI_SPRINT.md")
    velocity    = _parse_sprint_velocity(sprint_text)
    st.markdown("**Sprint velocity**")
    if velocity:
        import plotly.graph_objects as go
        labels    = [r["sprint"]    for r in velocity]
        planned   = [r["planned"]   for r in velocity]
        delivered = [r["delivered"] for r in velocity]
        fig = go.Figure()
        fig.add_bar(x=labels, y=planned,   name="planned",   marker_color="#4a4a6a")
        fig.add_bar(x=labels, y=delivered, name="delivered", marker_color="#4C9BE8")
        fig.update_layout(
            barmode="group",
            height=220,
            margin={"t": 16, "b": 24, "l": 32, "r": 8},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e0e0e0", "size": 11},
            legend={"orientation": "h", "y": 1.1},
        )
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
    else:
        st.caption("No velocity data found in GSI_SPRINT.md.")

    st.divider()

    # Inline compliance check
    st.markdown("**Compliance check** (8 gates)")
    results = _inline_compliance_check()
    if results:
        fails = [name for name, ok in results.items() if not ok]
        passed = len(results) - len(fails)
        if fails:
            st.error(f"{passed}/{len(results)} checks passed")
            for name in fails:
                st.write(f"FAIL: {name}")
        else:
            st.success(f"{passed}/{len(results)} — all clear")
    else:
        st.caption("Could not run compliance check.")

    # Version log — last 5
    st.divider()
    st.markdown("**Recent versions**")
    for entry in reversed(VERSION_LOG[-5:]):
        st.markdown(f"**{entry['version']}** · {entry['date']}")
        st.caption(entry["notes"][:200])


# ── Public entry point ─────────────────────────────────────────────────────────

def render_observability() -> None:
    """
    Founder-only observability page.
    Gated by st.secrets['DEV_TOKEN'] PIN entry.
    Not imported by app.py — accessed via Streamlit MPA direct URL.
    """
    st.title("App internals")
    st.caption(f"v{CURRENT_VERSION}")

    if not st.session_state.get("obs_unlocked"):
        _render_gate()
        return

    tab_health, tab_program = st.tabs(["App Health", "Program"])

    with tab_health:
        _tab_app_health()

    with tab_program:
        _tab_program()

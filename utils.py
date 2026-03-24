# utils.py
import html
import re
import traceback
from collections import deque
from datetime import datetime
import streamlit as st


def log_error(context: str, exc: Exception):
    entry = {
        "time":    datetime.now().strftime("%H:%M:%S"),
        "context": context,
        "error":   type(exc).__name__,
        "detail":  str(exc)[:120],
        "trace":   traceback.format_exc()[-300:],
    }
    if "app_error_log" in st.session_state:
        st.session_state.app_error_log.appendleft(entry)


def safe_run(fn, context: str = "", default=None):
    try:
        return fn()
    except Exception as e:
        log_error(context, e)
        return default


def safe_float(val, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def sanitise(text: str, max_len: int = 200) -> str:
    """Escape HTML special chars before injecting into unsafe_allow_html blocks."""
    if not isinstance(text, str):
        return ""
    text = text[:max_len]
    return html.escape(text)



def sanitise_bold(text: str, max_len: int = 400) -> str:
    """
    Like sanitise() but preserves <b> and </b> for emphasis in insight cards.
    Process:  escape ALL HTML first → restore only <b> and </b>.
    This is XSS-safe because insight strings are built from numeric values,
    never from user input.
    """
    import html
    escaped = html.escape(str(text))[:max_len]
    # Restore only the safe bold pair — nothing else
    escaped = escaped.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    return escaped

def safe_ticker_key(ticker: str) -> str:
    """Sanitise ticker before use as dict/JSON key. Allows A-Za-z0-9.-^= only."""
    return re.sub(r"[^A-Za-z0-9.\-^=]", "", str(ticker))[:20]


def safe_url(url: str) -> bool:
    """Validate URL is http/https and not pointing at internal/local network."""
    from urllib.parse import urlparse
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            return False
        host = p.netloc.lower()
        blocked = ("localhost", "127.", "192.168.", "10.", "0.0.0.0", "::1")
        return not any(host.startswith(b) for b in blocked)
    except Exception:
        return False


def init_session_state():
    defaults = {
        "app_error_log": deque(maxlen=50),
        "chatter_open":  True,
        "chatter_topic": "Global Markets",
        "chatter_feeds": [],
        "cb":            0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_error_log():
    log = list(st.session_state.get("app_error_log", []))
    if not log:
        return
    with st.expander(f"⚠️ Error log ({len(log)})", expanded=False):
        for e in log[:10]:
            st.markdown(
                f'<div style="font-size:0.72rem;color:#ff7043;' +
                f'border-left:2px solid #ff7043;padding:4px 8px;' +
                f'margin-bottom:4px;background:#1a0a0a;color:#ffb3b3;border-radius:4px">' +
                f'<b>{sanitise(e["time"])}</b> · {sanitise(e["context"])} · ' +
                f'{sanitise(e["error"])}: {sanitise(e["detail"])}</div>',
                unsafe_allow_html=True,
            )


def responsive_cols(desktop: int, tablet: int = None, mobile: int = 1):
    # tablet/mobile params reserved for future responsive breakpoint logic — currently unused.
    return st.columns(desktop)


def info_tip(label: str, tip: str) -> str:
    """Label + ℹ️ icon with native HTML title= tooltip (no JS, XSS-safe).
    Use inside unsafe_allow_html=True markdown blocks only.
    Example: st.markdown(info_tip("RSI 14", HELP_TEXT["rsi"]), unsafe_allow_html=True)
    """
    safe_tip   = html.escape(str(tip))[:400]
    safe_label = html.escape(str(label))[:80]
    icon = (
        f'<span title="{safe_tip}" '
        f'style="cursor:help;margin-left:4px;font-size:0.7rem;'
        f'color:#4b6080;vertical-align:super;">&#9432;</span>'
    ) if tip else ""
    return f'<span title="{safe_tip}" style="cursor:help;">{safe_label}</span>{icon}'


def section_title_with_tip(title: str, tip: str) -> str:
    """<p class=section-title> with inline ℹ️ tooltip. Drop-in for bare section titles.
    Example: st.markdown(section_title_with_tip("KPI Panel", HELP_TEXT["score"]),
                         unsafe_allow_html=True)
    """
    safe_tip   = html.escape(str(tip))[:400]
    safe_title = html.escape(str(title))[:80]
    return (
        f'<p class="section-title">{safe_title}'
        f'<span title="{safe_tip}" '
        f'style="cursor:help;margin-left:6px;font-size:0.72rem;'
        f'color:#4b6080;font-weight:400;vertical-align:middle;">&#9432;</span></p>'
    )

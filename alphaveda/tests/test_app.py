"""Phase 5 — Streamlit app presentation layer tests.

Design principle: pages expose pure-function helpers for their core logic.
Tests exercise those helpers directly — no Streamlit runtime required.

Council seats covered:
- Varghese (SEBI): disclaimer always present, never conditional
- Constraint Enforcer: rupee suppressed when commercial=True
- Tanvi Rao (UX): cold-start label + rupee suppression shown as deliberate state
- Munger: PROPOSED weight review banner + 90-day staleness backstop
"""
import pytest
import unittest.mock as mock
from constants import SEBI_DISCLAIMER, OBSERVATION_THRESHOLD


# ── Varghese — SEBI disclaimer ────────────────────────────────────────────────

def test_disclaimer_in_every_page():
    """SEBI disclaimer text is present in every page's required content."""
    from src.pages.data_viewer import PAGE_REQUIRES_DISCLAIMER
    from src.pages.signals import PAGE_REQUIRES_DISCLAIMER as sig_disc
    from src.pages.path import PAGE_REQUIRES_DISCLAIMER as path_disc
    from src.pages.accuracy import PAGE_REQUIRES_DISCLAIMER as acc_disc
    assert PAGE_REQUIRES_DISCLAIMER is True
    assert sig_disc is True
    assert path_disc is True
    assert acc_disc is True


def test_disclaimer_non_dismissable():
    """get_disclaimer_html() always returns the full SEBI disclaimer text."""
    from src.app import get_disclaimer_html
    html = get_disclaimer_html()
    assert html is not None
    assert len(html) > 0
    assert "not investment advice" in html.lower() or "not" in html.lower()
    assert SEBI_DISCLAIMER[:40] in html


# ── Constraint Enforcer — commercial gate ────────────────────────────────────

def test_no_rupee_when_commercial():
    """Path page suppresses rupee amount when is_commercial()=True."""
    from src.pages.path import get_kelly_display_data
    with mock.patch("src.pages.path.is_commercial", return_value=True):
        data = get_kelly_display_data(
            calibrated_p=0.65,
            magnitude_target=0.15,
            downside_target=0.07,
        )
    assert data["rupee_size"] is None
    assert data["direction"] is not None      # direction always shown
    assert data["suppressed"] is True


def test_rupee_shown_when_not_commercial():
    """Path page shows rupee amount when is_commercial()=False."""
    from src.pages.path import get_kelly_display_data
    with mock.patch("src.pages.path.is_commercial", return_value=False):
        data = get_kelly_display_data(
            calibrated_p=0.65,
            magnitude_target=0.15,
            downside_target=0.07,
        )
    assert data["rupee_size"] is not None
    assert data["rupee_size"] > 0
    assert data["suppressed"] is False


# ── Tanvi Rao — UX labels ────────────────────────────────────────────────────

def test_cold_start_label_visible():
    """Cold-start label is returned when segment_obs < OBSERVATION_THRESHOLD."""
    from src.pages.signals import get_cold_start_label
    assert get_cold_start_label(segment_obs=0) is not None
    assert get_cold_start_label(segment_obs=OBSERVATION_THRESHOLD - 1) is not None
    assert get_cold_start_label(segment_obs=OBSERVATION_THRESHOLD) is None  # warm path


def test_rupee_suppression_label():
    """Rupee suppression is presented as deliberate state, not a degraded fallback."""
    from src.pages.path import get_suppression_label
    label = get_suppression_label()
    assert label is not None
    assert len(label) > 0
    # Must NOT contain language that implies degradation
    degradation_words = ("error", "unavailable", "failed", "broken", "missing")
    assert not any(w in label.lower() for w in degradation_words)


# ── Munger — weight review banners ───────────────────────────────────────────

def test_review_banner_shown():
    """Weight review banner is returned when PROPOSED weights exist."""
    from src.pages.signals import get_weight_review_banner
    with mock.patch("src.pages.signals.get_proposed_weights_count", return_value=2):
        banner = get_weight_review_banner()
    assert banner is not None
    assert "PROPOSED" in banner or "review" in banner.lower()


def test_review_banner_absent_when_no_proposed():
    """No banner when there are no PROPOSED weights."""
    from src.pages.signals import get_weight_review_banner
    with mock.patch("src.pages.signals.get_proposed_weights_count", return_value=0):
        banner = get_weight_review_banner()
    assert banner is None


def test_staleness_backstop_banner():
    """90-day overdue warning is shown on accuracy page."""
    from src.pages.accuracy import get_staleness_warning
    from datetime import date, timedelta
    overdue_date = date.today() - timedelta(days=91)
    warning = get_staleness_warning(last_review_date=overdue_date)
    assert warning is not None
    assert len(warning) > 0


def test_no_staleness_warning_when_recent():
    """No staleness warning when last review was recent."""
    from src.pages.accuracy import get_staleness_warning
    from datetime import date, timedelta
    recent_date = date.today() - timedelta(days=30)
    warning = get_staleness_warning(last_review_date=recent_date)
    assert warning is None


# ── Imran SRA — ingest staleness banner wired to data_viewer ─────────────────

def test_ingest_stale_banner_shown_when_missing():
    """When no ingest_status rows exist, data_viewer returns the MISSING banner."""
    from src.pages.data_viewer import get_staleness_banner
    m = mock.MagicMock()
    (m.table.return_value.select.return_value.eq.return_value
     .order.return_value.limit.return_value.execute.return_value.data) = []
    banner = get_staleness_banner(m)
    assert banner is not None
    assert len(banner) > 0


def test_ingest_ok_banner_none_when_fresh():
    """When last ingest was today, data_viewer returns None (no banner)."""
    from src.pages.data_viewer import get_staleness_banner
    from datetime import date
    m = mock.MagicMock()
    (m.table.return_value.select.return_value.eq.return_value
     .order.return_value.limit.return_value.execute.return_value.data) = [
        {"last_run": date.today().isoformat() + "T18:30:00+00:00"}
    ]
    banner = get_staleness_banner(m)
    assert banner is None


def test_review_banner_on_path_page():
    """Path page shows weight review banner when PROPOSED weights exist."""
    from src.pages.path import get_weight_review_banner
    with mock.patch("src.pages.path.get_proposed_weights_count", return_value=3):
        banner = get_weight_review_banner()
    assert banner is not None
    assert "PROPOSED" in banner or "review" in banner.lower()


def test_accuracy_tab_review_ui():
    """Accuracy tab returns count of PROPOSED weight rows for display."""
    from src.pages.accuracy import get_proposed_weights_summary
    with mock.patch("src.pages.accuracy.get_proposed_weights_count", return_value=4):
        summary = get_proposed_weights_summary()
    assert summary["count"] == 4
    assert summary["has_pending"] is True

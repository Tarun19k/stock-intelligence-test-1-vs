"""Session A API tests — FastAPI transport layer.

Uses FastAPI TestClient (no live Fly.io needed).
All 186 existing tests must remain green alongside these.

Milestone gates (Session A sign-off):
- health returns 200 + ohlcv_rows > 0
- sebi_disclaimer present in every response
- No BUY/SELL/invest prohibited language
- CORS blocks non-Vercel origins
"""
from __future__ import annotations
import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in this environment")

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app, raise_server_exceptions=True)

ALL_ENDPOINTS = ["/market-data", "/signals", "/path", "/accuracy"]


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_200():
    r = client.get("/health")
    assert r.status_code == 200


def test_health_has_real_data():
    """ohlcv_rows > 0 required — HTTP 200 alone is not sufficient."""
    r = client.get("/health")
    assert r.json()["ohlcv_rows"] > 0, (
        "health endpoint returned ohlcv_rows=0 — G0 seed missing or ingest failed"
    )


def test_health_has_last_ingest():
    r = client.get("/health")
    assert r.json()["last_ingest"] is not None, "No OK ingest_status row found"


# ── SEBI envelope ─────────────────────────────────────────────────────────────

def test_sebi_disclaimer_on_every_endpoint():
    for path in ALL_ENDPOINTS:
        r = client.get(path)
        body = r.json()
        assert "sebi_disclaimer" in body, f"sebi_disclaimer missing from {path}"
        disclaimer = body["sebi_disclaimer"]
        assert "NOT investment advice" in disclaimer or "not investment advice" in disclaimer.lower(), \
            f"sebi_disclaimer on {path} missing 'NOT investment advice'"
        assert "research" in disclaimer.lower(), \
            f"sebi_disclaimer on {path} missing 'research'"


def test_as_of_on_every_endpoint():
    for path in ALL_ENDPOINTS:
        r = client.get(path)
        assert "as_of" in r.json(), f"as_of missing from {path}"


# ── Prohibited language ───────────────────────────────────────────────────────

PROHIBITED = ["BUY", "SELL", "invest in", "put money", "you should", "recommended for you"]


def test_no_prohibited_language():
    for path in ALL_ENDPOINTS:
        text = str(client.get(path).json())
        for word in PROHIBITED:
            assert word not in text, f"Prohibited term '{word}' found in {path} response"


# ── CORS ──────────────────────────────────────────────────────────────────────

def test_cors_allows_localhost():
    r = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_allows_vercel_domain():
    r = client.get("/health", headers={"Origin": "https://alphaveda-web.vercel.app"})
    assert r.headers.get("access-control-allow-origin") == "https://alphaveda-web.vercel.app"


def test_cors_blocks_external_origin():
    r = client.get("/health", headers={"Origin": "https://evil.com"})
    origin_header = r.headers.get("access-control-allow-origin", "")
    assert origin_header != "https://evil.com", "CORS allowed a non-Vercel origin"


# ── Commercial gate ───────────────────────────────────────────────────────────

def test_path_has_suppression_fields():
    """Path endpoint must always expose suppressed and commercial fields."""
    r = client.get("/path")
    data = r.json()["data"]
    assert "suppressed" in data
    assert "commercial" in data


def test_path_rupee_size_null_when_suppressed():
    """If suppressed=True, rupee_size must be null (never a number)."""
    r = client.get("/path")
    data = r.json()["data"]
    if data["suppressed"]:
        assert data["rupee_size"] is None, "rupee_size must be null when suppressed=True"


# ── Market data ───────────────────────────────────────────────────────────────

def test_market_data_returns_list():
    r = client.get("/market-data")
    assert isinstance(r.json()["data"], list)


def test_market_data_has_instruments():
    r = client.get("/market-data")
    assert len(r.json()["data"]) > 0, "market-data returned empty list — instruments not seeded"


def test_market_data_has_required_fields():
    r = client.get("/market-data")
    for item in r.json()["data"]:
        assert "ticker" in item
        assert "classification" in item

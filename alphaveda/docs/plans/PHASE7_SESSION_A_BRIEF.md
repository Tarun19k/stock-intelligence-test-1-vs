# Phase 7 — Session A Execution Brief (FastAPI on Railway)
# Status: READY — waiting on Tarun Pre-work (Railway account + CLI)
# Last updated: 2026-06-28

---

## Goal

Wrap existing `src/` logic in FastAPI. Deploy to Railway. **No logic changes to `src/`.**

The transport layer changes. The brain stays the same.

## Pre-work Gate (Tarun-owned — blocks Session A)

| Item | Owner | Done? |
|---|---|---|
| Create Railway account at railway.app | Tarun | [ ] |
| Create project named `alphaveda-api` in Railway dashboard | Tarun | [ ] |
| Install Railway CLI: `sudo npm install -g @railway/cli` then `railway login` | Tarun | [ ] |
| Install Vercel CLI: `sudo npm install -g vercel` then `vercel login` | Tarun | [ ] |
| Create Vercel project linked to GSI repo, named `alphaveda-web` | Tarun | [ ] |

Once all 5 are done → CoS builds Session A in one session (~4–6 hours).

---

## Directory structure to create

```
alphaveda/
  api/
    __init__.py
    main.py          # FastAPI app, CORS config
    models.py        # Pydantic response models + SEBI envelope
    routes/
      __init__.py
      health.py
      market_data.py
      signals.py
      path.py
      accuracy.py
  railway.toml       # build + start commands
  requirements-api.txt
```

---

## api/main.py — CORS locked to Vercel domains only

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import health, market_data, signals, path, accuracy
import os
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"), override=False)
except ImportError:
    pass

app = FastAPI(title="AlphaVeda API", version="0.1.0")

# CORS: locked to Vercel domains only. Never allow_origins=['*'].
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://alphaveda.*\.vercel\.app|http://localhost:3000",
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(market_data.router, prefix="/market-data")
app.include_router(signals.router, prefix="/signals")
app.include_router(path.router, prefix="/path")
app.include_router(accuracy.router, prefix="/accuracy")
```

---

## api/models.py — SEBI envelope (every response)

```python
from pydantic import BaseModel
from datetime import date
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from constants import SEBI_DISCLAIMER

class ApiEnvelope(BaseModel):
    data: dict | list
    sebi_disclaimer: str = SEBI_DISCLAIMER
    as_of: date
    # sebi_disclaimer is the single source of truth — constants.py.
    # Frontend renders this string, never its own copy.
    # Text cannot drift between Python and TypeScript.
```

---

## GET /health — gate verification

```python
@router.get("/health")
def health_check():
    sb = get_supabase_client()
    ohlcv_count = sb.table("ohlcv").select("id", count="exact").execute().count
    ingest_ok = (sb.table("ingest_status")
                   .select("last_run")
                   .eq("status", "OK")
                   .limit(1)
                   .execute().data)
    return {
        "status": "ok",
        "ohlcv_rows": ohlcv_count,
        "last_ingest": ingest_ok[0]["last_run"] if ingest_ok else None,
        "timestamp": datetime.utcnow().isoformat()
    }
# Gate: ohlcv_rows must be > 0 for Session A milestone to pass.
# HTTP 200 with ohlcv_rows=0 counts as a FAIL.
```

---

## railway.toml

```toml
[build]
buildCommand = "pip install -r requirements-api.txt"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```

---

## requirements-api.txt (new file)

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
pydantic>=2.7.0
supabase>=2.4.0
python-dotenv
pandas
numpy
scipy
```

---

## Commercial gate flow through API

1. `GET /path` calls `is_commercial()` from `src/config.py` — unchanged, fail-closed.
2. If `commercial=True`: `{suppressed: true, direction: "BULLISH", rupee_size: null}`
3. If `commercial=False`: `{suppressed: false, direction: "BULLISH", rupee_size: 72450.0}`
4. Frontend never calls `is_commercial()` — server-side only, always.
5. Fail-closed: Supabase unreachable → commercial=True → rupees suppressed.

---

## Backend tests — alphaveda/tests/test_api.py (new file)

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_returns_200_with_real_data():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ohlcv_rows"] > 0   # not just HTTP 200 — real data must be present

def test_sebi_envelope_on_every_endpoint():
    for path in ["/market-data", "/signals", "/path", "/accuracy"]:
        r = client.get(path)
        body = r.json()
        assert "sebi_disclaimer" in body
        assert "NOT investment advice" in body["sebi_disclaimer"] or \
               "research purposes only" in body["sebi_disclaimer"]

def test_no_prohibited_language():
    for path in ["/market-data", "/signals", "/path", "/accuracy"]:
        text = str(client.get(path).json())
        for word in ["BUY", "SELL", "invest in", "put money", "you should"]:
            assert word not in text

def test_cors_locked():
    # Non-Vercel origin must be blocked
    r = client.get("/health", headers={"Origin": "https://evil.com"})
    assert "access-control-allow-origin" not in r.headers or \
           r.headers.get("access-control-allow-origin") != "https://evil.com"
```

---

## Async vs sync Supabase decision (pre-Session A)

**Decision: use sync client (`supabase-py`) for Phase 7.**

Rationale: all `src/` logic is sync. Wrapping in `async def` handlers requires
`run_in_executor()` everywhere, adding complexity with no benefit. FastAPI handles
sync route handlers correctly via thread pool offloading. Revisit at G1 if Railway
concurrency becomes a bottleneck.

**Implementation:** All FastAPI route handlers defined as `def` (not `async def`).

---

## Session A milestone verification

- [ ] `railway up` completes without error
- [ ] `curl https://[railway-url]/health` → HTTP 200, `ohlcv_rows: 13`
- [ ] `curl https://[railway-url]/market-data` → 14 instruments
- [ ] `curl https://[railway-url]/signals` → cold-start label, SEBI envelope present
- [ ] `pytest alphaveda/tests/test_api.py` → all pass
- [ ] No `allow_origins=['*']` anywhere in api/
- [ ] SEBI disclaimer string in every response envelope
- [ ] No BUY/SELL/invest language in any endpoint response
- [ ] `pytest alphaveda/tests/` → still 186 PASS / 0 FAIL (existing suite untouched)

---

## DO NOT CHANGE — survives Phase 7 unchanged

- `src/signals/engine.py` — emit pipeline contract
- `src/signals/weights.py` — Buffett floor + DB validation
- `src/portfolio/optimizer.py` — Kelly formula (GAP-001 fix)
- `src/ingest/resolve_outcomes.py` — circuit_flag exclusion
- `constants.py` — all constants including SEBI_DISCLAIMER
- `src/config.py` — is_commercial() fail-closed logic
- All 186 existing tests must stay green throughout all Phase 7 sessions

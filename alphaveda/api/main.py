"""AlphaVeda FastAPI application — Phase 7 Session A.

Transport layer only. All business logic stays in src/.
CORS: locked to Vercel domains via regex. Never allow_origins=['*'].
"""
from __future__ import annotations
import os

try:
    from dotenv import load_dotenv
    load_dotenv(
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        override=False,
    )
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, market_data, signals, path, accuracy

app = FastAPI(
    title="AlphaVeda API",
    version="0.1.0",
    docs_url=None,   # disable Swagger UI in production
    redoc_url=None,
)

# CORS: Vercel production + preview domains + local dev only.
# allow_origin_regex covers alphaveda-web.vercel.app AND any preview deploy
# (alphaveda-web-abc123.vercel.app). External origins are blocked.
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

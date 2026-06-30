# AlphaVeda FastAPI — Phase 7 Session A
# Deployed on Fly.io (Mumbai region: bom).
# PYTHONPATH=/app maps to the alphaveda/ directory, so all src/ imports resolve.

FROM python:3.11-slim

WORKDIR /app

# Install deps before copying app code — maximises layer cache reuse on redeploy.
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy full alphaveda package (src/, api/, constants.py, etc.).
# .env is NOT copied — secrets are injected via `fly secrets set`.
COPY . .

ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]

#!/usr/bin/env bash
# start.sh — Launch the LiteLLM proxy using the isolated Python 3.11 venv.
# This venv is completely separate from the GSI dashboard (Python 3.14).
#
# First-time setup (run once):
#   ~/.pyenv/versions/3.11.9/bin/python3 -m venv litellm-proxy/.venv
#   source litellm-proxy/.venv/bin/activate
#   pip install "litellm[proxy]"
#   deactivate
#
# Usage:
#   cd <repo-root>
#   bash litellm-proxy/start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [[ ! -f "$VENV/bin/activate" ]]; then
  echo "ERROR: venv not found at $VENV"
  echo "Run the first-time setup steps in this file's header comment."
  exit 1
fi

# Load .env from the proxy directory if present
ENV_FILE="$SCRIPT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
  echo "Loaded env from $ENV_FILE"
else
  echo "WARNING: $ENV_FILE not found — API keys must already be exported."
fi

# Activate the isolated venv (Python 3.11 — not the GSI 3.14 environment)
# shellcheck disable=SC1090
source "$VENV/bin/activate"

echo "Python: $(python --version)"
echo "LiteLLM proxy starting on http://0.0.0.0:4000 ..."
echo "Point Claude Code at it:"
echo "  export ANTHROPIC_BASE_URL=http://localhost:4000"
echo "  export ANTHROPIC_AUTH_TOKEN=\$LITELLM_MASTER_KEY"
echo ""

# cd into the proxy dir so approval_hook.py is importable by Python
cd "$SCRIPT_DIR"

exec litellm --config config.yaml --port 4000

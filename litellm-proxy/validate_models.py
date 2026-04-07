#!/usr/bin/env python3
"""
validate_models.py — GSI LiteLLM Proxy Model Health Checker
─────────────────────────────────────────────────────────────
Reads litellm-proxy/config.yaml to get all registered model aliases,
then queries the LiteLLM proxy health endpoint and reports per-model
status with colored output.

Usage (from repo root):
    python3 litellm-proxy/validate_models.py

Usage (from litellm-proxy/):
    python3 validate_models.py

Options:
    --proxy URL    Proxy base URL (default: http://localhost:4000)

Exit codes:
    0 — all models healthy
    1 — one or more models unhealthy or not found in health response
    2 — proxy unreachable, missing LITELLM_MASTER_KEY, or config unreadable

Environment:
    LITELLM_MASTER_KEY   Bearer token for the proxy (required)

Example output:
    ✓  deep-reasoning    anthropic/claude-opus-4-5       [healthy]
    ✗  hf-code           groq/openai/gpt-oss-20b         [unhealthy]
    ?  research          perplexity/sonar-pro             [not in health response]
    ─────────────────────────────────────────────────────
    5/8 models healthy
"""

import argparse
import os
import sys
import urllib.request
import urllib.error
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# ANSI color codes (same style as sprint_planner.py)
# ---------------------------------------------------------------------------

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
DIM    = "\033[90m"

# ---------------------------------------------------------------------------
# Locate config.yaml — works whether run from repo root or litellm-proxy/
# ---------------------------------------------------------------------------

SCRIPT_DIR  = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"


# ---------------------------------------------------------------------------
# YAML loader with stdlib fallback
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    """
    Load a YAML file.  Uses PyYAML when available; falls back to a minimal
    line-parser that handles the simple key: value / list structure in
    litellm-proxy/config.yaml.  The fallback is intentionally narrow —
    it extracts only model_name and litellm_params.model entries.
    """
    try:
        import yaml  # PyYAML — present as a litellm transitive dependency
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except ImportError:
        pass  # fall through to line-parser

    # ---------- minimal fallback line-parser ----------
    models = []
    current: dict | None = None
    in_params = False

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.lstrip()

        # New model entry
        if stripped.startswith("- model_name:"):
            current = {"model_name": stripped.split(":", 1)[1].strip(), "litellm_params": {}}
            models.append(current)
            in_params = False
            continue

        if current is None:
            continue

        if stripped == "litellm_params:":
            in_params = True
            continue

        if in_params and stripped.startswith("model:"):
            current["litellm_params"]["model"] = stripped.split(":", 1)[1].strip()
            continue

        # Any non-indented key that is not "litellm_params" exits param block
        if line and not line[0].isspace() and stripped.endswith(":") and stripped != "litellm_params:":
            in_params = False

    return {"model_list": models}


# ---------------------------------------------------------------------------
# Config parser — returns list of (model_name, provider_model) tuples
# ---------------------------------------------------------------------------

def parse_config(path: Path) -> list[tuple[str, str]]:
    """
    Parse config.yaml and return [(alias, provider_model), ...] in order.
    Returns empty list on any error (caller prints a clear message).
    """
    if not path.exists():
        return []
    try:
        data = _load_yaml(path)
    except Exception as exc:  # noqa: BLE001
        print(f"{RED}ERROR: could not parse {path}: {exc}{RESET}", file=sys.stderr)
        return []

    model_list = data.get("model_list", []) or []
    result = []
    for entry in model_list:
        alias = (entry.get("model_name") or "").strip()
        params = entry.get("litellm_params") or {}
        provider_model = (params.get("model") or "").strip()
        if alias:
            result.append((alias, provider_model))
    return result


# ---------------------------------------------------------------------------
# Health endpoint query
# ---------------------------------------------------------------------------

def query_health(proxy_url: str, master_key: str) -> dict | None:
    """
    GET {proxy_url}/health with Bearer auth.
    Returns parsed JSON dict on success, None if unreachable.
    Expected response shape:
        {"healthy_endpoints": [...], "unhealthy_endpoints": [...]}
    Each endpoint entry may be a dict with a "model_name" key, or
    just a string — we handle both.
    """
    url = proxy_url.rstrip("/") + "/health"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {master_key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.URLError as exc:
        print(f"{RED}ERROR: proxy unreachable at {url}{RESET}", file=sys.stderr)
        print(f"{DIM}  {exc.reason if hasattr(exc, 'reason') else exc}{RESET}",
              file=sys.stderr)
        return None
    except json.JSONDecodeError as exc:
        print(f"{RED}ERROR: unexpected response from proxy (not JSON): {exc}{RESET}",
              file=sys.stderr)
        return None


def _extract_names(endpoints: list) -> set[str]:
    """
    Extract model name strings from a health endpoint list.
    LiteLLM may return dicts like {"model_name": "hf-code", ...} or plain strings.
    """
    names: set[str] = set()
    for ep in (endpoints or []):
        if isinstance(ep, dict):
            # Try several known keys LiteLLM uses
            for key in ("model_name", "model", "id"):
                val = ep.get(key)
                if val:
                    names.add(str(val).strip())
                    break
        elif isinstance(ep, str):
            names.add(ep.strip())
    return names


# ---------------------------------------------------------------------------
# PROXY-06: Spend visibility
# ---------------------------------------------------------------------------

def _show_spend(proxy_url: str, master_key: str) -> None:
    """
    Fetch /spend from the LiteLLM proxy and print a per-provider cost summary.
    Exits with code 2 if the proxy is unreachable or the key is missing.
    """
    if not master_key:
        print(f"{RED}ERROR: LITELLM_MASTER_KEY is not set.{RESET}", file=sys.stderr)
        sys.exit(2)

    url = proxy_url.rstrip("/") + "/spend"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {master_key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"{RED}ERROR: proxy unreachable at {url}{RESET}", file=sys.stderr)
        print(f"{DIM}  {exc.reason if hasattr(exc, 'reason') else exc}{RESET}",
              file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"{RED}ERROR: unexpected response (not JSON): {exc}{RESET}", file=sys.stderr)
        sys.exit(2)

    print()
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"{BOLD}  GSI LiteLLM Proxy — Spend Summary{RESET}")
    print(f"{BOLD}{'═' * 62}{RESET}")

    # LiteLLM /spend may return a list of entries or a dict with "spend" key.
    entries = data if isinstance(data, list) else data.get("spend", [])
    if not entries:
        print(f"  {YELLOW}No spend data returned (proxy may not track spend).{RESET}")
        print(f"{'═' * 62}")
        print()
        return

    total = 0.0
    for entry in entries:
        provider = entry.get("provider") or entry.get("model") or "unknown"
        cost     = float(entry.get("total_cost") or entry.get("spend") or 0)
        total   += cost
        bar      = "█" * min(int(cost * 1000), 30)  # visual scale: $0.001 = 1 block
        print(f"  {provider:<30}  ${cost:>8.4f}  {DIM}{bar}{RESET}")

    print(f"{'─' * 62}")
    print(f"  {'TOTAL':<30}  ${total:>8.4f}")
    print(f"{'═' * 62}")
    print()


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate all models in config.yaml against the LiteLLM proxy health endpoint.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--proxy",
        default="http://localhost:4000",
        metavar="URL",
        help="LiteLLM proxy base URL (default: http://localhost:4000)",
    )
    parser.add_argument(
        "--spend",
        action="store_true",
        help="Show daily per-provider spend summary from the /spend endpoint.",
    )
    args = parser.parse_args()

    if args.spend:
        _show_spend(args.proxy, os.environ.get("LITELLM_MASTER_KEY", ""))
        return

    # --- Require master key ---
    master_key = os.environ.get("LITELLM_MASTER_KEY", "")
    if not master_key:
        print(f"{RED}ERROR: LITELLM_MASTER_KEY environment variable is not set.{RESET}",
              file=sys.stderr)
        print("  Export it before running:", file=sys.stderr)
        print("    export LITELLM_MASTER_KEY=<your-key>", file=sys.stderr)
        sys.exit(2)

    # --- Parse config ---
    models = parse_config(CONFIG_PATH)
    if not models:
        print(f"{RED}ERROR: No models found in {CONFIG_PATH}{RESET}", file=sys.stderr)
        print("  Check that config.yaml exists and contains a model_list.", file=sys.stderr)
        sys.exit(2)

    print()
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"{BOLD}  GSI LiteLLM Proxy — Model Health Check{RESET}")
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"  Config  : {CONFIG_PATH}")
    print(f"  Proxy   : {args.proxy}")
    print(f"  Models  : {len(models)} registered")
    print(f"{'─' * 62}")

    # --- Query health endpoint ---
    health = query_health(args.proxy, master_key)
    if health is None:
        print()
        print(f"{YELLOW}  All {len(models)} model(s) status unknown — proxy unreachable.{RESET}")
        print(f"{'═' * 62}")
        sys.exit(2)

    healthy_names   = _extract_names(health.get("healthy_endpoints", []))
    unhealthy_names = _extract_names(health.get("unhealthy_endpoints", []))

    # --- Report per model ---
    healthy_count   = 0
    unhealthy_count = 0
    unknown_count   = 0

    col_alias = max(len(alias) for alias, _ in models) + 2
    col_model = max(len(pm)    for _, pm    in models) + 2

    print()
    for alias, provider_model in models:
        if alias in healthy_names:
            status_sym   = f"{GREEN}✓{RESET}"
            status_label = f"{GREEN}[healthy]{RESET}"
            healthy_count += 1
        elif alias in unhealthy_names:
            status_sym   = f"{RED}✗{RESET}"
            status_label = f"{RED}[unhealthy]{RESET}"
            unhealthy_count += 1
        else:
            status_sym   = f"{YELLOW}?{RESET}"
            status_label = f"{YELLOW}[not in health response]{RESET}"
            unknown_count += 1

        alias_col = alias.ljust(col_alias)
        model_col = provider_model.ljust(col_model)
        print(f"  {status_sym}  {alias_col}{DIM}{model_col}{RESET}{status_label}")

    # --- Summary ---
    total = len(models)
    print()
    print(f"{'─' * 62}")
    print(f"  {BOLD}{healthy_count}/{total} models healthy{RESET}", end="")
    if unhealthy_count:
        print(f"  |  {RED}{unhealthy_count} unhealthy{RESET}", end="")
    if unknown_count:
        print(f"  |  {YELLOW}{unknown_count} unknown{RESET}", end="")
    print()
    print(f"{'═' * 62}")
    print()

    # --- Exit code ---
    if unhealthy_count > 0 or unknown_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

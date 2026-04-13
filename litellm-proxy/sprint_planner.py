#!/usr/bin/env python3
"""
sprint_planner.py — GSI Sprint Execution Planner
─────────────────────────────────────────────────
Reads the backlog from GSI_SPRINT.md and classifies each item into
one of four execution tiers, then prints a prioritised plan.

Usage (from repo root):
    python3 litellm-proxy/sprint_planner.py

Usage (from litellm-proxy/):
    python3 sprint_planner.py

Output: tiered execution plan showing what to run with Claude Code
subscription vs what to route through the LiteLLM proxy.
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate GSI_SPRINT.md — works whether run from repo root or litellm-proxy/
# ---------------------------------------------------------------------------

SCRIPT_DIR  = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent
SPRINT_FILE = REPO_ROOT / "GSI_SPRINT.md"
CONFIG_PATH = SCRIPT_DIR / "config.yaml"

# ---------------------------------------------------------------------------
# Live model name loader — reads config.yaml so TIERS always reflects
# the current provider model strings (survives Groq model rotations).
# ---------------------------------------------------------------------------

def _load_model_display_names(config_path: Path) -> dict[str, str]:
    """
    Read litellm-proxy/config.yaml and return a mapping of
    model_name alias → provider model string, e.g.:
        {
            "hf-reasoning": "groq/llama-3.3-70b-versatile",
            "hf-code":      "groq/qwen-qwq-32b",
            "hf-fast":      "groq/llama-3.1-8b-instant",
            ...
        }

    Uses PyYAML when available; falls back to a minimal line-parser
    that handles the simple structure of litellm-proxy/config.yaml.
    Returns an empty dict silently on any failure so TIERS keeps its
    hardcoded defaults.
    """
    if not config_path.exists():
        return {}

    # --- attempt PyYAML first (litellm transitive dependency) ---
    data: dict = {}
    try:
        import yaml  # noqa: PLC0415
        with config_path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except ImportError:
        pass  # fall through to line-parser
    except Exception:  # noqa: BLE001
        return {}

    if not data:
        # --- minimal fallback line-parser ---
        models_raw: list[dict] = []
        current: dict | None = None
        in_params = False
        try:
            for raw in config_path.read_text(encoding="utf-8").splitlines():
                line    = raw.rstrip()
                stripped = line.lstrip()
                if stripped.startswith("- model_name:"):
                    current = {
                        "model_name":     stripped.split(":", 1)[1].strip(),
                        "litellm_params": {},
                    }
                    models_raw.append(current)
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
                if line and not line[0].isspace() and stripped.endswith(":") and stripped != "litellm_params:":
                    in_params = False
            data = {"model_list": models_raw}
        except Exception:  # noqa: BLE001
            return {}

    result: dict[str, str] = {}
    for entry in (data.get("model_list") or []):
        alias  = (entry.get("model_name") or "").strip()
        params = entry.get("litellm_params") or {}
        model  = (params.get("model") or "").strip()
        if alias and model:
            result[alias] = model
    return result


# Load once at module import — all TIERS["..."]["model"] fields below
# that correspond to proxy aliases are overwritten with live config values.
_LIVE_MODELS: dict[str, str] = _load_model_display_names(CONFIG_PATH)

# ---------------------------------------------------------------------------
# Shared keyword config — imported for display/validation purposes.
# approval_hook.py uses the same lists for runtime prompt routing.
# ---------------------------------------------------------------------------

try:
    from classifier_keywords import (  # noqa: F401
        ARCHITECT_KEYWORDS,
        CODEGEN_KEYWORDS,
        QUICKQA_KEYWORDS,
        RESEARCH_KEYWORDS,
    )
    _KEYWORDS_LOADED = True
except ImportError:
    _KEYWORDS_LOADED = False

# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

TIERS = {
    "subscription": {
        "label": "CLAUDE CODE SUBSCRIPTION",
        "model": "claude-sonnet-4-6 / claude-opus-4-6",
        "color": "\033[95m",   # magenta
        "when": "Architecture, new infrastructure, multi-file refactors, "
                "complex integrations, high governance risk",
        "order": 1,
    },
    "hf-reasoning": {
        "label": "HF-REASONING  (Groq Llama-3.3-70B — free)",
        "model": _LIVE_MODELS.get("hf-reasoning", "hf-reasoning"),
        "color": "\033[94m",   # blue
        "when": "Medium-complexity features, single-file implementations, "
                "data logic, test writing",
        "order": 2,
    },
    "hf-code": {
        "label": "HF-CODE  (Groq Qwen-QwQ-32B — free)",
        "model": _LIVE_MODELS.get("hf-code", "hf-code"),
        "color": "\033[92m",   # green
        "when": "Low-effort refactors, config extraction, UI polish, "
                "documentation, simple bug fixes",
        "order": 3,
    },
    "hf-fast": {
        "label": "HF-FAST  (Groq Llama-3.1-8B — free)",
        "model": _LIVE_MODELS.get("hf-fast", "hf-fast"),
        "color": "\033[96m",   # cyan
        "when": "Docstrings, inline comments, formatting, quick Q&A",
        "order": 4,
    },
    "blocked": {
        "label": "BLOCKED — dependency not yet met",
        "model": "—",
        "color": "\033[91m",   # red
        "when": "Items with unresolved prerequisite (OPEN-018, OPEN-007, etc.)",
        "order": 5,
    },
}

RESET  = "\033[0m"
BOLD   = "\033[1m"
YELLOW = "\033[93m"

# ---------------------------------------------------------------------------
# Classification rules
# Evaluated top-to-bottom; first match wins.
# ---------------------------------------------------------------------------

def classify(item_id: str, description: str, effort: str, governance: str,
             files: int = 0) -> str:
    """
    Classify a backlog item into an execution tier.

    Priority order (first match wins):
      BLOCKED → malformed-effort → subscription → hf-reasoning (medium) →
      hf-fast (trivial low) → hf-code (low) → hf-reasoning (default)

    The `files` parameter is populated when the sprint board table contains a
    "Files" column (integer count of files the item touches). When absent the
    column is omitted from GSI_SPRINT.md and files defaults to 0.
    """
    desc = description.lower()
    gov  = governance.lower()
    eff  = effort.lower()

    # --- BLOCKED: explicit dependency markers ---
    if "(claude api)" in gov:
        return "blocked"
    if "open-007" in gov and item_id not in ("OPEN-007",):
        return "blocked"

    # --- MALFORMED EFFORT: escalate to subscription (safe default) ---
    # Non-standard values ("v.low", "medium-high", "") cannot be reasoned about.
    # Treat unknown effort as high-risk rather than silently under-routing.
    if eff not in ("low", "medium", "high"):
        return "subscription"

    # --- SUBSCRIPTION: high-judgment / infrastructure / architecture ---

    # Multi-file scope: >2 files touched = multi-file refactor territory.
    # Activates only when sprint board has a "Files" column (default 0 = inactive).
    if files > 2:
        return "subscription"

    # HARD-LOCK keywords — always subscription regardless of effort.
    # These signal structural changes, P0 legal risk, or unbounded governance
    # obligations that external models must never be trusted with.
    if any(kw in desc for kw in [
        # Infrastructure / data layer — structural, multi-file by nature
        "supabase", "datamanager", "cachemanager", "datacontract",
        "infrastructure", "architecture", "integration",
        "persistence", "claude api",
        # DO NOT UNDO adjacency — signal pipeline and compliance boundaries.
        # Rules 11–14 and Policy 4/6 sit here. One wrong line = P0 regression.
        "verdict", "sebi", "momentum score", "signal score",
        # New module creation carries unbounded downstream governance obligations
        # (CLAUDE.md file structure, R8 EP list, R10b, doc update requirements).
        "new page", "new module",
        # Decisions and regulatory implementation — final, high-stakes, legal risk.
        "decision record", "adr-", "regulatory", "sprint manifest",
    ]):
        return "subscription"

    if eff == "high":
        return "subscription"

    # Policy escalation by governance field.
    # Policy 2 (Architecture), Policy 4 (Regulatory/Compliance), Policy 6
    # (Signal Arbitration) with non-low effort → subscription.
    # Low-effort items under these policies (e.g. updating a policy doc string,
    # appending a checklist entry) can safely go to hf-code — regression + review
    # catch any mistake.
    if any(p in gov for p in ("policy 2", "policy 4", "policy 6")) and eff != "low":
        return "subscription"

    # SOFT-LOCK keywords — subscription only when effort is non-low.
    # Low-effort instances of these (doc wording updates, audit trail appends,
    # risk register status changes, checklist formatting) are safe for hf-code.
    # The content is sensitive but the scope is mechanical — regression + review
    # is the quality gate, not model choice.
    if eff != "low" and any(kw in desc for kw in [
        "governance", "compliance", "audit trail",
        "risk register", "open item", "checklist",
    ]):
        return "subscription"

    # New file creation + non-trivial effort → subscription.
    # Creating a file requires CLAUDE.md updates the planner cannot predict.
    if eff != "low" and any(kw in desc for kw in [
        "new file", "create a new", "add a new",
    ]):
        return "subscription"

    # --- HF-REASONING: medium effort (effort field wins — checked BEFORE keywords) ---
    # The sprint board effort rating is set with full codebase context and takes
    # precedence over description keyword inference. Medium items must never be
    # downgraded by hf-code keywords such as "ui polish" or "disclosure".
    if eff == "medium":
        return "hf-reasoning"

    # --- HF-FAST: trivial low-effort formatting/docs tasks ---
    # Only pure mechanical edits with no logic changes.
    if eff == "low" and any(kw in desc for kw in [
        "docstring", "comment", "format", "rename", "typo",
    ]):
        return "hf-fast"

    # --- HF-CODE: low effort / simple refactors / config / UI polish ---
    if eff == "low":
        return "hf-code"
    if any(kw in desc for kw in [
        "extract", "config", "label", "disclosure",
        "ui polish", "polish", "static", "rename",
    ]):
        return "hf-code"

    # Default
    return "hf-reasoning"


# ---------------------------------------------------------------------------
# Parser — extracts backlog table rows from GSI_SPRINT.md
# ---------------------------------------------------------------------------

def parse_backlog(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")

    # Find the Backlog section
    backlog_match = re.search(r"### Backlog.*?\n(.*?)(?=\n---|\n###)", text, re.DOTALL)
    if not backlog_match:
        return []

    backlog_text = backlog_match.group(1)

    # Detect optional "Files" and "Depends" columns from the header row.
    # Files: integer count of files touched → feeds multi-file scope escalation.
    # Depends: item ID that must be Done before this item can start (PROXY-04).
    # Expected header: | ID | Description | Effort | Source | Governance policy | Files | Depends |
    files_col_idx: int | None = None
    depends_col_idx: int | None = None

    items = []
    for line in backlog_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 4:
            continue

        # Header row — detect column layout
        if cells[0] == "ID":
            for i, header in enumerate(cells):
                if header.lower() in ("files", "files touched", "file count"):
                    files_col_idx = i
                if header.lower() in ("depends", "dependency", "requires"):
                    depends_col_idx = i
            continue

        if cells[0] in ("---", ":---", "---:"):
            continue
        if re.match(r"^-+$", cells[0].replace(":", "")):
            continue

        item_id, description, effort, source, *rest = cells + ["", ""]
        governance = rest[0] if rest else ""

        # Extract files count when column is present
        files = 0
        if files_col_idx is not None and files_col_idx < len(cells):
            try:
                files = int(cells[files_col_idx])
            except (ValueError, IndexError):
                files = 0

        # Extract dependency ID when column is present
        depends = ""
        if depends_col_idx is not None and depends_col_idx < len(cells):
            depends = cells[depends_col_idx].strip()

        # Skip separator lines
        if re.match(r"^[-|: ]+$", item_id):
            continue

        items.append({
            "id":          item_id,
            "description": description,
            "effort":      effort,
            "source":      source,
            "governance":  governance,
            "files":       files,
            "depends":     depends,
            "tier":        classify(item_id, description, effort, governance, files),
        })

    return items


# ---------------------------------------------------------------------------
# In-Progress parser — items that have moved out of Backlog
# ---------------------------------------------------------------------------

def parse_in_progress(path: Path) -> list[dict]:
    """
    Extract items from the '### In Progress' table in GSI_SPRINT.md.
    These are items already started — they still need a tier assignment
    so the developer knows which model context is appropriate mid-task.
    Returns an empty list when the section has no table rows.
    """
    text = path.read_text(encoding="utf-8")
    match = re.search(r"### In Progress\s*\n(.*?)(?=\n---|\n###)", text, re.DOTALL)
    if not match:
        return []

    section = match.group(1)
    items   = []

    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue
        if cells[0] in ("ID", "---", ":---", "---:", "Description", "Verified"):
            continue
        if re.match(r"^-+$", cells[0].replace(":", "")):
            continue
        if re.match(r"^[-|: ]+$", cells[0]):
            continue

        item_id     = cells[0]
        description = cells[1] if len(cells) > 1 else ""
        effort      = cells[2] if len(cells) > 2 else ""
        source      = cells[3] if len(cells) > 3 else ""
        governance  = cells[4] if len(cells) > 4 else ""

        if not item_id or not description:
            continue

        items.append({
            "id":          item_id,
            "description": description,
            "effort":      effort,
            "source":      source,
            "governance":  governance,
            "files":       0,
            "status":      "in_progress",
            "tier":        classify(item_id, description, effort, governance),
        })

    return items


# ---------------------------------------------------------------------------
# PROXY-05: In-progress staleness check
# Uses git log to find when GSI_SPRINT.md was last modified.
# If in-progress items exist and the file hasn't changed in > STALE_DAYS, warn.
# ---------------------------------------------------------------------------

STALE_DAYS = 14  # ~2 sessions


def _sprint_file_age_days(path: Path) -> int | None:
    """
    Return the number of days since GSI_SPRINT.md was last committed.
    Returns None if git is unavailable or the file is untracked.
    """
    try:
        result = subprocess.run(
            ["git", "log", "-n1", "--format=%ci", "--", str(path)],
            capture_output=True, text=True,
            cwd=path.parent,
        )
        stamp = result.stdout.strip()[:10]  # "YYYY-MM-DD"
        if not stamp:
            return None
        last = date.fromisoformat(stamp)
        return (date.today() - last).days
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# PROXY-04: Depends-column parser
# Backlog table may include an optional "Depends" column.
# When present, items whose dependency is not yet in Done are flagged.
# ---------------------------------------------------------------------------

def _parse_done_ids(path: Path) -> set[str]:
    """
    Collect all item IDs that appear in any 'Done' section of GSI_SPRINT.md.
    Used to evaluate whether a 'Depends' prerequisite has shipped.
    """
    text = path.read_text(encoding="utf-8")
    done_ids: set[str] = set()
    # Find all Done sections (### Done — vX.XX)
    for block in re.finditer(r"### Done.*?\n(.*?)(?=\n---|\n###|\Z)", text, re.DOTALL):
        for line in block.group(1).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if cells and cells[0] not in ("ID", "---", ":---", "---:", "Description", "Verified"):
                done_ids.add(cells[0])
    return done_ids


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

def render_plan(items: list[dict], sprint_name: str,
                in_progress: list[dict] | None = None,
                done_ids: set[str] | None = None,
                stale_days: int | None = None) -> None:
    in_progress = in_progress or []
    done_ids    = done_ids or set()

    # Group by tier
    groups: dict[str, list[dict]] = {k: [] for k in TIERS}
    for item in items:
        groups[item["tier"]].append(item)

    sub_count     = len(groups["subscription"])
    proxy_count   = sum(len(groups[t]) for t in ("hf-reasoning", "hf-code", "hf-fast"))
    blocked_count = len(groups["blocked"])

    print()
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"{BOLD}  GSI SPRINT EXECUTION PLAN — {sprint_name}{RESET}")
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"  Backlog: {len(items)} items  |  "
          f"Subscription: {sub_count}  |  "
          f"Proxy (free): {proxy_count}  |  "
          f"Blocked: {blocked_count}")
    if in_progress:
        print(f"  In Progress: {len(in_progress)} item(s) — shown first below")
    # PROXY-05: staleness warning
    if in_progress and stale_days is not None and stale_days > STALE_DAYS:
        print(f"  {YELLOW}⚠  In-progress items last touched {stale_days}d ago "
              f"(>{STALE_DAYS}d — may be stale){RESET}")
    if sub_count + proxy_count > 0:
        savings_pct = round(proxy_count / (sub_count + proxy_count) * 100)
        print(f"  Est. subscription token savings: ~{savings_pct}%")
    print(f"{'─' * 62}")

    # --- IN PROGRESS section (rendered before tier groups) ---
    if in_progress:
        WIP_COLOR = "\033[93m"   # yellow
        print()
        print(f"{WIP_COLOR}{BOLD}  ▶ CURRENTLY IN PROGRESS{RESET}")
        print(f"  {'─' * 56}")
        for item in in_progress:
            tier_color = TIERS.get(item["tier"], {}).get("color", "")
            tier_label = TIERS.get(item["tier"], {}).get("label", item["tier"])
            print(f"  ⟳  [{item['id']}] {item['description']}")
            if item["governance"]:
                print(f"       {WIP_COLOR}↳ {item['governance']}{RESET}")
            print(f"       {tier_color}↳ tier: {tier_label}{RESET}")

    global_seq = 0

    for tier_key in ("subscription", "hf-reasoning", "hf-code", "hf-fast", "blocked"):
        tier = TIERS[tier_key]
        tier_items = groups[tier_key]
        if not tier_items:
            continue

        color = tier["color"]
        print()
        print(f"{color}{BOLD}  {tier['label']}{RESET}")
        print(f"  Model : {tier['model']}")
        print(f"  When  : {tier['when']}")
        print(f"  {'─' * 56}")

        for item in tier_items:
            if tier_key != "blocked":
                global_seq += 1
                prefix = f"  {global_seq:>2}."
            else:
                prefix = "   ✗ "

            gov_note = f"  [{item['governance']}]" if item["governance"] else ""
            files    = item.get("files", 0)
            print(f"{prefix} [{item['id']}] {item['description']}")
            if gov_note:
                print(f"       {color}↳ {item['governance']}{RESET}")
            if files:
                print(f"       \033[90m↳ {files} file(s) touched\033[0m")
            # PROXY-04: depends warning — flag when prerequisite not yet in Done
            dep = item.get("depends", "")
            if dep and dep not in done_ids:
                print(f"       {YELLOW}⚠  Depends on [{dep}] — not yet Done{RESET}")
            # Tripwire: medium-effort item in hf-code means classify() logic drifted
            if item["effort"].lower() == "medium" and tier_key == "hf-code":
                print(f"       \033[33m⚠  Effort=Medium in hf-code — verify tier manually\033[0m")
            # Tripwire: malformed effort field — item escalated to subscription as safe default
            if item["effort"].lower() not in ("low", "medium", "high") and tier_key == "subscription":
                print(f"       \033[33m⚠  Effort='{item['effort']}' unrecognised — escalated to subscription\033[0m")

    print()
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"{BOLD}  EXECUTION GUIDE{RESET}")
    print(f"{'─' * 62}")
    print("  1. SUBSCRIPTION items — run Claude Code directly:")
    print("     unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN")
    print("     claude")
    print("     → inside Claude Code: /new-session")
    print()
    print("  2. PROXY items — proxy runs via launchd (no extra terminal needed):")
    print(f"     {YELLOW}IMPORTANT: Two-launch sequence required — env vars are locked at process start.{RESET}")
    print(f"     {YELLOW}  Launch 1 (no vars): claude → /new-session → context loaded → exit{RESET}")
    print(f"     {YELLOW}  Launch 2 (vars set before launch): source .env → export vars → claude{RESET}")
    print("     # after /new-session completes in subscription mode:")
    print("     source litellm-proxy/.env")
    print("     export ANTHROPIC_BASE_URL=http://localhost:4000")
    print("     export ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY")
    print()
    print("  3. MIXED session — choose order by session budget:")
    print("     Full budget  → subscription first, proxy second.")
    print("     Low budget   → proxy first (self-contained, safe to complete).")
    print("     Never start a subscription item you cannot finish in one session.")
    print()
    print("  4. BLOCKED items — revisit once prerequisite items are complete.")
    print(f"{'═' * 62}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if not SPRINT_FILE.exists():
        print(f"ERROR: GSI_SPRINT.md not found at {SPRINT_FILE}", file=sys.stderr)
        print("Run this script from the repo root or litellm-proxy/ directory.",
              file=sys.stderr)
        sys.exit(1)

    # Extract sprint name from file header
    text = SPRINT_FILE.read_text(encoding="utf-8")
    sprint_match = re.search(r"## Current Sprint: (.+)", text)
    sprint_name  = sprint_match.group(1).strip() if sprint_match else "Current Sprint"

    items       = parse_backlog(SPRINT_FILE)
    in_progress = parse_in_progress(SPRINT_FILE)

    if not items and not in_progress:
        print("No backlog or in-progress items found in GSI_SPRINT.md.")
        print("Add items to the '### Backlog' or '### In Progress' table and re-run.")
        sys.exit(0)

    done_ids   = _parse_done_ids(SPRINT_FILE)
    stale_days = _sprint_file_age_days(SPRINT_FILE)

    render_plan(items, sprint_name, in_progress, done_ids=done_ids, stale_days=stale_days)


if __name__ == "__main__":
    main()

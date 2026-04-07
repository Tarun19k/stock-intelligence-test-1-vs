#!/usr/bin/env python3
"""
review_gate.py — GSI Post-Proxy Diff Review Gate  (PROXY-03)
─────────────────────────────────────────────────────────────
Scans unpushed commits for proxy-tagged changes and flags any that
have not been manually reviewed before a push.

Convention
──────────
When working in LiteLLM proxy mode (ANTHROPIC_BASE_URL set), commit
messages should include a tag indicating which model wrote the diff:

    feat: indicators.py — OPEN-004 extract scoring weights [proxy:hf-code]

After reviewing the diff, add a review marker to the commit message
(via git commit --amend before pushing) or use the --mark flag here:

    python3 litellm-proxy/review_gate.py --mark <sha>

Usage
─────
    python3 litellm-proxy/review_gate.py            # check unpushed commits
    python3 litellm-proxy/review_gate.py --mark SHA  # mark a commit as reviewed
    python3 litellm-proxy/review_gate.py --all       # check all commits (not just unpushed)

Exit codes
──────────
    0 — no unreviewed proxy commits
    1 — one or more unreviewed proxy commits found
    2 — git unavailable or not in a repo
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# ANSI colour codes (same palette as sprint_planner.py / validate_models.py)
# ---------------------------------------------------------------------------

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
DIM    = "\033[90m"
RESET  = "\033[0m"

# ---------------------------------------------------------------------------
# Tag patterns
# ---------------------------------------------------------------------------

# Matches: [proxy:hf-code], [proxy:hf-reasoning], [proxy:deep-reasoning], etc.
PROXY_TAG   = re.compile(r"\[proxy:([^\]]+)\]")
# Matches: [reviewed] or [reviewed:yes] or [reviewed:tarun]
REVIEW_TAG  = re.compile(r"\[reviewed(?::[^\]]*)?\]")

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(*args: str, check: bool = True) -> str:
    """Run a git command and return stdout. Raises on non-zero exit if check=True."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True,
            cwd=REPO_ROOT,
        )
        if check and result.returncode != 0:
            print(f"{RED}git error: {result.stderr.strip()}{RESET}", file=sys.stderr)
            sys.exit(2)
        return result.stdout.strip()
    except FileNotFoundError:
        print(f"{RED}ERROR: git not found in PATH.{RESET}", file=sys.stderr)
        sys.exit(2)


def _unpushed_commits() -> list[tuple[str, str]]:
    """Return [(sha, subject), ...] for commits not yet on the remote."""
    raw = _git("log", "origin/HEAD..HEAD", "--format=%H %s", check=False)
    if not raw:
        return []
    result = []
    for line in raw.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            result.append((parts[0][:12], parts[1]))
    return result


def _all_commits(limit: int = 50) -> list[tuple[str, str]]:
    """Return [(sha, subject), ...] for the last N commits."""
    raw = _git("log", f"-{limit}", "--format=%H %s")
    result = []
    for line in raw.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            result.append((parts[0][:12], parts[1]))
    return result


def _full_message(sha: str) -> str:
    """Return the full commit message for a given SHA."""
    return _git("log", "-1", "--format=%B", sha)


# ---------------------------------------------------------------------------
# Mark helper
# ---------------------------------------------------------------------------

def _mark_reviewed(sha: str) -> None:
    """
    Append [reviewed] to the commit message of a given SHA via git notes.
    We use git notes (not amend) to avoid rewriting published history.
    """
    existing_note = _git("notes", "show", sha, check=False)
    new_note = (existing_note + "\n[reviewed]").strip() if existing_note else "[reviewed]"
    _git("notes", "add", "-f", "-m", new_note, sha)
    print(f"{GREEN}✓  Marked {sha[:12]} as reviewed (git note added).{RESET}")
    print(f"{DIM}   Note: git notes are local by default. "
          f"Push with: git push origin refs/notes/commits{RESET}")


def _get_note(sha: str) -> str:
    return _git("notes", "show", sha, check=False)


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------

def check_commits(commits: list[tuple[str, str]]) -> int:
    """
    Print a report of proxy-tagged commits and their review status.
    Returns the count of unreviewed proxy commits.
    """
    proxy_commits = []
    for sha, subject in commits:
        full_msg = _full_message(sha)
        note     = _get_note(sha)
        combined = full_msg + "\n" + note

        proxy_match = PROXY_TAG.search(combined)
        if not proxy_match:
            continue

        model    = proxy_match.group(1)
        reviewed = bool(REVIEW_TAG.search(combined))
        proxy_commits.append((sha, subject, model, reviewed))

    if not proxy_commits:
        print(f"{GREEN}✓  No proxy-tagged commits found.{RESET}")
        return 0

    print()
    print(f"{BOLD}{'═' * 62}{RESET}")
    print(f"{BOLD}  GSI Proxy Diff Review Gate{RESET}")
    print(f"{BOLD}{'═' * 62}{RESET}")

    unreviewed = 0
    for sha, subject, model, reviewed in proxy_commits:
        if reviewed:
            icon  = f"{GREEN}✓{RESET}"
            label = f"{DIM}[reviewed]{RESET}"
        else:
            icon  = f"{YELLOW}⚠{RESET}"
            label = f"{YELLOW}[NEEDS REVIEW]{RESET}"
            unreviewed += 1
        print(f"  {icon}  {sha}  {DIM}[proxy:{model}]{RESET}  {label}")
        print(f"       {subject[:70]}")

    print(f"{'─' * 62}")
    if unreviewed:
        print(f"  {YELLOW}{unreviewed} commit(s) need review before push.{RESET}")
        print()
        print(f"  To mark as reviewed:")
        print(f"    python3 litellm-proxy/review_gate.py --mark <sha>")
        print()
        print(f"  Or add {BOLD}[reviewed]{RESET} to the commit message before pushing.")
    else:
        print(f"  {GREEN}All proxy commits reviewed.{RESET}")
    print(f"{'═' * 62}")
    print()

    return unreviewed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan unpushed commits for unreviewed proxy-tagged changes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--mark",
        metavar="SHA",
        help="Mark a commit as reviewed (adds a git note).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check all recent commits, not just unpushed ones.",
    )
    args = parser.parse_args()

    if args.mark:
        _mark_reviewed(args.mark)
        return

    commits = _all_commits() if args.all else _unpushed_commits()

    if not commits:
        print(f"{GREEN}✓  No unpushed commits to review.{RESET}")
        sys.exit(0)

    unreviewed = check_commits(commits)
    sys.exit(1 if unreviewed else 0)


if __name__ == "__main__":
    main()

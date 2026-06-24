"""
artifact_workflow.py — Main artifact generation + council review orchestrator.

CLI:
    python3 scripts/artifact_workflow.py [--dry-run] [--force] [--types sprint-status,schema-viewer,session-checkpoint]

Loop per artifact type (FM-01):
    MAX_ITERATIONS = 5
    Generate → council review → if APPROVE: commit; else: accumulate gaps + retry
    On cap: write with [partial-approval] tag, log warning.

FM-02: CSP patterns enforced in council_review.py
FM-03: each seat receives only HTML (enforced in council_review.py)
FM-04: SESSION_RESUME.md missing → placeholder (enforced in generators)
FM-05: git commit happens ONLY after loop convergence, never mid-loop
FM-06: artifact size capped at 500KB / 500 lines (enforced in generators + council)
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
ALPHAVEDA_ROOT = _HERE.parent.parent          # alphaveda/
SCRIPTS_DIR = _HERE.parent                    # alphaveda/scripts/
REPO_ROOT = ALPHAVEDA_ROOT.parent             # repo root (stock-intelligence-test-1-vs/)

sys.path.insert(0, str(SCRIPTS_DIR))

from council_review import review_all, collect_gaps, is_approved  # noqa: E402

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("artifact_workflow")

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_ITERATIONS = 5
ARTIFACT_STALE_HOURS = 24
MAX_LINE_COUNT = 500
MAX_BYTES = 200 * 1024  # 200 KB hard cap before truncation

SUPPORTED_TYPES = ["sprint-status", "schema-viewer", "session-checkpoint"]

# Map artifact type → generator module function
_GENERATOR_MAP = {
    "sprint-status": None,       # loaded lazily
    "schema-viewer": None,
    "session-checkpoint": None,
}


def _load_generator(artifact_type: str):
    """Lazily import generator module to surface import errors clearly."""
    if artifact_type == "sprint-status":
        from artifact_generators import sprint_status
        return sprint_status.generate
    elif artifact_type == "schema-viewer":
        from artifact_generators import schema_viewer
        return schema_viewer.generate
    elif artifact_type == "session-checkpoint":
        from artifact_generators import session_checkpoint
        return session_checkpoint.generate
    else:
        raise ValueError(f"Unknown artifact type: {artifact_type}")


# ── Staleness check ───────────────────────────────────────────────────────────

def _artifact_path(artifact_type: str, today_str: str) -> Path:
    return ALPHAVEDA_ROOT / "docs" / "artifacts" / today_str / f"{artifact_type}.html"


def _is_stale(artifact_type: str, today_str: str, force: bool) -> bool:
    """
    Return True if artifact should be regenerated.
    Stale = file doesn't exist OR is >= 24h old OR --force passed.
    """
    if force:
        return True
    path = _artifact_path(artifact_type, today_str)
    if not path.exists():
        return True
    age_hours = (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 3600
    if age_hours >= ARTIFACT_STALE_HOURS:
        log.info(f"  [{artifact_type}] artifact is {age_hours:.1f}h old — regenerating")
        return True
    log.info(f"  [{artifact_type}] artifact is fresh ({age_hours:.1f}h old) — skipping (use --force to override)")
    return False


# ── Size enforcement (FM-06) ──────────────────────────────────────────────────

def _enforce_size(html: str, artifact_type: str) -> str:
    """
    If HTML exceeds MAX_LINE_COUNT or MAX_BYTES, truncate and append a note.
    FM-06: prevents runaway file sizes.
    """
    lines = html.splitlines()
    if len(lines) > MAX_LINE_COUNT:
        truncated = "\n".join(lines[:MAX_LINE_COUNT])
        truncated += "\n<!-- [truncated for size: exceeded 500 lines] -->\n</body>\n</html>"
        log.warning(f"  [{artifact_type}] truncated: {len(lines)} lines → {MAX_LINE_COUNT}")
        return truncated

    encoded = html.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        # Truncate by bytes — find safe cut point at a line boundary
        cut = html[:MAX_BYTES].rfind("\n")
        if cut == -1:
            cut = MAX_BYTES
        truncated = html[:cut]
        truncated += "\n<!-- [truncated for size: exceeded 200KB] -->\n</body>\n</html>"
        log.warning(f"  [{artifact_type}] truncated: {len(encoded) // 1024}KB → 200KB")
        return truncated

    return html


# ── Git commit (FM-05: only after loop convergence) ───────────────────────────

def _git_commit(committed_files: list[Path], today_str: str, approved_count: int, total_count: int):
    """
    Commit all generated artifact files.
    FM-05: called once after all loops complete.
    """
    if not committed_files:
        log.info("No files to commit.")
        return

    type_names = ", ".join(p.stem for p in committed_files)
    msg = (
        f"artifact(workflow): {today_str} — {type_names} "
        f"[{approved_count}/{total_count} council-approved]"
    )

    try:
        # Stage files
        for fpath in committed_files:
            subprocess.run(
                ["git", "add", str(fpath.relative_to(REPO_ROOT))],
                cwd=str(REPO_ROOT),
                check=True,
                capture_output=True,
            )

        # Check if anything staged
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(REPO_ROOT),
            capture_output=True,
        )
        if result.returncode == 0:
            log.info("Nothing new to commit (all files already tracked and unchanged).")
            return

        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
        )
        log.info(f"Committed: {msg}")

    except subprocess.CalledProcessError as exc:
        log.error(f"Git commit failed: {exc.stderr.decode() if exc.stderr else exc}")


# ── SESSION_RESUME.md update ──────────────────────────────────────────────────

def _update_session_resume(generated_types: list[str], today_str: str):
    """
    Append/update an ARTIFACTS section in SESSION_RESUME.md.
    Non-fatal if file doesn't exist.
    """
    resume_path = ALPHAVEDA_ROOT / "graphify-out" / "SESSION_RESUME.md"
    if not resume_path.exists():
        log.warning("SESSION_RESUME.md not found — skipping artifact section update")
        return

    text = resume_path.read_text(encoding="utf-8")
    artifact_note = (
        f"\n\n## ARTIFACTS (last run: {today_str})\n"
        + "\n".join(f"- {t}: docs/artifacts/{today_str}/{t}.html" for t in generated_types)
        + "\n"
    )

    if "## ARTIFACTS" in text:
        # Replace existing ARTIFACTS section
        text = re.sub(
            r"\n## ARTIFACTS.*?(?=\n## |\Z)",
            artifact_note,
            text,
            flags=re.DOTALL,
        )
    else:
        text += artifact_note

    resume_path.write_text(text, encoding="utf-8")
    log.info("Updated SESSION_RESUME.md ARTIFACTS section")


import re  # noqa: E402 (needed for _update_session_resume)


# ── Core loop ─────────────────────────────────────────────────────────────────

def run(
    artifact_types: list[str],
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """
    Main orchestration loop.
    Returns summary dict: {type: {"verdict": str, "iterations": int, "path": str|None}}
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary = {}
    committed_files: list[Path] = []
    approved_count = 0

    log.info(f"=== AlphaVeda Artifact Workflow — {today_str} ===")
    if dry_run:
        log.info("DRY-RUN mode: artifacts will be generated and reviewed but NOT written to disk")

    for artifact_type in artifact_types:
        log.info(f"\n--- Processing: {artifact_type} ---")

        # Staleness check
        if not _is_stale(artifact_type, today_str, force):
            existing = _artifact_path(artifact_type, today_str)
            summary[artifact_type] = {
                "verdict": "SKIPPED (fresh)",
                "iterations": 0,
                "path": str(existing),
            }
            continue

        generator = _load_generator(artifact_type)
        accumulated_gaps: list[str] = []
        final_html = ""
        final_verdict = "REVISE"
        iteration = 0

        for iteration in range(MAX_ITERATIONS):
            log.info(f"  Iteration {iteration + 1}/{MAX_ITERATIONS}")

            # Generate
            try:
                html = generator(feedback=accumulated_gaps)
            except Exception as exc:
                log.error(f"  Generator raised exception: {exc}")
                import traceback
                html = f"<html><body><pre>Generator error:\n{traceback.format_exc()}</pre></body></html>"

            # Size enforcement (FM-06)
            html = _enforce_size(html, artifact_type)

            # Write to temp file for size measurement
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", encoding="utf-8", delete=False
            ) as tmp:
                tmp.write(html)
                tmp_path = Path(tmp.name)

            file_size_bytes = tmp_path.stat().st_size

            # Council review (FM-03: council_review.review_all passes only html)
            review = review_all(html, artifact_type, file_size_bytes=file_size_bytes)
            final_verdict = review["final"]["verdict"]

            # Log seat verdicts
            for seat_result in review["verdicts"]:
                status = "✓" if seat_result["verdict"] == "APPROVE" else "✗"
                log.info(f"    [{status}] {seat_result['seat']}: {seat_result['verdict']}")
                for gap in seat_result["gaps"]:
                    log.info(f"         GAP: {gap}")

            log.info(f"  FINAL: {final_verdict}")

            if final_verdict == "APPROVE":
                final_html = html
                tmp_path.unlink(missing_ok=True)
                break

            # Accumulate gaps for next iteration
            accumulated_gaps = collect_gaps(review)
            final_html = html  # keep last generated even on REVISE
            tmp_path.unlink(missing_ok=True)

        # Determine tag
        if final_verdict == "APPROVE":
            tag = ""
            approved_count += 1
        else:
            # FM-01: cap reached
            tag = " [partial-approval]"
            log.warning(
                f"  [{artifact_type}] MAX_ITERATIONS={MAX_ITERATIONS} reached — "
                f"committing with [partial-approval]{tag}"
            )

        # Write artifact (FM-05: write after loop, not during)
        if not dry_run:
            dest = _artifact_path(artifact_type, today_str)
            dest.parent.mkdir(parents=True, exist_ok=True)

            if tag:
                # Inject tag into HTML comment near top
                final_html = final_html.replace(
                    "<title>", f"<!-- {tag.strip()} -->\n<title>", 1
                )

            dest.write_text(final_html, encoding="utf-8")
            committed_files.append(dest)
            log.info(f"  Written: {dest}")
        else:
            log.info(f"  [dry-run] Would write: {_artifact_path(artifact_type, today_str)}")

        summary[artifact_type] = {
            "verdict": final_verdict + tag,
            "iterations": iteration + 1,
            "path": str(_artifact_path(artifact_type, today_str)) if not dry_run else None,
        }

    # Git commit — FM-05: after all loops complete
    if not dry_run and committed_files:
        _git_commit(committed_files, today_str, approved_count, len(artifact_types))
        _update_session_resume(
            [p.stem for p in committed_files], today_str
        )

    # Print summary
    log.info("\n=== SUMMARY ===")
    for atype, info in summary.items():
        log.info(f"  {atype}: {info['verdict']} (iterations: {info['iterations']})")
    log.info(f"  Approved: {approved_count}/{len(artifact_types)}")

    return summary


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AlphaVeda artifact generation + council review workflow"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and review artifacts but do not write files or commit",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if artifact is < 24h old",
    )
    parser.add_argument(
        "--types",
        type=str,
        default=",".join(SUPPORTED_TYPES),
        help=f"Comma-separated artifact types (default: all). Options: {', '.join(SUPPORTED_TYPES)}",
    )
    args = parser.parse_args()

    types = [t.strip() for t in args.types.split(",") if t.strip()]
    unknown = [t for t in types if t not in SUPPORTED_TYPES]
    if unknown:
        log.error(f"Unknown artifact type(s): {unknown}. Supported: {SUPPORTED_TYPES}")
        sys.exit(1)

    summary = run(artifact_types=types, dry_run=args.dry_run, force=args.force)

    # Exit code: 0 if all approved or skipped, 1 if any partial-approval
    has_partial = any("partial-approval" in str(v.get("verdict", "")) for v in summary.values())
    sys.exit(1 if has_partial else 0)


if __name__ == "__main__":
    main()

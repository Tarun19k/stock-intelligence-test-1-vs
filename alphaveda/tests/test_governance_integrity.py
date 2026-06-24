"""
Governance integrity tests — keeps COUNCIL_TEST_MAP.md and the test suite in sync.

Mode:
  --warn   (default, GOVERNANCE_STRICT unset): issues warnings, never fails.
           Active now (Phase 2 housekeeping). Phase 3 sign-off proceeds.
  --strict (GOVERNANCE_STRICT=1): governance violations cause test failures.
           Promoted after Phase 3 council sign-off.

Resources: COUNCIL_TEST_MAP.md, tests/test_council_conditions.py, ast, re, subprocess
"""
import ast
import os
import re
import subprocess
import warnings
from pathlib import Path

ALPHAVEDA_ROOT = Path(__file__).parent.parent
MAP_PATH = ALPHAVEDA_ROOT / "COUNCIL_TEST_MAP.md"
TESTS_DIR = ALPHAVEDA_ROOT / "tests"
STRICT = os.environ.get("GOVERNANCE_STRICT", "0") == "1"


def _governance_fail(msg: str) -> None:
    if STRICT:
        raise AssertionError(f"[governance] {msg}")
    warnings.warn(f"[governance-warn] {msg}", stacklevel=3)


def _parse_map() -> list[dict]:
    """Parse both table sections of COUNCIL_TEST_MAP.md into row dicts."""
    rows = []
    for line in MAP_PATH.read_text().splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---|---" in stripped:
            continue
        # Skip header rows by checking if first cell is a known header label
        cells = [c.strip() for c in stripped.split("|") if c.strip()]
        if not cells or cells[0] in ("Seat", "Phase"):
            continue
        if len(cells) < 6:
            continue
        rows.append({
            "seat": cells[0].strip("*").strip(),
            "condition": cells[1],
            "test_file": cells[2],
            "function": cells[3],
            "phase": cells[4],
            "status": cells[5],
        })
    return rows


def _get_completed_phases() -> set[str]:
    """Extract phase numbers from the ## Completed Phases section."""
    text = MAP_PATH.read_text()
    match = re.search(r"## Completed Phases\n(.*?)(?:\n##|\Z)", text, re.DOTALL)
    if not match:
        return set()
    phases = set()
    for line in match.group(1).splitlines():
        m = re.search(r"Phase (\d+)", line)
        if m:
            phases.add(m.group(1))
    return phases


def _functions_in_file(path: Path) -> set[str]:
    """Return all function names in a Python file using AST."""
    try:
        tree = ast.parse(path.read_text())
    except (SyntaxError, FileNotFoundError):
        return set()
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


# ─────────────────────────────────────────────────────────────────────────────
# TestGovernanceMap — map accuracy checks
# ─────────────────────────────────────────────────────────────────────────────


class TestGovernanceMap:

    def test_parser_reads_minimum_rows(self):
        """Sentinel: parser must extract ≥30 rows or COUNCIL_TEST_MAP.md is malformed (FM-05)."""
        rows = _parse_map()
        assert len(rows) >= 30, (
            f"Parser returned only {len(rows)} rows from COUNCIL_TEST_MAP.md — "
            "expected ≥30. Map may be malformed or truncated."
        )

    def test_no_spec_in_complete_phases(self):
        """SPEC in a completed Phase = a test that was never written but Phase is signed off (FM-04)."""
        rows = _parse_map()
        completed = _get_completed_phases()
        spec_in_done = [
            r for r in rows
            if r["phase"].strip() in completed and r["status"].strip() == "SPEC"
        ]
        if spec_in_done:
            detail = ", ".join(
                f"{r['seat']}/{r['function']} (Phase {r['phase']})"
                for r in spec_in_done
            )
            _governance_fail(f"SPEC entries in completed phases {completed}: {detail}")

    def test_green_tests_are_collectable(self):
        """Every GREEN row must have a collectable test function in its declared test file (FM-06)."""
        rows = _parse_map()
        green_rows = [r for r in rows if "GREEN" in r["status"]]
        not_found = []
        for r in green_rows:
            test_file = TESTS_DIR / r["test_file"].strip()
            fn = r["function"].strip()
            if fn == "(rule, not test)":
                continue
            if not test_file.exists():
                not_found.append(f"{r['test_file']} (file missing)")
                continue
            if fn not in _functions_in_file(test_file):
                not_found.append(f"{r['test_file']}::{fn} (function not found)")
        if not_found:
            _governance_fail(f"GREEN tests not collectable (name drift?): {not_found}")

    def test_no_ghost_tests(self):
        """Un-skipped test functions with pass-only bodies are ghost tests (FM-08)."""
        ghosts = []
        for test_file in TESTS_DIR.glob("test_*.py"):
            try:
                tree = ast.parse(test_file.read_text())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                if not node.name.startswith("test_"):
                    continue
                # Skip if decorated with skip
                has_skip = any(
                    (isinstance(d, ast.Attribute) and d.attr == "skip")
                    or (
                        isinstance(d, ast.Call)
                        and isinstance(d.func, ast.Attribute)
                        and d.func.attr == "skip"
                    )
                    for d in node.decorator_list
                )
                if has_skip:
                    continue
                # Ghost: body is only pass statements (ignoring docstring)
                non_docstring = [
                    s for s in node.body
                    if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                ]
                is_ghost = not non_docstring or all(isinstance(s, ast.Pass) for s in non_docstring)
                if is_ghost:
                    ghosts.append(f"{test_file.name}::{node.name}")
        if ghosts:
            _governance_fail(f"Ghost tests (un-skipped, pass-only body): {ghosts}")


# ─────────────────────────────────────────────────────────────────────────────
# TestSkipReason — skip decorator hygiene
# ─────────────────────────────────────────────────────────────────────────────


class TestSkipReason:

    def test_no_stale_phase_skips(self):
        """Skip decorators referencing a completed Phase are stale and must be removed (FM-07)."""
        completed = _get_completed_phases()
        if not completed:
            return
        stale = []
        for test_file in TESTS_DIR.glob("test_*.py"):
            text = test_file.read_text()
            for m in re.finditer(r'@pytest\.mark\.skip\(reason="([^"]+)"\)', text):
                reason = m.group(1)
                if "not yet implemented" not in reason:
                    continue
                phase_match = re.search(r"Phase (\d+)", reason)
                if phase_match and phase_match.group(1) in completed:
                    stale.append(f"{test_file.name}: {reason!r}")
        if stale:
            _governance_fail(f"Stale skip decorators for completed phases: {stale}")

    def test_environmental_skips_exempt(self):
        """Skips for missing env vars must never use the Phase format (they are not stale)."""
        for test_file in TESTS_DIR.glob("test_*.py"):
            text = test_file.read_text()
            for m in re.finditer(r'@pytest\.mark\.skip\(reason="([^"]+)"\)', text):
                reason = m.group(1)
                is_env_skip = "not set" in reason or "SUPABASE_URL" in reason
                if is_env_skip:
                    assert "not yet implemented" not in reason, (
                        f"Environmental skip in {test_file.name} incorrectly uses Phase format: {reason!r}"
                    )


# ─────────────────────────────────────────────────────────────────────────────
# TestGovernanceMeta — self-checking guard
# ─────────────────────────────────────────────────────────────────────────────


class TestGovernanceMeta:

    def test_governance_test_is_self_checking(self):
        """Self-guard: parser must return ≥30 rows, else the governance test itself is broken (FM-05)."""
        rows = _parse_map()
        assert len(rows) >= 30, (
            f"Governance self-check failed: only {len(rows)} rows parsed. "
            "COUNCIL_TEST_MAP.md may be truncated. Do not proceed with Phase sign-off."
        )

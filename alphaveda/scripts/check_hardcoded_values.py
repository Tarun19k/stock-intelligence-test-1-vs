#!/usr/bin/env python3
"""Find suspicious hardcoded market values in signal and accuracy code."""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ALPHAVEDA_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (
    ALPHAVEDA_ROOT / "src" / "signals",
    ALPHAVEDA_ROOT / "src" / "accuracy",
)
LIVE_DATA_TERMS = {
    "amount",
    "balance",
    "capital",
    "close",
    "confidence",
    "equity",
    "fund",
    "index",
    "loss",
    "ma",
    "market",
    "nav",
    "portfolio",
    "price",
    "rate",
    "regime",
    "return",
    "revenue",
    "score",
    "threshold",
    "value",
    "vix",
    "volume",
}
SMALL_INTEGERS = {0, 1, 2}


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    literal: str
    function_name: str
    line: str


def _name_terms(name: str) -> set[str]:
    """Split snake/camel/alphanumeric names into lowercase semantic terms."""
    expanded = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    return {part for part in re.split(r"[^A-Za-z0-9]+", expanded.lower()) if part}


def _looks_live(name: str) -> bool:
    terms = _name_terms(name)
    return bool(terms & LIVE_DATA_TERMS) or any(
        term.endswith("ma") and term[:-2].isdigit() for term in terms
    )


def _expression_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.add(child.id)
        elif isinstance(child, ast.Attribute):
            names.add(child.attr)
        elif isinstance(child, ast.Subscript) and isinstance(child.slice, ast.Constant):
            if isinstance(child.slice.value, str):
                names.add(child.slice.value)
    return names


def _numeric_literals(node: ast.AST) -> list[ast.Constant]:
    return [
        child
        for child in ast.walk(node)
        if isinstance(child, ast.Constant)
        and isinstance(child.value, (int, float))
        and not isinstance(child.value, bool)
        and child.value not in SMALL_INTEGERS
    ]


def _is_all_caps_module_assignment(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> bool:
    current = node
    while current in parents:
        current = parents[current]
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return False
        if isinstance(current, (ast.Assign, ast.AnnAssign)):
            targets = current.targets if isinstance(current, ast.Assign) else [current.target]
            return bool(targets) and all(
                isinstance(target, ast.Name) and target.id.isupper() for target in targets
            )
    return False


def _function_for(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    current = node
    while current in parents:
        current = parents[current]
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
    return "<module>"


def _python_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        for path in root.rglob("*.py"):
            if path.name == "constants.py" or "tests" in path.relative_to(root).parts:
                continue
            files.append(path)
    return sorted(files)


def scan_file(path: Path) -> list[Finding]:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source, filename=str(path))
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    suspicious: dict[tuple[int, int], ast.Constant] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if keyword.arg and _looks_live(keyword.arg):
                    for literal in _numeric_literals(keyword.value):
                        suspicious[(literal.lineno, literal.col_offset)] = literal

        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            for index, operand in enumerate(operands):
                other_names = set().union(*(
                    _expression_names(other)
                    for other_index, other in enumerate(operands)
                    if other_index != index
                ))
                if any(_looks_live(name) for name in other_names):
                    for literal in _numeric_literals(operand):
                        suspicious[(literal.lineno, literal.col_offset)] = literal

    findings = []
    for literal in suspicious.values():
        if _is_all_caps_module_assignment(literal, parents):
            continue
        line = lines[literal.lineno - 1].strip()
        literal_text = ast.get_source_segment(source, literal) or repr(literal.value)
        findings.append(Finding(
            path=path,
            line_number=literal.lineno,
            literal=literal_text,
            function_name=_function_for(literal, parents),
            line=line,
        ))
    return sorted(findings, key=lambda finding: (finding.line_number, finding.literal))


def main() -> int:
    findings = [finding for path in _python_files() for finding in scan_file(path)]
    if not findings:
        print("No suspicious hardcoded numeric literals found.")
        return 0

    print(f"Suspicious hardcoded numeric literals: {len(findings)}")
    for finding in findings:
        relative_path = finding.path.relative_to(ALPHAVEDA_ROOT.parent)
        print(
            f"{relative_path}:{finding.line_number}: {finding.literal} | "
            f"function {finding.function_name} | {finding.line}"
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())

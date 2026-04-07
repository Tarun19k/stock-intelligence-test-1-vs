"""
classifier_keywords.py — Shared keyword config for GSI prompt and sprint classification.

Both approval_hook.py (runtime prompt routing) and sprint_planner.py (sprint tier
assignment) import from here. Update once; both classifiers stay in sync.

Priority order (first match wins):
    quickqa → research → codegen → architect → boilerplate (default)
"""

# Quick Q&A — short, low-stakes, cheap to route
QUICKQA_KEYWORDS: list[str] = [
    "how do i",
    "what does",
    "what is the command",
    "what is the difference",
    "difference between",
    " vs ",
    "versus",
    "syntax",
    "one liner",
    "one-liner",
    "example of",
    "quick",
    "briefly",
    "tldr",
    "tl;dr",
]

# Research — web-grounded, data lookups, documentation queries
RESEARCH_KEYWORDS: list[str] = [
    "search",
    "look up",
    "lookup",
    "find me",
    "latest",
    "recent",
    "current price",
    "current rate",
    "what is the latest",
    "news about",
    "documentation for",
    "api reference",
    "changelog",
    "release notes",
    "what version",
    "is there a library",
    "does python have",
]

# Code generation — writing, implementing, fixing concrete code
CODEGEN_KEYWORDS: list[str] = [
    "write a",
    "write the",
    "implement",
    "refactor",
    "fix the",
    "fix this",
    "fix bug",
    "create a",
    "create the",
    "build a",
    "build the",
    "add a",
    "add the",
    "add feature",
    "update the function",
    "update the class",
    "update the test",
    "update the logic",
    "update the implementation",
    "modify",
    "edit the",
    "patch",
    "make it",
    "make this",
    "generate a",
    "convert",
    "migrate",
]

# Architect — deep reasoning, root cause analysis, strategy, audit
# Deliberately narrow: only use when the task genuinely needs Opus-level reasoning
ARCHITECT_KEYWORDS: list[str] = [
    "root cause",
    "trace through",
    "debug why",
    "why is this failing",
    "why does this break",
    "diagnose",
    "architecture",
    "system design",
    "design a system",
    "tradeoff",
    "trade-off",
    "compare approaches",
    "which approach",
    "should i use",
    "audit",
    "security review",
    "code review",
    "performance review",
    "sprint plan",
    "regression failing",
    "explain the logic",
    "explain why",
    "walk me through",
    "step by step",
    "deep dive",
    # Design / failure-mode vocabulary
    "edge case",
    "fallback",
    "failure mode",
    "failure scenario",
    "what happens if",
    "what if ",           # trailing space avoids false match on "what if I"
    "resilience",
    "identify edge",
    "identify risk",
    "identify gap",
    "root causes",
    "faulty node",
    "single point of failure",
    "worst case",
]

# Boilerplate is the safe default — no keywords needed; matched last by exclusion.

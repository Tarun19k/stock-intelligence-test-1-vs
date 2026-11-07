#!/usr/bin/env bash
# session-start.sh — SessionStart hook: install repo dependencies so tests,
# linters, and both apps (GSI Dashboard + AlphaVeda) are runnable from a
# fresh workspace without a manual pip/npm install step.
#
# Covers two independent dependency stacks in this repo:
#   1. GSI Dashboard (root)      — requirements.txt (Streamlit/Python)
#   2. AlphaVeda (alphaveda/)    — requirements.txt + requirements-api.txt (Python)
#                                   web/package.json (Next.js/Node)
#
# Also mirrors the AlphaVeda Financial Council's skill files from their
# git-tracked source (alphaveda/.claude/skills/) into ~/.claude/skills/, the
# path alphaveda/.claude/rules/COUNCIL_RULES.md Rule A reads for its dispatch
# gate check — ~/.claude/skills/ is not durable across sessions in Claude
# Code on the web, so the repo copy is the source of truth and this hook
# re-syncs it every session.
#
# Runs synchronously (first iteration per session-start-hook skill guidance):
# guarantees deps are ready before Claude tries to run regression.py / pytest /
# npm test, at the cost of a slower session start. Switch to async mode later
# if startup latency becomes a problem.
#
# Web-only: no-ops outside Claude Code on the web (CLAUDE_CODE_REMOTE unset).
# Idempotent: safe to re-run — pip/npm both skip already-satisfied installs,
# and the skills mirror is a plain overwrite copy.

set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

REPO=$(git rev-parse --show-toplevel)
cd "$REPO"

# Two real, reproduced install-time issues on this container image (2026-08-17), not
# permission/config problems:
#   1. sgmllib3k (pulled by feedparser) fails its wheel build under setuptools' local distutils
#      shim — AttributeError: install_layout. SETUPTOOLS_USE_DISTUTILS=stdlib routes to the real
#      stdlib distutils (still present on Python 3.11) and avoids the shim's bug.
#   2. PyJWT is preinstalled by the base image via apt/debian with no pip RECORD file, so pip
#      can't uninstall it to upgrade — --ignore-installed installs fresh over top instead.
export SETUPTOOLS_USE_DISTUTILS=stdlib

echo "[session-start] installing GSI Dashboard Python deps..."
pip install -q -r requirements.txt

echo "[session-start] installing AlphaVeda Python deps..."
pip install -q --ignore-installed PyJWT -r alphaveda/requirements.txt -r alphaveda/requirements-api.txt

if [ -f alphaveda/web/package.json ]; then
  echo "[session-start] installing AlphaVeda web (Next.js) deps..."
  npm install --prefix alphaveda/web
fi

if [ -d alphaveda/.claude/skills ]; then
  echo "[session-start] mirroring AlphaVeda council skills into ~/.claude/skills/..."
  mkdir -p "$HOME/.claude/skills"
  cp -r alphaveda/.claude/skills/. "$HOME/.claude/skills/"
fi

if [ -f alphaveda/.claude/skills-index.md ]; then
  cp alphaveda/.claude/skills-index.md "$HOME/.claude/skills-index.md"
fi

if [ -f alphaveda/.claude/scripts/check-seat-skill.sh ]; then
  mkdir -p "$HOME/.claude/scripts"
  cp alphaveda/.claude/scripts/check-seat-skill.sh "$HOME/.claude/scripts/check-seat-skill.sh"
  chmod +x "$HOME/.claude/scripts/check-seat-skill.sh"
fi

echo "[session-start] dependency + skill sync complete."

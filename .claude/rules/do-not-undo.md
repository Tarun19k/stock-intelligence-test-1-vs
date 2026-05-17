---
paths:
  - "app.py"
  - "forecast.py"
  - "version.py"
  - "config.py"
  - "tickers.json"
  - "styles.py"
  - "pages/global_intelligence.py"
  - "pages/*.py"
  - "market_data.py"
  - "indicators.py"
---

# DO NOT UNDO — Hard Constraints

These rules encode past production failures. Reversing any of them recreates the original breakage.

## forecast.py — no filesystem persistence
Do NOT revert to filesystem storage for forecasts. Streamlit Cloud wipes the filesystem on every redeploy. Session state is the only durable store across a session; Supabase is the target for cross-session persistence (OPEN-003).

## app.py — no scope on st.rerun()
Do NOT add `scope='fragment'` to any `st.rerun()` call. This raises `StreamlitAPIException` in Streamlit 1.43+. Use plain `st.rerun()` only.

## app.py — no MPA primary nav
Do NOT use Streamlit MPA as the primary navigation mechanism. The MPA sidebar is hidden via CSS by design. All routing goes through `app.py` page logic.

## app.py — no _refresh_fragment
Do NOT re-add `_refresh_fragment` to app.py. Removed in v5.26. It was a no-op and its presence caused confusion. It must not return.

## version.py — VERSION_LOG stays here
Do NOT move VERSION_LOG back into config.py. It lives in version.py by design — separating changelog from constants prevents circular import issues and keeps version history auditable.

## tickers.json — GROUPS stays here
Do NOT move GROUPS back into config.py. tickers.json is the master ticker registry. GROUPS is part of market structure and belongs alongside the tickers it describes.

## tickers.json — TATAMOTORS.NS is delisted
Do NOT use `TATAMOTORS.NS`. It is delisted. Use `TMCV.NS` (commercial vehicles) + `TMPV.NS` (passenger vehicles) as the split entities.

## styles.py — CSS in CSS constant only
Do NOT put CSS inside the `inject_css()` docstring. All CSS lives inside the `CSS` string constant. The docstring is for documentation only.

## pages/global_intelligence.py — _render_next_steps_ai removed
Do NOT call `_render_next_steps_ai()` from `render_global_intelligence()`. Removed in v5.31 due to liability risk. The function definition is retained for a future redesign — it must not be wired back up until that redesign is complete and reviewed.

## Sprint discipline — commit after every file
Do NOT batch multiple files into a single commit during active development. Sequence: implement file → run regression → commit → next file. This limits blast radius if a session is interrupted.

## Parallel agents — no git commands
When dispatching parallel worktree agents: agent prompts MUST include "do NOT attempt git add, git commit, or any git command." Agents cannot execute git commands in worktree context. Asking wastes tokens. CTO (main conversation) runs one regression after all agents complete, then commits per the rule above.

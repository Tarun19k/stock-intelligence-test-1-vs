# Recovery: /chief-of-staff recover then read this file first

Checkpoint: 2026-07-25, mid-session (Layer 1-5 Gall's-Law execution, AlphaVeda)

## DO NOT REDO

- **L1-A** — `engine.py` `compute_momentum_signal()` circuit_flag filter — MERGED (`565bd08` lineage, verified 213/213 tests, 0 live circuit rows exist today but adversarial test proves the fix has teeth). Do not re-dispatch.
- **L1-B** — `GainersLosersStrip.tsx` circuit_flag filter + caveat text — MERGED `806883e`. Codex trial 2 succeeded (trial 1 failed on real OpenAI 503s). Verified via diff read + `npm install && npx tsc --noEmit`.
- **L1-C** — SEBI wording fix (Codex) + A13 structural mitigation (Claude), same file, two agents — MERGED `6af7752`. Merge risk flagged and independently re-verified post-merge via grep + fresh `tsc --noEmit` on combined `main`.
- **L2-C** — G21 Lynch content layer (`lynch-narratives.ts`, 234 lines, 15 tickers) — MERGED `2d0f48a`/`dae836c`. Codex trial 2 succeeded. Independently verified: SEBI language grep (zero BUY/SELL/HOLD hits), all 15 tickers spot-checked for genuine business-specific differentiation (not template-swapped), wiring diff is additive-only, `tsc --noEmit` clean on worktree AND re-verified on merged `main`.
- **RF-J logged** (`GAP_REGISTER.md`) and **L1-D queued** (`AGENT_TASK_LOG.md`) — the retail-investor accuracy-ledger honesty gap: `/accuracy` never fetches `magnitude_target`/`downside_target` so Target% can't be shown next to actual Return%; `resolve_outcomes.py`'s `hit` is direction-only (no magnitude check); no page discloses resolution horizon ("X days"). Pushed `ea9c790`.
- All worktrees (`codex-l1b-circuit-fix`, `codex-l1c-wording`, `codex-l2c-lynch-layer`, plus the earlier Claude worktrees for L1-A/L1-C-structural) removed and branches deleted after merge — clean.
- All merges pushed to `origin/main` through `ea9c790`.

## EXACT RESUME POINT

Housekeeping checkpoint in progress (this file). Next action after this checkpoint: dispatch the financial council (AlphaVeda 21-seat council, relevant subset — likely Lynch/panel-lynch, Calibration Integrity, UX/Accessibility (ui-ux-pro-max), Varghese/sebi-compliance-reviewer) for guidance on UI/UX layout and which data points to surface on `/accuracy` and `/instrument/[ticker]`, specifically to satisfy Tarun's retail-investor testing vision: "was the projected price actually right, after X days? was the projection guidance correct?" This directly informs how L1-D should be built — the council guidance should land BEFORE L1-D implementation starts, not after.

## OPEN DECISIONS (Tarun-owned)

| Decision | Impact | Deadline |
|---|---|---|
| L2-A: HDFCBANK/PIDILITIND corporate-action correction — inputs complete (0.5x scale factor, volume ×2 adjustment chosen), not yet executed | Live production data correction, Munger WATCH condition | No hard deadline, but blocks corp-action data integrity |
| L2-B: recurring corporate-action check — cadence chosen (weekly + pre-flight gate), not yet executed | Prevents future corp-action data corruption | No hard deadline |
| L3-A: G20 nav promotion go/no-go | Feature gate | Pending your call |
| L3-B: G1 fundamentals sourcing — manual (~6-8hrs/yr) vs paid API (~$800+/yr floor), real costs sourced by Wealth Strategist | Commercial cost commitment | Pending your call |
| **L1-D UI/UX + data-point design** — about to convene financial council for guidance before build starts | Directly determines what retail investors see on `/accuracy` and `/instrument/[ticker]` | Active this session |

## Commercial state

`waitlist.converted_at` still unreachable (no waitlist route live) — commercial=False, yfinance path active, FMP not yet required. No change this session.

## Parallel session note

None — single workspace (`stock-intelligence-test-1-vs`) this session. `agentic-operations` and `crochet-counter` untouched.

# LiteLLM Proxy — Setup & Roadmap

Smart routing proxy for Claude Code. Routes requests to the best-fit model
based on task type, with human approval before token spend and automatic
fallback to open-source models when paid providers are rate-limited.

---

## Directory Layout

```
litellm-proxy/
├── config.yaml        — 8-tier model list, fallback chains, budget caps
├── .env.example       — key template (copy to .env, never commit .env)
├── .env               — your real keys (git-ignored)
├── approval_hook.py   — human-in-the-loop approval layer (Session 2)
├── start.sh           — one-command proxy launcher
├── .venv/             — isolated Python 3.11 environment (git-ignored)
└── README.md          — this file
```

---

## Model Tiers

| Tier | Model name | Provider | Best for | Cost |
|---|---|---|---|---|
| 1 | `deep-reasoning` | Anthropic claude-opus-4-5 | Architecture, deep debugging, complex reasoning | Paid |
| 2 | `code-gen` | OpenAI gpt-4o | Feature implementation, refactoring | Paid |
| 3 | `fast-cheap` | Gemini gemini-2.0-flash | Boilerplate, docs, comments | Paid (low) |
| 4 | `research` | Perplexity sonar-pro | Web-grounded research, live data | Paid |
| 5 | `quick-qa` | OpenAI gpt-4o-mini | Short Q&A, syntax lookups | Paid (low) |
| 6 | `hf-reasoning` | Groq Llama-3.3-70B-Versatile | Open-source reasoning fallback | **Free** |
| 7 | `hf-code` | Groq Qwen-QwQ-32B | Open-source code fallback | **Free** |
| 8 | `hf-fast` | Groq Llama-3.2-3B-Preview | Open-source boilerplate fallback | **Free** |

### Fallback chain
```
deep-reasoning → code-gen → hf-reasoning → fast-cheap
code-gen       → hf-code  → fast-cheap
fast-cheap     → hf-fast
research       → code-gen → hf-reasoning
quick-qa       → hf-fast  → fast-cheap
```

HF tiers activate automatically when paid providers hit a 429 or daily budget cap.
No manual intervention required.

---

## One-Time Setup (complete)

```bash
# 1. Create isolated Python 3.11 venv (avoids orjson/PyO3 conflict with system Python 3.14)
~/.pyenv/versions/3.11.9/bin/python3 -m venv litellm-proxy/.venv

# 2. Install LiteLLM into the venv
litellm-proxy/.venv/bin/pip install "litellm[proxy]"

# 3. Copy key template and fill in real values
cp litellm-proxy/.env.example litellm-proxy/.env
# Edit litellm-proxy/.env — add your API keys and LITELLM_MASTER_KEY
```

### API keys needed

| Key | Where to get it | Status |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com/settings/keys | Needs credits added |
| `OPENAI_API_KEY` | platform.openai.com/api-keys | Needs billing/credits |
| `GEMINI_API_KEY` | aistudio.google.com → Get API Key | Enable billing to lift free-tier cap |
| `PERPLEXITY_API_KEY` | perplexity.ai/settings/api | Regenerate — current key rejected |
| `HF_TOKEN` | huggingface.co/settings/tokens | Optional — Groq handles free tiers |
| `GROQ_API_KEY` | console.groq.com → API Keys → Create | **Free, no billing required** — powers tiers 6–8 |
| `LITELLM_MASTER_KEY` | You invent it | Any non-guessable string |

> **Note:** The HF tiers (6–8) are free and work independently of the paid providers.
> You can use the proxy with only `HF_TOKEN` + `LITELLM_MASTER_KEY` while billing is being sorted.

---

## Starting the Proxy

**Auto-start via launchd (default — installed, no terminal needed):**
The proxy runs as a macOS background service. It starts on login and restarts on crash.
Logs: `~/Library/Logs/litellm-proxy.log`

```bash
# One-time install (already done)
cp "litellm-proxy/com.gsi.litellm-proxy.plist" ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.gsi.litellm-proxy.plist

# Verify running (PID should be non-zero)
launchctl list | grep gsi

# Stop if needed
launchctl unload ~/Library/LaunchAgents/com.gsi.litellm-proxy.plist
```

**Manual fallback (if launchd not installed):**
```bash
bash litellm-proxy/start.sh
# Proxy running at http://0.0.0.0:4000
```

## Approval UI

The hook auto-detects which UI to use:

| Environment | Behaviour |
|---|---|
| macOS (any) | Native dialog popup — no terminal needed |
| Terminal with tty | Inline prompt with 30s auto-approve timeout |
| Background / CI | Silent auto-approve with log line |

### Health check
```bash
curl -s http://localhost:4000/health \
  -H "Authorization: Bearer YOUR_LITELLM_MASTER_KEY" | python3 -m json.tool
```

---

## Session Workflow

Every session starts with the sprint planner — a plain Python script that reads
`GSI_SPRINT.md` and classifies each item into a model tier. No Claude needed.
This tells you whether to set proxy env vars before launching.

```bash
# Step 1 — check the sprint board (repo root, before launching Claude Code)
python3 litellm-proxy/sprint_planner.py

# Step 2a — proxy items on the board today
source litellm-proxy/.env
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY
claude

# Step 2b — subscription items only
claude   # no env vars

# Step 3 — inside Claude Code (always)
/new-session
```

For mixed sessions (subscription + proxy items), do subscription items first
(unset env vars), then re-launch with env vars for proxy items.

```bash
# Switch from subscription → proxy mid-session
unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN   # back to direct Claude
# or
source litellm-proxy/.env && export ANTHROPIC_BASE_URL=http://localhost:4000 && export ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY
claude   # re-launch with proxy routing
```

## Pointing Claude Code at the Proxy

```bash
source litellm-proxy/.env
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY
claude
```

Claude Code sends Anthropic-format requests. LiteLLM intercepts and translates
to the correct provider transparently — Claude Code requires no changes.

---

## Session Roadmap

### Session 1 — Scaffold (COMPLETE)
- [x] Python 3.11 venv created (isolated from GSI Python 3.14)
- [x] LiteLLM 1.83.3 installed cleanly
- [x] `config.yaml` — 8-tier model list with HF fallbacks
- [x] `.env.example` — all 6 keys documented
- [x] `approval_hook.py` — skeleton with profiles, keyword stubs, `_classify()` helper
- [x] `start.sh` — one-command launcher with env loading
- [x] `.gitignore` — `.env` and `.venv/` excluded
- [x] Proxy smoke-tested: reached all 5 paid providers (errors are billing, not config)

### Session 2 — Wire Approval Hook
- [ ] Tune keyword lists against real Claude Code prompts
- [ ] Validate `_classify()` priority ordering with unit tests
- [ ] Add timeout to `input()` for unattended proxy runs
- [ ] Smoke-test classification: `from approval_hook import _classify`

### Session 3 — Integration Test
- [ ] Update `start.sh` to load the hook:
  ```bash
  exec litellm --config "$SCRIPT_DIR/config.yaml" \
    --plugins "$SCRIPT_DIR/approval_hook.ApprovalLayer"
  ```
- [ ] Export Claude Code env vars and launch
- [ ] Verify approval prompt fires in proxy terminal
- [ ] Test HF fallback: temporarily disable a paid provider, confirm HF tier activates
- [ ] Debug any routing or classification mismatches

---

## Post-MVP Improvements

| Item | Effort | What it gives you |
|---|---|---|
| HF Dedicated Inference Endpoints | Medium | Persistent GPU, no cold starts, consistent latency |
| Cost visibility (`/spend` endpoint) | Low | Per-provider daily spend dashboard via LiteLLM built-in |
| Langfuse integration | Medium | Per-task token analytics, latency traces, cost breakdown |
| GUI approval layer | Medium | Replace terminal `input()` with Streamlit sidebar widget |
| Streamlit app wiring | Low | GSI dashboard reuses same proxy — shared fallback chains |
| Auto-start on login | Low | macOS `launchd` plist — no manual `bash start.sh` each session |

---

## Security Notes

- `.env` is git-ignored at both the repo root level and the `litellm-proxy/` level (double-confirmed)
- `LITELLM_MASTER_KEY` gates all proxy access — treat it like a password
- The proxy runs on `localhost` only — not exposed to the network
- HF token needs only `Read` + `Inference` permissions — do not grant write access

---

## Reusing the Proxy in the GSI Streamlit App

```python
import litellm

response = litellm.completion(
    model="hf-code",          # or any model name from config.yaml
    messages=[{"role": "user", "content": "..."}],
    api_base="http://localhost:4000",
    api_key="YOUR_LITELLM_MASTER_KEY"
)
```

Both Claude Code and the GSI dashboard can share the same running proxy instance.

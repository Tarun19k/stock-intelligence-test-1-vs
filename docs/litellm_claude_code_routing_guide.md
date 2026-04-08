# LiteLLM + Claude Code: Smart API Routing & Token Conservation Guide

## Executive Summary

This document covers a complete architecture for routing Claude Code requests through LiteLLM as a proxy, solving the real-world problem of API rate limits and usage resets that disrupt development timelines. The solution introduces task-aware routing, automatic provider fallbacks, per-provider budget caps, and a human approval layer — giving developers control over token spend *before* execution.

---

## The Problem

Developers relying on a single LLM provider (typically Anthropic's Claude) face three compounding challenges when hitting rate limits:

- **Time loss**: Claude Code's rate limits enforce multi-hour reset windows, stalling work mid-task
- **Context fragmentation**: Interruptions mid-task break flow, forcing expensive re-prompting to restore context
- **Token waste**: Retrying failed requests or using over-powered models for simple tasks burns quota unnecessarily

The root issue is that no single provider is optimal for every task — yet most tooling treats all tasks as equivalent and routes everything to one model.

---

## Fetching Your API Keys

### OpenAI
1. Navigate to **platform.openai.com/api-keys**
2. Click **Create new secret key**, assign a name and optional project scope
3. Copy the key immediately — it is shown only once
4. Store as `OPENAI_API_KEY` in your environment

### Google Gemini
1. Navigate to **aistudio.google.com** and sign in with a Google account
2. Click **Get API Key** → **Create API key**
3. Optionally restrict to the Generative Language API in Google Cloud Console
4. Store as `GEMINI_API_KEY` in your environment

### Perplexity
1. Navigate to **perplexity.ai/settings/api** (or **perplexity.ai/console**)
2. Set up billing if not already configured
3. Click **Generate API Key** — name it descriptively (e.g., `LiteLLM-Router`)
4. Perplexity's API is fully OpenAI-compatible, making it a drop-in for LiteLLM
5. Store as `PERPLEXITY_API_KEY` in your environment

### Anthropic (Claude)
1. Navigate to **console.anthropic.com/settings/keys**
2. Click **Create Key**
3. Store as `ANTHROPIC_API_KEY` in your environment

---

## Installation

```bash
pip install "litellm[proxy]"
```

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                    Claude Code (IDE)                   │
└──────────────────────┬─────────────────────────────────┘
                       │ Anthropic-format requests
                       ▼
┌────────────────────────────────────────────────────────┐
│              LiteLLM Proxy (localhost:4000)             │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  TASK CLASSIFIER  (pre-routing layer)           │   │
│  │  • Detects task type from prompt context        │   │
│  │  • Estimates token cost                         │   │
│  │  • Proposes the best-fit model                  │   │
│  │  • Seeks YOUR approval before execution         │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │ Approved                         │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  SMART ROUTER                                   │   │
│  │  • Routes to approved model                     │   │
│  │  • On 429 → auto fallback (no approval needed)  │   │
│  │  • Budget tracking per provider/day             │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
         │              │              │             │
    Anthropic       OpenAI        Gemini       Perplexity
   (Deep logic)  (Code gen)   (Fast/cheap)  (Search tasks)
```

**Key principle**: Claude Code sends Anthropic-format requests. LiteLLM intercepts them and translates to the appropriate provider's format transparently.

---

## Task-to-Model Mapping Strategy

| Task Type | Recommended Model | Rationale |
|---|---|---|
| Architecture, debugging, complex reasoning | `claude-opus` | Deepest reasoning, highest output quality |
| Feature implementation, code generation | `gpt-4o` or `claude-sonnet` | Fast, reliable, significantly cheaper than Opus |
| Boilerplate, documentation, comments, tests | `gemini-2.0-flash` | Near-free, very fast for mechanical tasks |
| Research, grounded web-based answers | `sonar-pro` (Perplexity) | Built-in real-time search, reduces hallucination retries |
| Quick Q&A, syntax lookups | `gpt-4o-mini` | Cheapest capable model for low-stakes queries |

---

## Core Configuration: `config.yaml`

```yaml
model_list:

  # === TIER 1: Deep reasoning (Anthropic) ===
  - model_name: deep-reasoning
    litellm_params:
      model: anthropic/claude-opus-4-5
      api_key: os.environ/ANTHROPIC_API_KEY
      max_budget: 20.0
      budget_duration: 1d

  # === TIER 2: Code generation (OpenAI) ===
  - model_name: code-gen
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      max_budget: 15.0
      budget_duration: 1d

  # === TIER 3: Fast/cheap tasks (Gemini) ===
  - model_name: fast-cheap
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY
      max_budget: 5.0
      budget_duration: 1d

  # === TIER 4: Research tasks (Perplexity) ===
  - model_name: research
    litellm_params:
      model: perplexity/sonar-pro
      api_key: os.environ/PERPLEXITY_API_KEY
      api_base: https://api.perplexity.ai
      max_budget: 10.0
      budget_duration: 1d

  # === TIER 5: Lightweight Q&A (OpenAI Mini) ===
  - model_name: quick-qa
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
      max_budget: 3.0
      budget_duration: 1d

router_settings:
  # Auto-fallback chain: if primary hits limit, cascade downward
  fallbacks:
    - {"deep-reasoning": ["code-gen", "fast-cheap"]}
    - {"code-gen": ["fast-cheap"]}
    - {"research": ["code-gen"]}
    - {"quick-qa": ["fast-cheap"]}
  num_retries: 2
  retry_after: 5                          # seconds before retry on 429
  routing_strategy: "usage-based-routing-v2"  # tracks live token usage

litellm_settings:
  drop_params: true       # silently ignore unsupported params per provider
  set_verbose: false

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
```

---

## Environment Variables (`.env`)

Create a `.env` file in the same directory. **Never commit this file to version control.**

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...
LITELLM_MASTER_KEY=my-local-proxy-key   # any string — this is your proxy access key
```

Add `.env` to your `.gitignore`:

```bash
echo ".env" >> .gitignore
```

---

## Starting the Proxy

```bash
litellm --config config.yaml
# Proxy running at http://0.0.0.0:4000
```

---

## Pointing Claude Code to the Proxy

Export these environment variables before launching Claude Code:

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=my-local-proxy-key
```

Claude Code will now route all its requests through LiteLLM. From Claude Code's perspective, nothing changes — it still sends Anthropic-format requests. LiteLLM handles translation to the correct provider.

---

## The Approval Layer: Human-in-the-Loop Token Conservation

The custom middleware below intercepts every request *before* it consumes tokens. It classifies the task type, estimates cost, proposes the appropriate model, and waits for your approval — giving you the ability to approve, cancel, or manually override the model choice.

```python
# approval_hook.py
import litellm
from litellm.integrations.custom_logger import CustomLogger

TASK_PROFILES = {
    "architect": {
        "model": "deep-reasoning",
        "description": "Architecture / deep debugging / complex reasoning",
        "threshold_tokens": 2000
    },
    "codegen": {
        "model": "code-gen",
        "description": "Feature implementation / code generation / refactoring",
        "threshold_tokens": 4000
    },
    "boilerplate": {
        "model": "fast-cheap",
        "description": "Tests / docs / comments / boilerplate",
        "threshold_tokens": 99999
    },
    "research": {
        "model": "research",
        "description": "Research / web-grounded lookups / 'what is X'",
        "threshold_tokens": 1000
    },
    "quickqa": {
        "model": "quick-qa",
        "description": "Quick syntax / short Q&A",
        "threshold_tokens": 99999
    }
}

ARCHITECT_KEYWORDS = ["design", "architect", "why", "explain", "debug", "trace",
                      "root cause", "strategy", "approach", "review"]
CODEGEN_KEYWORDS   = ["write", "implement", "refactor", "fix", "create", "build",
                      "add feature", "update", "modify"]
RESEARCH_KEYWORDS  = ["search", "find", "latest", "what is", "research",
                      "current", "news", "price", "rate"]
QUICKQA_KEYWORDS   = ["syntax", "how do i", "what does", "what is the command",
                      "quick", "short"]

class ApprovalLayer(CustomLogger):
    def pre_call(self, model, messages, **kwargs):
        estimated_tokens = sum(len(m["content"].split()) * 1.3 for m in messages)
        last_msg = messages[-1]["content"].lower()

        # Task classification
        if any(w in last_msg for w in ARCHITECT_KEYWORDS):
            task = "architect"
        elif any(w in last_msg for w in RESEARCH_KEYWORDS):
            task = "research"
        elif any(w in last_msg for w in CODEGEN_KEYWORDS):
            task = "codegen"
        elif any(w in last_msg for w in QUICKQA_KEYWORDS):
            task = "quickqa"
        else:
            task = "boilerplate"

        profile = TASK_PROFILES[task]
        suggested_model = profile["model"]

        if estimated_tokens > 300:  # Only prompt for non-trivial requests
            print(f"\n{'='*55}")
            print(f"📋  Task type   : {profile['description']}")
            print(f"🤖  Suggested   : {suggested_model}")
            print(f"📊  Est. tokens : ~{int(estimated_tokens)}")
            print(f"{'='*55}")
            print("Options: [Enter] = approve  |  [n] = cancel  |  [s] = switch model")
            approval = input("→ Your choice: ").strip().lower()

            if approval == "n":
                raise Exception("❌ Request cancelled by user.")
            elif approval == "s":
                print("\nAvailable: deep-reasoning / code-gen / fast-cheap / research / quick-qa")
                alt = input("→ Enter model name: ").strip()
                kwargs["model"] = alt
                print(f"✅ Switched to: {alt}")
            else:
                kwargs["model"] = suggested_model
                print(f"✅ Approved → routing to {suggested_model}")

        return kwargs

# Register the hook
litellm.callbacks = [ApprovalLayer()]
```

To load this hook when starting the proxy:

```bash
litellm --config config.yaml --plugins approval_hook.ApprovalLayer
```

---

## Request Flow: End-to-End

```
1. You type a prompt in Claude Code
2. Approval hook intercepts the request
3. Task is classified (architect / codegen / boilerplate / research / quickqa)
4. Token estimate + suggested model shown to you
5. You approve (Enter), cancel (n), or override (s)
6. LiteLLM routes to the approved model
7. If provider returns 429 → automatic silent fallback to next tier
8. If daily budget is exhausted → LiteLLM skips that provider entirely
9. Response returned to Claude Code in Anthropic format
```

---

## Reusing the Proxy in Your Streamlit App

The same running proxy serves both Claude Code and your fintech application simultaneously. In your Python code:

```python
import litellm

response = litellm.completion(
    model="code-gen",                          # Use any model name from config.yaml
    messages=[{"role": "user", "content": "..."}],
    api_base="http://localhost:4000",
    api_key="my-local-proxy-key"
)
```

This means your Streamlit app benefits from the same fallback chains, budget routing, and provider diversity — without any additional setup.

---

## Current Limitations and Gaps

| Gap | Status | Workaround |
|---|---|---|
| Native Claude Code rate-limit fallback | Not built by Anthropic yet (open GitHub issue) | LiteLLM proxy (this guide) |
| Approval layer GUI | Terminal-only in this implementation | Can be extended to a Streamlit sidebar widget |
| Context preservation across model switches | Partial — message history passed, but model behaviour differs | Use same-family fallbacks where possible (Sonnet → Haiku) |
| Cost visibility dashboard | Not included in base config | Add Langfuse or LiteLLM's built-in `/spend` endpoint |
| Per-task token analytics | Not tracked by default | Enable `success_callback: ["langfuse"]` in `litellm_settings` |

---

## Quick-Start Checklist

- [ ] `pip install "litellm[proxy]"` completed
- [ ] API keys obtained for: Anthropic, OpenAI, Gemini, Perplexity
- [ ] `.env` file created with all four keys + `LITELLM_MASTER_KEY`
- [ ] `.env` added to `.gitignore`
- [ ] `config.yaml` created with model list, fallbacks, and budget caps
- [ ] `approval_hook.py` created and saved
- [ ] Proxy started: `litellm --config config.yaml`
- [ ] Claude Code env vars exported: `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN`
- [ ] Test run: send a prompt in Claude Code and verify approval prompt appears
- [ ] Streamlit app updated to point `api_base` at `localhost:4000`


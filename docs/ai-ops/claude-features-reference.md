# Claude Features Reference — Token Optimization & AI Operations Guide

**Last updated:** April 2026
**Scope:** Claude Code, Claude API (Anthropic API), Claude Agent SDK
**Target audience:** AI engineers optimizing for cost, performance, and session statefulness

---

## 1. Prompt Caching

### What It Is
Caches identical prompt prefixes and reuses them across requests. Cache hits reduce processing cost by **90%**.

### What Gets Cached

| Content Type | Cacheable? | Notes |
|---|---|---|
| Tool definitions (`tools` array) | Yes | Cached automatically |
| System prompts / instructions | Yes | Cached automatically |
| Text, images, documents in messages | Yes | Cacheable up to 4,096 tokens (Haiku) / 2,048 (Sonnet) |
| Tool use blocks & results | Yes | Part of message history |
| Previous thinking blocks | Yes | Auto-excluded from context |
| Empty text blocks | No | Cannot be cached |

### TTLs
- **5-minute TTL (default):** Free; automatically refreshed
- **1-hour TTL:** 2× base input cost; for longer gaps between requests

### Triggering Caching

**Automatic (simplest):**
```python
response = client.messages.create(
    model="claude-opus-4-6",
    cache_control={"type": "ephemeral"},  # Enables automatic caching
    system="Long stable system prompt...",
    messages=[{"role": "user", "content": "Your question"}]
)
```

**Explicit cache breakpoints:**
```python
system=[
    {"type": "text", "text": "Stable instructions...", "cache_control": {"type": "ephemeral"}},
    {"type": "text", "text": "Large reference doc...", "cache_control": {"type": "ephemeral"}}
]
```

**Key principle:** Cache writes at breakpoints. System performs lookback up to 20 blocks. Place stable content first (tools → system → messages).

### Pricing

| Token type | Rate (Opus 4.6) |
|---|---|
| Base input | $5 / MTok |
| Cache write (5-min) | $6.25 / MTok (1.25×) |
| Cache write (1-hour) | $10 / MTok (2×) |
| **Cache read** | **$0.50 / MTok (90% savings)** |

### Tracking Cache Performance
```python
print(response.usage)
# cache_creation_input_tokens: written to cache
# cache_read_input_tokens: retrieved from cache
# input_tokens: tokens after last breakpoint (not cached)
```

### Common Pitfall
❌ Wrong: Changing timestamp prevents cache hits
```python
{"type": "text", "text": f"Timestamp: {now}", "cache_control": {"type": "ephemeral"}}
```
✅ Right: Only mark the last block of stable prefix:
```python
{"type": "text", "text": "Static instructions...", "cache_control": {"type": "ephemeral"}}
{"type": "text", "text": f"Timestamp: {now}"}  # Not cached
```

---

## 2. Memory System

### Types of Memory

| Memory Type | Scope | Auto-loaded? | Use Case |
|---|---|---|---|
| **Session memory** | Single session | N/A | Stateful conversation within one session |
| **Agent memory stores** | Across sessions | Yes (via resources[]) | Persistent learnings via Managed Agents API |
| **MEMORY.md** (Claude Code) | Per project | Yes | Project context loaded at session start |

### Agent Memory Stores (Managed Agents API)

```python
# Create a store
store = client.beta.memory_stores.create(
    name="Project Context",
    description="Per-project decisions and learnings"
)

# Write a memory
client.beta.memory_stores.memories.write(
    memory_store_id=store.id,
    path="/sprint_decisions.md",
    content="v5.37 decisions: DF-01 period=3mo, QUANT-01 parked..."
)

# Attach to session
session = client.beta.sessions.create(
    agent=agent.id,
    resources=[{
        "type": "memory_store",
        "memory_store_id": store.id,
        "access": "read_write",
        "prompt": "Check before starting any task"
    }]
)
```

**Key limits:**
- Max 8 memory stores per session
- Individual memories: ≤100KB (~25k tokens)
- Best practice: Many small focused files over few large ones

**Available memory tools:** `memory_list`, `memory_search`, `memory_read`, `memory_write`, `memory_edit`, `memory_delete`

**Audit trail:** Every mutation creates immutable version (`memver_...`) for rollback and compliance.

### MEMORY.md (Claude Code Auto-Memory)

Auto-created at `~/.claude/projects/<project>/memory/`:
- `MEMORY.md` — index file (loaded at session start, lines after 200 truncated)
- Individual `.md` files for each memory (user, feedback, project, reference types)

**Memory types:**
| Type | When to save | Contents |
|---|---|---|
| `user` | Learn user's role, preferences | Expertise level, working style |
| `feedback` | User corrects or confirms approach | Rule + Why: + How to apply: |
| `project` | Ongoing work, goals, decisions | Fact + Why: + How to apply: |
| `reference` | External system pointers | Where to find authoritative info |

---

## 3. Session Statefulness

### What Persists Across Sessions

| Item | Persists? | How |
|---|---|---|
| Agent definitions | Yes | Agent ID & version |
| Environment config | Yes | Environment ID |
| Memory stores | Yes | `resources[]` attachment |
| Conversation history | No | Must be managed explicitly |
| Tool results | No | Only within single session |

### Pinning Agent Versions
```python
# Pin to specific version for reproducibility
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": 1},
    environment_id=environment.id
)
```

### Session Lifecycle
```
idle → [send message] → running → rescheduling → running → idle
                                  (transient error, auto-retry)
         terminated (unrecoverable error)
```

### Best Practices for Cross-Session Context
1. Use memory stores for learnings that must persist
2. Reference external state (databases, files) rather than embedding in messages
3. Archive sessions when done; pin agent versions for predictable behavior
4. Seed memory at session creation for session-specific context

---

## 4. Managed Agents & Subagents (Claude Code)

### What They Are
Subagents are specialized Claude instances with:
- Independent context windows (no token contention with main session)
- Custom system prompts and scoped tool access
- Foreground (blocking) or background (async) execution

### Foreground vs Background

**Foreground** — wait for result before proceeding:
```
Use when: agent's output is needed before you can continue
```
**Background** — continue working while agent runs:
```
Use when: independent research/compilation that doesn't block next steps
```

### Worktree Isolation

When dispatching via `isolation: "worktree"`:
1. Agent gets an isolated git worktree (separate file copies)
2. No shared state between concurrent agents
3. **Agents cannot run git commands** — write files only
4. File writes persist in main working tree after worktree closes
5. CTO (main conversation) reads diff, runs one regression, then commits

**Mandatory agent prompt fields:**
- File path being edited
- Target function name
- Relevant scoped rules from CLAUDE.md for that file type

### Token Efficiency of Parallel Agents

| Mode | Main context cost | Agent context |
|---|---|---|
| Sequential in main | Adds to main window | — |
| Background agent | ~0 (just notification) | ~20–25k (isolated) |
| Worktree agent (Haiku) | ~0 (just notification) | ~15–18k (isolated) |

**Rule of thumb:** 3 parallel Haiku worktree agents = ~45k agent tokens (isolated) vs ~45k main context if sequential — same token cost but 3× faster.

---

## 5. Context Window Management

### Model Context Sizes

| Model | Context Window | Max Output |
|---|---|---|
| Claude Opus 4.6 | 1M tokens | 128k tokens |
| Claude Sonnet 4.6 | 1M tokens | 64k tokens |
| Claude Haiku 4.5 | 200k tokens | 64k tokens |

### Compaction (Auto-Triggered)

When conversation approaches context limits:
1. Earlier turns summarized (e.g., 50k tokens → 5k tokens)
2. Most recent skill invocations re-attached (first 5k tokens per skill)
3. Re-attached skills share 25k token pool
4. Older skills may drop entirely if pool exhausted

**Recovery:** Re-invoke a skill manually if behavior degrades after compaction.

### Context Awareness (Sonnet 4.6+, Haiku 4.5)

Models receive token budget updates after each tool call:
```xml
<system_warning>Token usage: 35000/1000000; 965000 remaining</system_warning>
```
This enables better task planning and prioritization mid-session.

### Keeping Context Lean

1. Prune old messages after compaction window
2. Cache stable, reusable content (prompt caching)
3. Use Files API for large datasets (referenced, not inlined)
4. Target reads with `offset`/`limit` — never read large files fully
5. Compress documentation into summaries + references
6. Archive completed tasks from conversation history

---

## 6. Model Selection

### Decision Matrix

| Model | Cost | Best For |
|---|---|---|
| **Haiku 4.5** | 1× baseline | High-volume, simple: classification, grepping, doc-only edits, template-filling, targeted single-line changes |
| **Sonnet 4.6** | 3× | Balanced production: multi-section edits, cross-file coherence, sprint planning, moderate architecture |
| **Opus 4.6** | 5× | Complex reasoning: novel algorithm design, security audits, complex multi-file refactors, first-time subsystem design |

### Haiku Qualification (all 3 must be true)
1. Edit location is known (file + function + approximate line)
2. ≤1 judgment call required
3. No cross-file reasoning needed

If ANY fails → Sonnet.

### Cost Ratios
- Haiku input: $1 / MTok
- Sonnet input: $3 / MTok (3×)
- Opus input: $5 / MTok (5×)

---

## 7. Hooks System (Claude Code)

### Hook Types

| Hook | Fires | Exit 2 behavior | Use Case |
|---|---|---|---|
| `PreToolUse` | Before tool runs | **Blocks tool execution** | Pre-checks, regression gates |
| `PostToolUse` | After tool runs | Shows output, continues | Post-processing, doc audits |
| `UserPromptSubmit` | Before message sent | Shows output, continues | Input validation, context injection |

### Example: Regression Gate
```bash
#!/bin/bash
# .claude/hooks/pre_commit.sh
python3 regression.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Regression baseline not passing. Commit blocked."
  exit 2  # Blocks the tool call
fi
exit 0
```

### Configuration in settings.json
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit*)",
        "hooks": [{"type": "command", "command": "bash .claude/hooks/pre_commit.sh"}]
      }
    ]
  }
}
```

---

## 8. MCP Servers (Model Context Protocol)

### What They Are
External tool/data providers integrated via standardized protocol. Extend Claude's capabilities beyond built-in tools.

### Available in Claude Code

| MCP | What it does |
|---|---|
| **Playwright** | Browser automation: navigate, screenshot, fill forms, click, evaluate JS |
| **Figma** | Design API: create components, access design systems |
| **Supabase** | Backend: SQL queries, auth, real-time data |
| **GitHub** | Git + GitHub API: PR creation, issue management |

### Token Implications
- Tool definitions cached across requests (no per-call overhead)
- Tool results inline in conversation (count as input tokens on next turn)
- MCP tools behave identically to built-in tools from a token perspective

---

## 9. Skills & Slash Commands (Claude Code)

### Skill Lifecycle in Context
1. Skill content enters conversation as single message on invocation
2. **Not re-read** on subsequent turns — stays in history
3. During compaction: first 5k tokens of each skill preserved
4. Re-attached skills share 25k token pool after compaction
5. Re-invoke manually if behavior degrades after many turns

### Invocation Control

| Setting | User invoke | Claude invoke | Context behavior |
|---|---|---|---|
| Default | Yes | Yes | Description always loaded; full skill on invoke |
| `disable-model-invocation: true` | Yes | **No** | Description NOT in context; only you can invoke |
| `user-invocable: false` | **No** | Yes | Description always in context; Claude invokes automatically |

### Skill Priority (highest to lowest)
Enterprise > Personal (`~/.claude/skills/`) > Project (`.claude/skills/`) > Plugin

---

## 10. Tool Efficiency

### Dedicated Tools vs Bash

| Task | Prefer | Why |
|---|---|---|
| Find files by pattern | `Glob` over `find`/`ls` | Built-in, permission-aware, faster |
| Search file contents | `Grep` over `grep`/`rg` | Built-in, no sandbox overhead |
| Read files | `Read` over `cat`/`head` | Supports offset/limit, image/PDF |
| Create/edit files | `Write`/`Edit` over `echo`/`sed` | Diff-visible, reversible, tracked |

### Parallel Tool Calls
Multiple independent tool calls in a single message execute in parallel — no extra cost, significant latency savings:
```
# Single message, parallel execution:
[Read(file1), Read(file2), Grep(pattern)]  # All execute simultaneously
```

### Large File Reading Strategy

| File size | Strategy |
|---|---|
| < 100 lines | Read fully |
| 100–300 lines | Read fully if editing; Grep first if searching |
| 300–600 lines | Use offset/limit targeting specific section |
| > 600 lines | Never read fully — always target with offset/limit |
| JSON > 1000 lines | Read only specific keys via offset to known line range |

---

## 11. Batch Processing API

### Cost Structure

| | Regular API | Batch API |
|---|---|---|
| Input tokens | $5 / MTok (Opus) | $2.50 / MTok (**50% off**) |
| Output tokens | $25 / MTok (Opus) | $12.50 / MTok (**50% off**) |
| Processing time | Immediate | < 1 hour typical |

### When to Use
- Large-scale evaluation (1000+ test cases)
- Bulk classification or moderation
- Bulk summarization at fixed intervals

---

## 12. Extended Thinking

### Token Accounting

| Component | Billed? | In Context? |
|---|---|---|
| Thinking (current turn) | Yes (output tokens) | Yes |
| Thinking (previous turns) | Yes (once, on creation) | **No — auto-stripped** |

**Implication:** Previous thinking blocks are free to reuse — no re-billing.

### When to Use
- Complex reasoning, math, code architecture design
- When accuracy delta justifies 2–10× output token cost
- **Skip for:** Simple tasks, real-time chat, single-lookup answers

---

## 13. Free Token Counting API

Pre-count tokens before sending — no charge, helps budget planning:
```python
response = client.messages.count_tokens(
    model="claude-opus-4-6",
    system="You are a scientist",
    messages=[{"role": "user", "content": "Hello, Claude"}]
)
print(response.input_tokens)  # 14
```

Use before dispatching large agents to validate est_tokens in sprint manifest.

---

## 14. Files API (Beta)

Upload once, reference across requests via `file_id`. Saves re-upload overhead for large files used 10+ times.

| Operation | Cost |
|---|---|
| Upload / download / list | **Free** |
| File content in messages | Input token cost for content size |

Max file size: 500 MB. Supported: PDF, plain text, images, CSV/JSON.

---

## 15. Quick Reference: Cost Optimization Checklist

| Optimization | Est. Savings | Complexity |
|---|---|---|
| Haiku instead of Sonnet/Opus | 40–80% | Low |
| Enable prompt caching | 90% on re-reads | Medium |
| Use Batch API | 50% flat | High (async workflow) |
| Parallel agent clusters | Same cost, faster | Medium |
| Targeted offset/limit reads | Pays only for needed section | Low |
| Files API for repeated large files | 30–50% | Low |
| Prune context aggressively | 20–30% | Medium |
| Remove unused tools from tools[] | 5–10% | Low |
| Optimize new-session command | 47k tokens/session | Done ✅ |

---

## 16. GSI-Specific Optimizations (Applied)

| Optimization | Saving | Status |
|---|---|---|
| new-session.md: eliminated GSI_session.json full read | ~42k/session | ✅ Applied |
| new-session.md: eliminated GSI_GOVERNANCE.md read | ~3k/session | ✅ Applied |
| new-session.md: last-50-lines snapshot read | ~5k/session | ✅ Applied |
| Haiku worktree clusters for targeted edits | ~18–20k/cluster | In sprint manifest |
| CLAUDE.md as canonical backlog (not GSI_session.json) | ~42k/lookup | ✅ Policy |
| v5.37c merged into v5.37b | ~20k sprint overhead | ✅ Applied |
| QUANT-01 deferred to v5.38 | ~65k agent | ✅ Applied |

---

*Sources: Anthropic API docs, Claude Code docs, Agent SDK docs — verified April 2026.*

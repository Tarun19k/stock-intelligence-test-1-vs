# approval_hook.py
# Human-in-the-loop approval layer for LiteLLM proxy.
#
# Approval UI priority (auto-detected at runtime):
#   1. macOS native dialog (osascript) — proxy runs in background, popup appears on screen
#   2. Terminal input with timeout    — when stdin is an interactive tty
#   3. Auto-approve with log          — unattended / CI / no tty available

import platform
import select
import subprocess
import sys

from litellm.integrations.custom_logger import CustomLogger

from classifier_keywords import (
    ARCHITECT_KEYWORDS,
    CODEGEN_KEYWORDS,
    QUICKQA_KEYWORDS,
    RESEARCH_KEYWORDS,
)

# ---------------------------------------------------------------------------
# Task profiles — map each task type to a model name from config.yaml
# ---------------------------------------------------------------------------

TASK_PROFILES = {
    "quickqa": {
        "model": "quick-qa",
        "description": "Quick syntax / short Q&A / one-liners",
        "threshold_tokens": 99999,
    },
    "research": {
        "model": "research",
        "description": "Research / web-grounded lookups / documentation",
        "threshold_tokens": 1000,
    },
    "codegen": {
        "model": "code-gen",
        "description": "Feature implementation / code generation / bug fix",
        "threshold_tokens": 4000,
    },
    "architect": {
        "model": "deep-reasoning",
        "description": "Architecture / deep debugging / strategy / audit",
        "threshold_tokens": 2000,
    },
    "boilerplate": {
        "model": "hf-fast",
        "description": "Tests / docs / comments / boilerplate (free tier)",
        "threshold_tokens": 99999,
    },
}

# ---------------------------------------------------------------------------
# Keyword lists — imported from classifier_keywords.py (single source of truth).
# Edit keywords there; changes apply to both runtime routing and sprint planning.
# Priority: quickqa → research → codegen → architect → boilerplate (default)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Classification helper
# ---------------------------------------------------------------------------

def _classify(last_msg: str) -> str:
    """
    Classify a prompt into one of five task types.
    Priority: quickqa → research → codegen → architect → boilerplate (default).

    Priority rationale:
      - quickqa first: short Q&A should never burn expensive quota
      - research before codegen: avoid using code model for lookups
      - codegen before architect: most fix/write tasks don't need Opus
      - architect only when explicitly signalled
      - boilerplate is the safe default for everything else
    """
    if any(w in last_msg for w in QUICKQA_KEYWORDS):
        return "quickqa"
    if any(w in last_msg for w in RESEARCH_KEYWORDS):
        return "research"
    if any(w in last_msg for w in CODEGEN_KEYWORDS):
        return "codegen"
    if any(w in last_msg for w in ARCHITECT_KEYWORDS):
        return "architect"
    return "boilerplate"


# ---------------------------------------------------------------------------
# Approval UI — three modes, auto-detected
# ---------------------------------------------------------------------------

_ALL_MODELS = (
    "deep-reasoning / code-gen / fast-cheap / research / quick-qa"
    " / hf-reasoning / hf-code / hf-fast"
)

_IS_MACOS = platform.system() == "Darwin"


def _osascript(script: str) -> tuple[str, int]:
    """Run an AppleScript snippet and return (stdout, returncode)."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True,
    )
    return result.stdout.strip(), result.returncode


def _macos_approve(profile: dict, estimated_tokens: int) -> tuple[str, str]:
    """
    Show a native macOS dialog. Returns (choice, alt_model).
    choice: "approve" | "cancel" | "switch"
    """
    body = (
        f"Task:      {profile['description']}\\n"
        f"Suggested: {profile['model']}\\n"
        f"Est. tokens: ~{estimated_tokens}"
    )
    script = (
        f'display dialog "{body}" '
        f'with title "LiteLLM Approval" '
        f'buttons {{"Cancel Request", "Switch Model", "Approve"}} '
        f'default button "Approve" '
        f'giving up after 30'
    )
    out, code = _osascript(script)

    if code != 0 or "gave up:true" in out:
        # Dialog timed out or was dismissed — auto-approve
        return "approve", profile["model"]
    if "Cancel Request" in out:
        return "cancel", ""
    if "Switch Model" in out:
        # Second dialog to pick the model
        switch_script = (
            f'display dialog "Enter model name:\\n({_ALL_MODELS})" '
            f'default answer "{profile["model"]}" '
            f'with title "Switch Model" '
            f'giving up after 30'
        )
        switch_out, _ = _osascript(switch_script)
        # Parse: "button returned:OK, text returned:hf-fast"
        alt = profile["model"]
        for part in switch_out.split(","):
            if "text returned" in part:
                alt = part.split(":")[-1].strip()
        return "switch", alt
    return "approve", profile["model"]


def _terminal_approve(profile: dict, estimated_tokens: int, timeout: int = 30) -> tuple[str, str]:
    """
    Interactive terminal approval with timeout.
    Returns (choice, alt_model).
    """
    print(f"\n{'=' * 55}")
    print(f"   Task type   : {profile['description']}")
    print(f"   Suggested   : {profile['model']}")
    print(f"   Est. tokens : ~{estimated_tokens}")
    print(f"{'=' * 55}")
    print("Options: [Enter] approve  |  [n] cancel  |  [s] switch model")
    print("→ Your choice: ", end="", flush=True)

    try:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            print(f"\n[{timeout}s timeout — auto-approving]")
            return "approve", profile["model"]
        choice = sys.stdin.readline().rstrip("\n").strip().lower()
    except (AttributeError, ValueError):
        choice = input().strip().lower()

    if choice == "n":
        return "cancel", ""
    if choice == "s":
        print(f"Available: {_ALL_MODELS}")
        print("→ Enter model name: ", end="", flush=True)
        try:
            ready, _, _ = select.select([sys.stdin], [], [], timeout)
            alt = sys.stdin.readline().rstrip("\n").strip() if ready else profile["model"]
        except (AttributeError, ValueError):
            alt = input().strip()
        return "switch", alt or profile["model"]
    return "approve", profile["model"]


# ---------------------------------------------------------------------------
# Approval layer
# ---------------------------------------------------------------------------

class ApprovalLayer(CustomLogger):
    """
    Pre-call hook: classifies the task, estimates token cost, then asks
    for human approval using whichever UI is available:

      Mode 1 — macOS native dialog (proxy runs in background, popup on screen)
      Mode 2 — Terminal prompt with 30s auto-approve timeout
      Mode 3 — Silent auto-approve with log line (no tty / CI)

    Registered via config.yaml: callbacks: ["approval_hook.approval_layer"]
    (points to the module-level instance below, not the class)
    """

    APPROVAL_THRESHOLD = 50   # tokens below this route silently (~38 words)

    async def async_pre_call_hook(
        self,
        user_api_key_dict: dict,
        cache: object,
        data: dict,
        call_type: str,
    ) -> dict:
        """
        LiteLLM calls this before every request. Mutate data["model"] to reroute.
        Blocking UI calls (osascript, input) are intentional — this is a local dev tool.
        """
        # PROXY-07: Tool-use guard — Groq models do not support the `tools` parameter.
        # Force deep-reasoning (Anthropic) when tools are present; skip approval UI.
        if data.get("tools"):
            data["model"] = "deep-reasoning"
            print(
                f"[LiteLLM tool-use guard] tools detected — forced to deep-reasoning "
                f"(Groq does not support tool_use)"
            )
            return data

        messages = data.get("messages", [])

        estimated_tokens = sum(
            len(m.get("content", "").split()) * 1.3
            for m in messages
            if isinstance(m.get("content"), str)
        )

        raw_content = messages[-1].get("content", "") if messages else ""
        if isinstance(raw_content, list):
            # Claude Code sends content as a list of typed blocks — extract text
            last_content = " ".join(
                block.get("text", "")
                for block in raw_content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            last_content = raw_content
        task = _classify(last_content.lower())
        profile = TASK_PROFILES[task]
        suggested_model = profile["model"]

        if estimated_tokens <= self.APPROVAL_THRESHOLD:
            data["model"] = suggested_model
            return data

        # Pick approval UI
        if _IS_MACOS:
            choice, alt = _macos_approve(profile, int(estimated_tokens))
        elif sys.stdin.isatty():
            choice, alt = _terminal_approve(profile, int(estimated_tokens))
        else:
            print(
                f"[LiteLLM auto-approve] task={task} "
                f"model={suggested_model} tokens=~{int(estimated_tokens)}"
            )
            choice, alt = "approve", suggested_model

        if choice == "cancel":
            raise Exception("Request cancelled by user.")
        if choice == "switch":
            data["model"] = alt
            print(f"Switched to: {alt}")
        else:
            data["model"] = suggested_model
            print(f"Approved — routing to {suggested_model}")

        return data

    async def async_success_callback(
        self,
        kwargs: dict,
        response_obj: object,
        start_time: object,
        end_time: object,
    ) -> None:
        """
        PROXY-02: Fallback transparency — log when the model that actually served
        the request differs from what was requested (e.g. paid model fell back to Groq).
        """
        requested = (kwargs.get("model") or "").strip()
        actual    = getattr(response_obj, "model", None) or ""
        actual    = actual.strip()

        if requested and actual and requested != actual:
            print(
                f"[LiteLLM fallback] requested={requested!r} → actual={actual!r} "
                f"(model substitution occurred)"
            )


# Module-level instance — config.yaml points to this, not the class.
# LiteLLM's get_instance_fn() does getattr(module, name) and needs an instance,
# not a class. Pointing at "approval_hook.approval_layer" returns this object directly.
approval_layer = ApprovalLayer()

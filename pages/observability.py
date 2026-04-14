# pages/observability.py
# Depends on: market_data, config, version
# Entry point: render_observability() — called from app.py routing (direct URL only)
#
# Founder-only internal page. Not in public nav — hidden via existing CSS.
# Access: gated by st.secrets["DEV_TOKEN"] + PIN entry.
# Two tabs:
#   App Health  — live cache warmth, rate-limit state, hit/miss ratios, latency
#   Program     — sprint velocity, open items, audit counts, compliance status

import re
import json
import os
import subprocess
import pytz
from datetime import datetime

import streamlit as st

from config import MARKET_SESSIONS, CURRENT_VERSION
from market_data import get_health_stats, get_rate_limit_state, is_ticker_cache_warm
from version import VERSION_LOG

# ── Gate helpers ───────────────────────────────────────────────────────────────

def _get_dev_token() -> str:
    try:
        return st.secrets.get("DEV_TOKEN", "")
    except Exception:
        return ""


def _render_gate() -> bool:
    """Show PIN entry. Returns True when unlocked."""
    st.markdown("### App internals")
    st.caption("This page is not public.")
    pin = st.text_input("Access code", type="password", key="obs_pin_input")
    if st.button("Unlock", key="obs_unlock_btn"):
        token = _get_dev_token()
        if token and pin == token:
            st.session_state["obs_unlocked"] = True
            st.rerun()
        else:
            st.error("Wrong code.")
    return False


# ── Market status helpers ──────────────────────────────────────────────────────

def _market_status_rows() -> list:
    """Return list of (market, tz, open_time, close_time, is_open) tuples."""
    rows = []
    for market, sess in MARKET_SESSIONS.items():
        tz_name = sess.get("tz", "UTC")
        tz      = pytz.timezone(tz_name)
        now     = datetime.now(tz)
        if now.weekday() >= 5:
            rows.append((market, tz_name, sess["open"], sess["close"], False))
            continue
        o_h, o_m = sess["open"]
        c_h, c_m = sess["close"]
        open_dt  = now.replace(hour=o_h, minute=o_m, second=0, microsecond=0)
        close_dt = now.replace(hour=c_h, minute=c_m, second=0, microsecond=0)
        is_open  = open_dt <= now < close_dt
        rows.append((market, tz_name, sess["open"], sess["close"], is_open))
    return rows


# ── Tab: App Health ────────────────────────────────────────────────────────────

@st.fragment(run_every=10)
def _tab_app_health() -> None:
    st.caption("Refreshes every 10 seconds.")

    stats = get_health_stats()
    rl    = get_rate_limit_state()

    # Row 1 — rate limit + cache warmth
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Rate limit",
        "cooling down" if rl["in_cooldown"] else "clear",
        delta=f"{rl['seconds_remaining']}s left" if rl["in_cooldown"] else None,
        delta_color="inverse",
    )
    c2.metric("Consecutive 429s", rl["consecutive_429s"])
    c3.metric("Cache entries",    stats["cache_size"])
    c4.metric(
        "Cache hit rate",
        f"{stats['hit_rate_pct']}%",
        delta=f"{stats['cache_hits']} hits / {stats['cache_misses']} misses",
    )

    st.divider()

    # Row 2 — fetch latency
    c5, c6 = st.columns(2)
    c5.metric("Avg fetch time",  f"{stats['avg_fetch_ms']} ms")
    c6.metric("P95 fetch time",  f"{stats['p95_fetch_ms']} ms")

    samples = stats["latency_samples"]
    if samples:
        import plotly.graph_objects as go
        fig = go.Figure(go.Scatter(
            y=samples,
            mode="lines+markers",
            line={"color": "#4C9BE8", "width": 1.5},
            marker={"size": 4},
            name="fetch ms",
        ))
        fig.update_layout(
            title="Fetch latency: last 20 samples (ms)",
            height=200,
            margin={"t": 36, "b": 24, "l": 32, "r": 8},
            yaxis_title="ms",
            xaxis_title="sample",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e0e0e0", "size": 11},
        )
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    st.divider()

    # Row 3 — error counts
    errors = stats["error_counts"]
    st.markdown(f"**Fetch errors: {stats['total_errors']} total**")
    if errors:
        err_rows = sorted(errors.items(), key=lambda x: x[1], reverse=True)
        cols = st.columns(min(4, len(err_rows)))
        for i, (sym, cnt) in enumerate(err_rows[:8]):
            cols[i % len(cols)].metric(sym, cnt)
    else:
        st.caption("No fetch errors recorded this session.")

    st.divider()

    # Row 4 — market open/closed status
    st.markdown("**Market sessions**")
    market_rows = _market_status_rows()
    hdr_cols = st.columns([2, 2, 1, 1, 1])
    hdr_cols[0].caption("Market")
    hdr_cols[1].caption("Timezone")
    hdr_cols[2].caption("Open")
    hdr_cols[3].caption("Close")
    hdr_cols[4].caption("Status")
    for market, tz_name, open_t, close_t, is_open in market_rows:
        row = st.columns([2, 2, 1, 1, 1])
        row[0].write(market)
        row[1].caption(tz_name)
        row[2].caption(f"{open_t[0]:02d}:{open_t[1]:02d}")
        row[3].caption(f"{close_t[0]:02d}:{close_t[1]:02d}")
        row[4].write("OPEN" if is_open else "closed")


# ── Tab: Program ───────────────────────────────────────────────────────────────

def _read_file_safe(path: str) -> str:
    """Read a repo-root governance doc. Returns empty string if missing."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


# ── Feed parsers (cached, used by Sprint Monitor + Risk & Compliance tabs) ────

@st.cache_data(ttl=300)
def _parse_sprint_manifest() -> dict:
    """Parse GSI_SPRINT_MANIFEST.json. Returns structured dict with graceful fallback."""
    try:
        with open("GSI_SPRINT_MANIFEST.json", encoding="utf-8") as f:
            raw = json.load(f)
        items = [it for it in raw.get("items", []) if "_section" not in it]
        done  = [it for it in items if it.get("status") == "DONE"]
        tb    = raw.get("token_budget", {})
        return {
            "sprint_version": raw.get("sprint_version", "?"),
            "status":         raw.get("status", "?"),
            "baseline":       raw.get("regression_baseline_entering", "?"),
            "items":          items,
            "done_count":     len(done),
            "total_count":    len(items),
            "token_budget":   tb,
            "file_change_log": raw.get("file_change_log", []),
            "checks":         raw.get("checks", []),
            "error_msg":      None,
        }
    except FileNotFoundError:
        return {"error_msg": "GSI_SPRINT_MANIFEST.json not found", "items": [], "checks": []}
    except Exception as e:
        return {"error_msg": str(e), "items": [], "checks": []}


@st.cache_data(ttl=300)
def _parse_risk_register() -> list:
    """Parse GSI_RISK_REGISTER.md. Returns list of {id, severity, category, status, description}."""
    try:
        with open("GSI_RISK_REGISTER.md", encoding="utf-8") as f:
            text = f.read()
        rows = []
        # Match markdown table rows: | RISK-T01 | HIGH | Technical | Open | description... |
        pattern = re.compile(
            r"\|\s*(RISK-[A-Z0-9\-]+)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|"
        )
        for m in pattern.finditer(text):
            rows.append({
                "id":          m.group(1).strip(),
                "severity":    m.group(2).strip(),
                "category":    m.group(3).strip(),
                "status":      m.group(4).strip(),
                "description": m.group(5).strip()[:120],
            })
        return rows
    except FileNotFoundError:
        return [{"error_msg": "GSI_RISK_REGISTER.md not found"}]
    except Exception as e:
        return [{"error_msg": str(e)}]


@st.cache_data(ttl=300)
def _parse_compliance_output() -> dict:
    """Run compliance_check.py via subprocess. Returns {gates, summary, error_msg}."""
    try:
        result = subprocess.run(
            ["python3", "compliance_check.py"],
            capture_output=True, text=True, timeout=15,
        )
        stdout = result.stdout.strip()
        lines  = stdout.splitlines()
        # First line: "N/M compliance checks passed"
        summary = lines[0] if lines else "no output"
        gates = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("FAIL:"):
                gates.append({"id": line[5:].strip(), "status": "FAIL"})
        # Passed gates not listed in output — derive from summary
        m = re.search(r"(\d+)/(\d+)", summary)
        if m:
            passed_n = int(m.group(1))
            total_n  = int(m.group(2))
            failed_ids = {g["id"] for g in gates}
            # We only know failed gate names; passed gates are unnamed in stdout
            for i in range(passed_n):
                gates.insert(i, {"id": f"check_{i+1}", "status": "PASS"})
        return {"gates": gates, "summary": summary, "return_code": result.returncode, "error_msg": None}
    except subprocess.TimeoutExpired:
        return {"gates": [], "summary": "timeout", "return_code": -1, "error_msg": "compliance_check.py timed out (15s)"}
    except Exception as e:
        return {"gates": [], "summary": "error", "return_code": -1, "error_msg": str(e)}


@st.cache_data(ttl=300)
def _parse_snapshot_history() -> list:
    """Parse SNAPSHOT-NNN blocks from GSI_SESSION_SNAPSHOT.md.
    Returns list of {snapshot_id, session, date, version, qset, deviations, q01_baseline, is_resume}
    ordered newest-first."""
    try:
        with open("GSI_SESSION_SNAPSHOT.md", encoding="utf-8") as f:
            text = f.read()
        blocks = re.split(r"(?=^## SNAPSHOT-\d+)", text, flags=re.MULTILINE)
        results = []
        for block in blocks:
            m = re.match(
                r"## (SNAPSHOT-(\d+))\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)(\s*\|\s*RESUME)?\s*$",
                block.strip().splitlines()[0] if block.strip() else "",
            )
            if not m:
                continue
            snap_id   = m.group(1)
            snap_num  = int(m.group(2))
            date      = m.group(3).strip()
            session   = m.group(4).strip()
            version   = m.group(5).strip()
            qset      = m.group(6).strip()
            is_resume = bool(m.group(7))

            # Extract deviations from italic summary line
            dev_m = re.search(r"Deviations:\s*([^\.\*]+)", block)
            deviations = dev_m.group(1).strip() if dev_m else "?"

            # Extract Q01 baseline
            q01_m = re.search(r"\*\*Q01[^\*]*\*\*[:\s]+([^\n]+)", block)
            q01   = q01_m.group(1).strip() if q01_m else "?"

            results.append({
                "snapshot_id": snap_id,
                "snap_num":    snap_num,
                "date":        date,
                "session":     session,
                "version":     version,
                "qset":        qset,
                "is_resume":   is_resume,
                "deviations":  deviations,
                "q01_baseline": q01,
            })
        results.sort(key=lambda x: x["snap_num"], reverse=True)
        return results
    except FileNotFoundError:
        return [{"error_msg": "GSI_SESSION_SNAPSHOT.md not found"}]
    except Exception as e:
        return [{"error_msg": str(e)}]


@st.cache_data(ttl=300)
def _parse_session_learnings() -> list:
    """Parse RECORD-NNN blocks from GSI_SESSION_LEARNINGS.md.
    Returns list of {record_id, session, date, findings} ordered newest-first."""
    try:
        with open("GSI_SESSION_LEARNINGS.md", encoding="utf-8") as f:
            text = f.read()
        blocks = re.split(r"(?=^## RECORD-\d+)", text, flags=re.MULTILINE)
        results = []
        for block in blocks:
            m = re.match(
                r"## (RECORD-(\d+))\s*\|\s*([^\|]+?)\s*\|\s*([^\n]+)",
                block.strip().splitlines()[0] if block.strip() else "",
            )
            if not m:
                continue
            rec_id  = m.group(1)
            rec_num = int(m.group(2))
            session = m.group(3).strip()
            date    = m.group(4).strip()
            # Collect body up to 400 chars
            body_lines = block.strip().splitlines()[1:]
            findings   = " ".join(ln.strip() for ln in body_lines if ln.strip())[:400]
            results.append({
                "record_id": rec_id,
                "rec_num":   rec_num,
                "session":   session,
                "date":      date,
                "findings":  findings,
            })
        results.sort(key=lambda x: x["rec_num"], reverse=True)
        return results
    except FileNotFoundError:
        return [{"error_msg": "GSI_SESSION_LEARNINGS.md not found"}]
    except Exception as e:
        return [{"error_msg": str(e)}]


# ── Existing parsers (used by existing _tab_program) ──────────────────────────

def _parse_audit_counts(text: str) -> dict:
    """Count audit finding statuses from GSI_AUDIT_TRAIL.md."""
    fixed   = len(re.findall(r"\bFIXED\b",   text))
    partial = len(re.findall(r"\bPARTIAL\b", text))
    open_   = len(re.findall(r"\bOPEN\b",    text))
    return {"fixed": fixed, "partial": partial, "open": open_,
            "total": fixed + partial + open_}


def _parse_risk_counts(text: str) -> dict:
    """Count risk statuses from GSI_RISK_REGISTER.md."""
    mitigated = len(re.findall(r"\bMitigated\b", text, re.IGNORECASE))
    open_     = len(re.findall(r"\bOpen\b",      text, re.IGNORECASE))
    return {"mitigated": mitigated, "open": open_}


def _parse_sprint_velocity(text: str) -> list:
    """Extract sprint rows from GSI_SPRINT.md Done section. Returns list of dicts."""
    pattern = r"\|\s*(v\d+\.\d+[^\|]*?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
    rows    = []
    for m in re.finditer(pattern, text):
        rows.append({
            "sprint":   m.group(1).strip(),
            "planned":  int(m.group(2)),
            "delivered": int(m.group(3)),
        })
    return rows[-8:]  # last 8 sprints max


def _inline_compliance_check() -> dict:
    """Run the 8 compliance checks inline. Returns dict of name → bool."""
    try:
        db  = _read_file_safe("pages/dashboard.py")
        gi  = _read_file_safe("pages/global_intelligence.py")
        md  = _read_file_safe("market_data.py")
        ind = _read_file_safe("indicators.py")
        return {
            "SEBI disclaimer":         "SEBI-registered investment advisor" in db,
            "Algo disclosure":         "algorithmically generated" in db.lower(),
            "No raw score":            "Momentum: {score}/100" not in db,
            "No red flags fallback":   '"No major red flags at this time."' not in db,
            "ROE null guard":          "roe_str" in db,
            "Next steps removed":      len(re.findall(r"(?<!def )_render_next_steps_ai\(\)", gi)) == 0,
            "RATES CONTEXT":           "RATES CONTEXT" in ind,
            "Rate limit gate":         "_is_rate_limited()" in md,
        }
    except Exception:
        return {}


def _tab_program() -> None:
    # Sprint manifest
    manifest_text = _read_file_safe("GSI_SPRINT_MANIFEST.json")
    if manifest_text:
        try:
            manifest = json.loads(manifest_text)
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Sprint",  manifest.get("sprint", "—"))
            mc2.metric("Status",  manifest.get("status", "—"))
            mc3.metric("Baseline checks", manifest.get("baseline_before", "—"))
            checks      = manifest.get("checks", [])
            tier_a      = [c for c in checks if c.get("tier") == "A"]
            tier_b      = [c for c in checks if c.get("tier") == "B"]
            st.caption(f"{len(tier_a)} Tier A gates · {len(tier_b)} Tier B checks · "
                       f"{len(manifest.get('file_change_log', []))} files logged")
        except Exception:
            st.caption("Manifest present but could not parse.")
    else:
        st.caption("No sprint manifest found.")

    st.divider()

    # Audit trail counts
    audit_text = _read_file_safe("GSI_AUDIT_TRAIL.md")
    audit      = _parse_audit_counts(audit_text)
    st.markdown("**Audit trail**")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Fixed",   audit["fixed"])
    a2.metric("Partial", audit["partial"])
    a3.metric("Open",    audit["open"])
    a4.metric("Total",   audit["total"])

    st.divider()

    # Risk register counts
    risk_text = _read_file_safe("GSI_RISK_REGISTER.md")
    risk      = _parse_risk_counts(risk_text)
    st.markdown("**Risk register**")
    r1, r2 = st.columns(2)
    r1.metric("Mitigated", risk["mitigated"])
    r2.metric("Open",      risk["open"])

    st.divider()

    # Sprint velocity chart
    sprint_text = _read_file_safe("GSI_SPRINT.md")
    velocity    = _parse_sprint_velocity(sprint_text)
    st.markdown("**Sprint velocity**")
    if velocity:
        import plotly.graph_objects as go
        labels    = [r["sprint"]    for r in velocity]
        planned   = [r["planned"]   for r in velocity]
        delivered = [r["delivered"] for r in velocity]
        fig = go.Figure()
        fig.add_bar(x=labels, y=planned,   name="planned",   marker_color="#4a4a6a")
        fig.add_bar(x=labels, y=delivered, name="delivered", marker_color="#4C9BE8")
        fig.update_layout(
            barmode="group",
            height=220,
            margin={"t": 16, "b": 24, "l": 32, "r": 8},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e0e0e0", "size": 11},
            legend={"orientation": "h", "y": 1.1},
        )
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
    else:
        st.caption("No velocity data found in GSI_SPRINT.md.")

    st.divider()

    # Inline compliance check
    st.markdown("**Compliance check** (8 gates)")
    results = _inline_compliance_check()
    if results:
        fails = [name for name, ok in results.items() if not ok]
        passed = len(results) - len(fails)
        if fails:
            st.error(f"{passed}/{len(results)} checks passed")
            for name in fails:
                st.write(f"FAIL: {name}")
        else:
            st.success(f"{passed}/{len(results)} — all clear")
    else:
        st.caption("Could not run compliance check.")

    # Version log — last 5
    st.divider()
    st.markdown("**Recent versions**")
    for entry in reversed(VERSION_LOG[-5:]):
        st.markdown(f"**{entry['version']}** · {entry['date']}")
        st.caption(entry["notes"][:200])


# ── Tab: Sprint Monitor ────────────────────────────────────────────────────────

_STATUS_COLOUR = {
    "DONE":        "#2e7d32",
    "IN_PROGRESS": "#f57c00",
    "pending":     "#546e7a",
    "blocked":     "#c62828",
}

_MODEL_BADGE = {
    "haiku":  "🟢 haiku",
    "sonnet": "🔵 sonnet",
    "opus":   "🟣 opus",
}


def _status_label(status: str) -> str:
    colour = _STATUS_COLOUR.get(status, "#546e7a")
    label  = status.upper() if status else "?"
    return f'<span style="color:{colour};font-weight:600">{label}</span>'


def _render_sprint_monitor_tab() -> None:
    """Sprint Monitor tab — manifest item table, token burn, next item card, git status."""
    try:
        manifest = _parse_sprint_manifest()
    except Exception as e:
        st.warning(f"Could not load sprint manifest: {e}")
        return

    if manifest.get("error_msg"):
        st.info(f"No active sprint manifest. ({manifest['error_msg']})")
        return

    sprint  = manifest["sprint_version"]
    status  = manifest["status"]
    items   = manifest["items"]
    done_n  = manifest["done_count"]
    total_n = manifest["total_count"]

    # ── Header KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Sprint",   sprint)
    k2.metric("Status",   status)
    k3.metric("Progress", f"{done_n}/{total_n}")
    k4.metric("Baseline", str(manifest["baseline"]))

    st.divider()

    # ── Manifest item table ──
    st.markdown("**Sprint items**")
    if not items:
        st.caption("No items in manifest.")
    else:
        import pandas as pd
        rows = []
        for it in items:
            files_str = ", ".join(it.get("files", []))
            rows.append({
                "ID":         it.get("id", "?"),
                "Sub":        it.get("sub_sprint", "?"),
                "Model":      _MODEL_BADGE.get(it.get("model", ""), it.get("model", "?")),
                "Mode":       it.get("mode", "?"),
                "Status":     it.get("status", "?"),
                "Est tokens": it.get("est_tokens", "?"),
                "Files":      files_str[:60] + ("…" if len(files_str) > 60 else ""),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Token budget burn chart ──
    st.markdown("**Token budget: est vs actual**")
    try:
        tb_items = manifest.get("token_budget", {}).get("items", [])
        if not tb_items:
            st.caption("No token_budget.items in manifest.")
        else:
            import pandas as pd
            import plotly.graph_objects as go

            ids     = [it["id"] for it in tb_items]
            est_mid = []
            for it in tb_items:
                s = str(it.get("est_tokens", "0")).lower().replace("k", "")
                parts = s.split("–") if "–" in s else s.split("-")
                try:
                    nums = [float(p.strip()) for p in parts if p.strip()]
                    est_mid.append(sum(nums) / len(nums) if nums else 0)
                except ValueError:
                    est_mid.append(0)

            # Try to read actuals from token-burn-log.jsonl
            actuals_map = {}
            try:
                with open("docs/ai-ops/token-burn-log.jsonl") as lf:
                    for line in lf:
                        line = line.strip()
                        if not line:
                            continue
                        entry = json.loads(line)
                        if entry.get("sprint") == sprint:
                            for log_it in entry.get("items", []):
                                a = log_it.get("actual_tokens")
                                if a is not None:
                                    actuals_map[log_it["id"]] = a / 1000.0
            except Exception:
                pass

            actuals = [actuals_map.get(i) for i in ids]

            fig = go.Figure()
            fig.add_bar(
                x=ids, y=est_mid,
                name="est (midpoint k)", marker_color="#4a4a6a",
            )
            if any(a is not None for a in actuals):
                fig.add_bar(
                    x=ids,
                    y=[a if a is not None else 0 for a in actuals],
                    name="actual k",
                    marker_color="#4C9BE8",
                    opacity=[1.0 if a is not None else 0.3 for a in actuals],
                )
            fig.update_layout(
                barmode="group",
                height=240,
                margin={"t": 16, "b": 60, "l": 32, "r": 8},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#e0e0e0", "size": 11},
                legend={"orientation": "h", "y": 1.12},
                xaxis_tickangle=-30,
            )
            st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
    except Exception as e:
        st.warning(f"Token budget chart unavailable: {e}")

    st.divider()

    # ── Next item card ──
    st.markdown("**Next item**")
    try:
        pending = [it for it in items if it.get("status") not in ("DONE",)]
        if not pending:
            st.success(f"All {total_n} items DONE — sprint ready to close.")
        elif status == "PLANNING":
            st.info("Sprint not started yet — no items in progress.")
        else:
            nxt = pending[0]
            model_str = _MODEL_BADGE.get(nxt.get("model", ""), nxt.get("model", "?"))
            st.info(
                f"**{nxt.get('id', '?')}** · {model_str} · `{nxt.get('mode', '?')}`\n\n"
                f"**Pass criterion:** {nxt.get('pass_criterion', '?')}\n\n"
                f"**Files:** {', '.join(nxt.get('files', []))}\n\n"
                f"**Est tokens:** {nxt.get('est_tokens', '?')}"
            )
            perms = nxt.get("permissions_required", [])
            if perms:
                st.caption("Permissions: " + " · ".join(perms))
    except Exception as e:
        st.warning(f"Next item card unavailable: {e}")

    st.divider()

    # ── Pending git commits ──
    st.markdown("**Uncommitted changes** (git status)")
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, timeout=5,
        )
        lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
        if lines:
            st.metric("Uncommitted files", len(lines))
            st.code("\n".join(lines), language=None)
        else:
            st.caption("Working tree clean.")
    except Exception as e:
        st.warning(f"git status unavailable: {e}")


# ── Tab: Risk & Compliance ────────────────────────────────────────────────────

# SEBI disclaimer pages from CLAUDE.md scoped rules + compliance_check checks
_SEBI_PAGES = [
    ("pages/dashboard.py",             "SEBI-registered investment advisor"),
    ("pages/global_intelligence.py",   "SEBI-registered investment advisor"),
    ("pages/week_summary.py",          "SEBI-registered investment advisor"),
    ("pages/home.py",                  "SEBI-registered investment advisor"),
]

_SEVERITY_ORDER = ["HIGH", "CRITICAL", "MED", "MEDIUM", "LOW"]
_SEVERITY_COLOUR = {
    "CRITICAL": "#b71c1c",
    "HIGH":     "#c62828",
    "MED":      "#f57c00",
    "MEDIUM":   "#f57c00",
    "LOW":      "#388e3c",
}


@st.cache_data(ttl=300)
def _parse_loophole_log() -> list:
    """Parse GSI_LOOPHOLE_LOG.md — returns list of {class_name, trigger, gate, count}."""
    try:
        with open("GSI_LOOPHOLE_LOG.md", encoding="utf-8") as f:
            text = f.read()
        # Table rows: | **Class name** | trigger | gate |
        pattern = re.compile(r"\|\s*\*\*([^\*]+)\*\*\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|")
        rows = []
        for m in pattern.finditer(text):
            rows.append({
                "class_name": m.group(1).strip(),
                "trigger":    m.group(2).strip()[:80],
                "gate":       m.group(3).strip()[:80],
            })
        return rows
    except FileNotFoundError:
        return []
    except Exception:
        return []


def _render_risk_compliance_tab() -> None:
    """Risk & Compliance tab — risk heatmap, compliance gates, SEBI exposure map."""

    # ── 1. Risk heatmap ──
    st.markdown("**Risk register — severity × category**")
    try:
        risks = _parse_risk_register()
        if risks and "error_msg" in risks[0]:
            st.warning(risks[0]["error_msg"])
        elif not risks:
            st.caption("No risk data found.")
        else:
            open_risks  = [r for r in risks if "open" in r.get("status", "").lower()]
            mit_risks   = [r for r in risks if "mitigated" in r.get("status", "").lower()]
            st.metric("Open risks", len(open_risks), delta=f"{len(mit_risks)} mitigated", delta_color="off")

            if open_risks:
                import pandas as pd, plotly.graph_objects as go

                categories = sorted({r.get("category", "Other") for r in open_risks})
                severities = [s for s in _SEVERITY_ORDER if any(
                    r.get("severity", "").upper() == s.upper() for r in open_risks
                )]

                # Build count matrix
                z = []
                for sev in severities:
                    row = []
                    for cat in categories:
                        count = sum(
                            1 for r in open_risks
                            if r.get("severity", "").upper() == sev.upper()
                            and r.get("category", "Other") == cat
                        )
                        row.append(count)
                    z.append(row)

                fig = go.Figure(go.Heatmap(
                    z=z, x=categories, y=severities,
                    colorscale=[[0, "#1a1a2e"], [0.5, "#c62828"], [1, "#ff1744"]],
                    showscale=False,
                    text=[[str(v) if v > 0 else "" for v in row] for row in z],
                    texttemplate="%{text}",
                ))
                fig.update_layout(
                    height=180,
                    margin={"t": 8, "b": 40, "l": 60, "r": 8},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#e0e0e0", "size": 11},
                )
                st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

                # Drill-down expanders by severity
                for sev in severities:
                    sev_risks = [r for r in open_risks if r.get("severity", "").upper() == sev.upper()]
                    colour    = _SEVERITY_COLOUR.get(sev.upper(), "#546e7a")
                    with st.expander(f"{sev} ({len(sev_risks)} open)", expanded=(sev in ("HIGH", "CRITICAL"))):
                        for r in sev_risks:
                            st.markdown(
                                f"**{r['id']}** · `{r.get('category','?')}` · {r.get('description','')}"
                            )
            else:
                st.success("No open risks — all mitigated.")
    except Exception as e:
        st.warning(f"Risk heatmap unavailable: {e}")

    st.divider()

    # ── 2. Compliance gate table ──
    st.markdown("**Compliance gates** (live check)")
    try:
        comp = _parse_compliance_output()
        if comp.get("error_msg"):
            st.warning(f"compliance_check.py error: {comp['error_msg']}")
        else:
            summary = comp.get("summary", "?")
            rc      = comp.get("return_code", -1)
            if rc == 0:
                st.success(summary)
            else:
                st.error(summary)

            # Build display from stdout — re-run to get named results
            try:
                result2 = subprocess.run(
                    ["python3", "compliance_check.py"],
                    capture_output=True, text=True, timeout=15,
                )
                lines = result2.stdout.strip().splitlines()
                fail_names = set()
                for line in lines[1:]:
                    if line.strip().startswith("FAIL:"):
                        fail_names.add(line.strip()[5:].strip())

                # Known gate list from compliance_check.py
                gate_defs = [
                    ("SEBI disclaimer",            "SEBI text in dashboard.py"),
                    ("Algo disclosure",             "algorithmically generated in dashboard.py"),
                    ("No raw score",                "Momentum: {score}/100 absent from dashboard.py"),
                    ("No red flags fallback",       "No major red flags fallback absent"),
                    ("ROE null guard",              "roe_str guard in dashboard.py"),
                    ("Next steps removed",          "_render_next_steps_ai() not called in global_intelligence.py"),
                    ("RATES CONTEXT",               "RATES CONTEXT in indicators.py"),
                    ("Rate limit gate",             "_is_rate_limited() in market_data.py"),
                    ("Deps doc current when req changed", "requirements.txt ≤ GSI_DEPENDENCIES.md by commit date"),
                    ("SEBI disclaimer (week_summary)",    "SEBI text in week_summary.py"),
                ]
                import pandas as pd
                gate_rows = [
                    {
                        "Gate":        name,
                        "Status":      "FAIL" if name in fail_names else "PASS",
                        "Description": desc,
                    }
                    for name, desc in gate_defs
                ]
                df_gates = pd.DataFrame(gate_rows)
                st.dataframe(df_gates, use_container_width=True, hide_index=True)
            except Exception:
                st.caption("Gate detail table unavailable — showing summary only.")
    except Exception as e:
        st.warning(f"Compliance check unavailable: {e}")

    st.divider()

    # ── 3. SEBI exposure map ──
    st.markdown("**SEBI disclaimer exposure map**")
    try:
        sebi_rows = []
        for path, search_str in _SEBI_PAGES:
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                present = search_str in content
            except FileNotFoundError:
                present = None  # file absent
            sebi_rows.append({
                "Page":     path,
                "Status":   "PRESENT" if present else ("FILE MISSING" if present is None else "ABSENT"),
            })
        import pandas as pd
        df_sebi = pd.DataFrame(sebi_rows)
        st.dataframe(df_sebi, use_container_width=True, hide_index=True)
        absent = [r for r in sebi_rows if r["Status"] != "PRESENT"]
        if absent:
            st.error(f"{len(absent)} page(s) missing SEBI disclaimer: {', '.join(r['Page'] for r in absent)}")
        else:
            st.success("SEBI disclaimer confirmed in all monitored pages.")
    except Exception as e:
        st.warning(f"SEBI exposure map unavailable: {e}")

    st.divider()

    # ── 4. Loophole frequency ──
    st.markdown("**Governance loophole classes** (GSI_LOOPHOLE_LOG.md)")
    try:
        loopholes = _parse_loophole_log()
        if loopholes:
            for lp in loopholes:
                st.markdown(
                    f"**{lp['class_name']}**  \n"
                    f"Trigger: {lp['trigger']}  \n"
                    f"Gate: `{lp['gate']}`"
                )
        else:
            st.caption("No loophole log data found.")
    except Exception as e:
        st.warning(f"Loophole log unavailable: {e}")


# ── Public entry point ─────────────────────────────────────────────────────────

def render_observability() -> None:
    """
    Founder-only observability page.
    Gated by st.secrets['DEV_TOKEN'] PIN entry.
    Not imported by app.py — accessed via Streamlit MPA direct URL.
    """
    st.title("App internals")
    st.caption(f"v{CURRENT_VERSION}")

    if not st.session_state.get("obs_unlocked"):
        _render_gate()
        return

    tab_health, tab_program, tab_sprint, tab_risk = st.tabs(
        ["App Health", "Program", "Sprint Monitor", "Risk & Compliance"]
    )

    with tab_health:
        _tab_app_health()

    with tab_program:
        _tab_program()

    with tab_sprint:
        _render_sprint_monitor_tab()

    with tab_risk:
        _render_risk_compliance_tab()


# Streamlit MPA: execute when this file is served directly via /observability
render_observability()

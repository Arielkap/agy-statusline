#!/usr/bin/env python3
"""
Antigravity CLI (agy) Custom Statusline
Renders real-time context token usage and rolling/weekly quotas for:
- Gemini (5h + weekly)
- Gemini 4 Argon (weekly WTU quota)
- Claude / 3P (5h + weekly)
"""

import sys
import json


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return str(n)


def fmt_time(sec: int) -> str:
    if sec <= 0:
        return "-"
    m = sec // 60
    if m < 60:
        return f"{m}m"
    h = m // 60
    rem_m = m % 60
    if h < 24:
        return f"{h}h{rem_m}m" if rem_m > 0 else f"{h}h"
    d = h // 24
    rem_h = h % 24
    return f"{d}d{rem_h}h" if rem_h > 0 else f"{d}d"


def color_pct(pct: float) -> str:
    # Color based on remaining percentage (green -> yellow -> red)
    if pct >= 50.0:
        color = "\033[32m"  # Green
    elif pct >= 20.0:
        color = "\033[33m"  # Yellow
    else:
        color = "\033[31m"  # Red
    return f"{color}{pct:.0f}%\033[0m"


def main():
    try:
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            print("🪙 Tokens: -- │ 5h: -- │ Wk: --")
            return
        data = json.loads(raw_input)
    except Exception:
        print("🪙 Tokens: -- │ 5h: -- │ Wk: --")
        return

    # ANSI Codes
    dim = "\033[90m"
    rst = "\033[0m"
    bold = "\033[1m"
    cyan = "\033[36m"
    sep = f" {dim}│{rst} "

    # Terminal width
    term_width = data.get("terminal_width", 120)

    # 1. Context Tokens
    cw = data.get("context_window") or {}
    tot_in = cw.get("total_input_tokens", 0)
    tot_out = cw.get("total_output_tokens", 0)
    tot_tokens = tot_in + tot_out
    max_tokens = cw.get("context_window_size", 1048576)
    used_pct = cw.get("used_percentage")
    if used_pct is None:
        used_pct = (tot_tokens / max_tokens * 100) if max_tokens else 0.0

    tok_str = f"{cyan}🪙 Tokens: {fmt_tokens(tot_tokens)}/{fmt_tokens(max_tokens)}{rst} {dim}({used_pct:.1f}% used){rst}"

    # 2. Active Model Identification
    model_info = data.get("model") or {}
    model_name = str(model_info.get("id") or model_info.get("display_name") or "").lower()

    is_argon_active = "argon" in model_name
    is_claude_active = any(x in model_name for x in ["claude", "sonnet", "opus", "haiku", "3p"])
    is_gemini_active = not is_argon_active and not is_claude_active

    # 3. Quotas Extraction
    quota = data.get("quota") or {}

    # Gemini Standard
    g_5h = quota.get("gemini-5h") or {}
    g_wk = quota.get("gemini-weekly") or {}

    # Argon 4 (WTU weekly)
    a_5h = quota.get("gemini-argon-5h") or quota.get("argon-5h") or {}
    a_wk = (
        quota.get("gemini-argon-wtu-weekly")
        or quota.get("gemini-argon-weekly")
        or quota.get("argon-weekly")
        or {}
    )

    # Claude / 3P
    p_5h = quota.get("3p-5h") or {}
    p_wk = quota.get("3p-weekly") or {}

    # Fallback search if keys differ
    if not g_5h or not g_wk or not a_wk or not p_5h or not p_wk:
        for k, v in quota.items():
            kl = k.lower()
            if "argon" in kl:
                if "5h" in kl and not a_5h:
                    a_5h = v
                elif not a_wk:
                    a_wk = v
            elif "gemini" in kl:
                if "5h" in kl and not g_5h:
                    g_5h = v
                elif "week" in kl and not g_wk:
                    g_wk = v
            elif any(x in kl for x in ["3p", "claude", "sonnet"]):
                if "5h" in kl and not p_5h:
                    p_5h = v
                elif "week" in kl and not p_wk:
                    p_wk = v

    def render_bucket(name: str, b_5h: dict, b_wk: dict, is_active: bool, compact: bool = False) -> str:
        label = f"\033[1;34m★ {name}{rst}" if is_active else f"{bold}{name}{rst}"
        parts = []

        if b_5h and b_5h.get("remaining_fraction") is not None:
            p5 = b_5h["remaining_fraction"] * 100
            t5 = fmt_time(b_5h.get("reset_in_seconds", 0))
            if compact:
                parts.append(f"5h: {color_pct(p5)}")
            else:
                parts.append(f"5h: {color_pct(p5)} {dim}({t5}){rst}")

        if b_wk and b_wk.get("remaining_fraction") is not None:
            pw = b_wk["remaining_fraction"] * 100
            tw = fmt_time(b_wk.get("reset_in_seconds", 0))
            if compact:
                parts.append(f"Wk: {color_pct(pw)}")
            else:
                parts.append(f"Wk: {color_pct(pw)} {dim}({tw}){rst}")

        if not parts:
            return f"{label} --"
        return f"{label} " + " • ".join(parts)

    gemini_part = render_bucket("Gemini", g_5h, g_wk, is_gemini_active)
    argon_part = render_bucket("Argon 4", a_5h, a_wk, is_argon_active)
    claude_part = render_bucket("Claude", p_5h, p_wk, is_claude_active)

    # Adaptive rendering based on terminal width
    if term_width >= 130:
        # Full view: Tokens | Gemini | Argon 4 | Claude
        output = f"{tok_str}{sep}{gemini_part}{sep}{argon_part}{sep}{claude_part}"
    elif term_width >= 90:
        # Medium view: compact numbers
        tok_compact = f"{cyan}🪙 {fmt_tokens(tot_tokens)}/{fmt_tokens(max_tokens)}{rst} {dim}({used_pct:.0f}%){rst}"
        gemini_c = render_bucket("Gemini", g_5h, g_wk, is_gemini_active, compact=True)
        argon_c = render_bucket("Argon 4", a_5h, a_wk, is_argon_active, compact=True)
        claude_c = render_bucket("Claude", p_5h, p_wk, is_claude_active, compact=True)
        output = f"{tok_compact}{sep}{gemini_c}{sep}{argon_c}{sep}{claude_c}"
    else:
        # Small view: tokens + active model + Argon warning if empty
        tok_compact = f"{cyan}🪙 {fmt_tokens(tot_tokens)}{rst}"
        active_part = (
            argon_part if is_argon_active else (claude_part if is_claude_active else gemini_part)
        )
        if not is_argon_active and a_wk.get("remaining_fraction") == 0:
            output = f"{tok_compact}{sep}{active_part}{sep}\033[31mArgon: 0%\033[0m"
        else:
            output = f"{tok_compact}{sep}{active_part}"

    print(output)


if __name__ == "__main__":
    main()

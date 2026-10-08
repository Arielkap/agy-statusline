#!/usr/bin/env python3
"""
Antigravity CLI (agy) Custom Statusline
Renders real-time context token usage, 5h rolling quota, and weekly quota.
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
            print("🪙 Tokeny: -- │ 5h: -- │ Tydz: --")
            return
        data = json.loads(raw_input)
    except Exception:
        print("🪙 Tokeny: -- │ 5h: -- │ Tydz: --")
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

    tok_str = f"{cyan}🪙 Tokeny: {fmt_tokens(tot_tokens)}/{fmt_tokens(max_tokens)}{rst} {dim}({used_pct:.1f}% zajęte){rst}"

    # 2. Quotas
    quota = data.get("quota") or {}
    
    # Identify active model
    model_info = data.get("model") or {}
    model_name = str(model_info.get("id") or model_info.get("display_name") or "").lower()
    is_claude_active = any(x in model_name for x in ["claude", "sonnet", "opus", "haiku", "3p"])

    # Extract Gemini buckets
    g_5h = quota.get("gemini-5h") or {}
    g_wk = quota.get("gemini-weekly") or {}

    # Extract 3P / Claude buckets
    p_5h = quota.get("3p-5h") or {}
    p_wk = quota.get("3p-weekly") or {}

    # Fallback to search if key names vary
    if not g_5h or not g_wk or not p_5h or not p_wk:
        for k, v in quota.items():
            kl = k.lower()
            if "gemini" in kl:
                if "5h" in kl and not g_5h:
                    g_5h = v
                elif "week" in kl and not g_wk:
                    g_wk = v
            elif any(x in kl for x in ["3p", "claude", "sonnet"]):
                if "5h" in kl and not p_5h:
                    p_5h = v
                elif "week" in kl and not p_wk:
                    p_wk = v

    def bucket_str(name: str, bucket_5h: dict, bucket_wk: dict, is_active: bool) -> str:
        f_5h = bucket_5h.get("remaining_fraction")
        pct_5h = (f_5h * 100) if f_5h is not None else 100.0
        t_5h = fmt_time(bucket_5h.get("reset_in_seconds", 0))

        f_wk = bucket_wk.get("remaining_fraction")
        pct_wk = (f_wk * 100) if f_wk is not None else 100.0
        t_wk = fmt_time(bucket_wk.get("reset_in_seconds", 0))

        label = f"{bold}{name}{rst}" if not is_active else f"\033[1;34m★ {name}{rst}"
        return f"{label} 5h: {color_pct(pct_5h)} {dim}({t_5h}){rst} • Tydz: {color_pct(pct_wk)} {dim}({t_wk}){rst}"

    gemini_part = bucket_str("Gemini", g_5h, g_wk, not is_claude_active)
    claude_part = bucket_str("Claude", p_5h, p_wk, is_claude_active)

    # Adaptive output based on terminal width
    if term_width >= 115:
        # Full view: Tokens | Gemini 5h & Week | Claude 5h & Week
        output = f"{tok_str}{sep}{gemini_part}{sep}{claude_part}"
    elif term_width >= 75:
        # Compact dual view
        tok_compact = f"{cyan}🪙 {fmt_tokens(tot_tokens)}/{fmt_tokens(max_tokens)}{rst} {dim}({used_pct:.0f}%){rst}"
        active_part = claude_part if is_claude_active else gemini_part
        other_part = gemini_part if is_claude_active else claude_part
        output = f"{tok_compact}{sep}{active_part}{sep}{other_part}"
    else:
        # Ultra-compact for small windows: show active model limits only
        tok_compact = f"{cyan}🪙 {fmt_tokens(tot_tokens)}{rst}"
        active_part = claude_part if is_claude_active else gemini_part
        output = f"{tok_compact}{sep}{active_part}"

    print(output)

if __name__ == "__main__":
    main()

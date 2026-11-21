#!/usr/bin/env python3
"""
Antigravity CLI (agy) Custom Statusline  -  7 themes: neon | ember | matrix | beskar | arctic | sunset | luna
Renders context tokens + 5h / weekly quotas (with progress bars) for:
- Gemini pool (Neon / Hydrogen / Flash)
- Gemini 4 Argon (weekly WTU)
- Claude / 3P

Theme selection (first match wins):
  1. argv[1]                           e.g.  agy_statusline.py ember
  2. env  AGY_STATUSLINE_THEME
  3. file ~/.agy_statusline_theme      (one word)
  4. default: neon
"""

import json
import os
import sys

RST = "\033[0m"
BOLD = "\033[1m"


def c(n: int) -> str:
    return f"\033[38;5;{n}m"


THEMES = {
    # Cyberpunk: cyan / magenta / violet
    "neon": {
        "tok": c(51), "dim": c(60), "sep": "▕", "frame": c(99),
        "bar": ("▰", "▱"), "star": "◆", "tok_icon": "◈",
        "ok": c(51), "mid": c(213), "low": c(197),
        "label": c(147), "active": c(219),
        "icons": {"Neon": "⚡", "Hydrogen": "💠", "Gemini": "✧", "Argon 4": "☄", "Claude": "❖"},
    },
    # Forge: orange / red / gold
    "ember": {
        "tok": c(214), "dim": c(95), "sep": "┃", "frame": c(166),
        "bar": ("█", "░"), "star": "★", "tok_icon": "🔥",
        "ok": c(220), "mid": c(208), "low": c(196),
        "label": c(180), "active": c(202),
        "icons": {"Neon": "🌋", "Hydrogen": "💧", "Gemini": "🔸", "Argon 4": "⚔️ ", "Claude": "🛡️ "},
    },
    # Terminal hacker: greens
    "matrix": {
        "tok": c(46), "dim": c(22), "sep": "│", "frame": c(34),
        "bar": ("▓", "░"), "star": "▶", "tok_icon": "▣",
        "ok": c(46), "mid": c(148), "low": c(160),
        "label": c(71), "active": c(118),
        "icons": {"Neon": "λ", "Hydrogen": "∆", "Gemini": "∑", "Argon 4": "Ω", "Claude": "Ψ"},
    },
    # Mandalorian: beskar steel + gold
    "beskar": {
        "tok": c(250), "dim": c(240), "sep": "┫", "frame": c(244),
        "bar": ("■", "□"), "star": "✪", "tok_icon": "⛨",
        "ok": c(220), "mid": c(172), "low": c(160),
        "label": c(252), "active": c(226),
        "icons": {"Neon": "⚔", "Hydrogen": "⛏", "Gemini": "⚙", "Argon 4": "☠", "Claude": "⚜"},
    },
    # Arctic: ice blue / white / teal
    "arctic": {
        "tok": c(123), "dim": c(67), "sep": "╎", "frame": c(75),
        "bar": ("▮", "▯"), "star": "❄", "tok_icon": "❅",
        "ok": c(159), "mid": c(111), "low": c(204),
        "label": c(153), "active": c(231),
        "icons": {"Neon": "✺", "Hydrogen": "❆", "Gemini": "✦", "Argon 4": "◇", "Claude": "✱"},
    },
    # Sunset synthwave: hot pink / orange / purple
    "sunset": {
        "tok": c(213), "dim": c(96), "sep": "╱", "frame": c(171),
        "bar": ("●", "○"), "star": "☀", "tok_icon": "✿",
        "ok": c(215), "mid": c(205), "low": c(124),
        "label": c(183), "active": c(209),
        "icons": {"Neon": "🌅", "Hydrogen": "🌴", "Gemini": "🌙", "Argon 4": "🔮", "Claude": "🦋"},
    },
    # Luna: deep purple / violet / lavender
    "luna": {
        "tok": c(141), "dim": c(54), "sep": "┊", "frame": c(93),
        "bar": ("◆", "◇"), "star": "☾", "tok_icon": "🌙",
        "ok": c(177), "mid": c(135), "low": c(197),
        "label": c(183), "active": c(207),
        "icons": {"Neon": "🔮", "Hydrogen": "✧", "Gemini": "☽", "Argon 4": "✦", "Claude": "❋"},
    },
}


def pick_theme() -> dict:
    name = ""
    if len(sys.argv) > 1:
        name = sys.argv[1]
    if not name:
        name = os.environ.get("AGY_STATUSLINE_THEME", "")
    if not name:
        try:
            with open(os.path.expanduser("~/.agy_statusline_theme")) as f:
                name = f.read().strip()
        except OSError:
            pass
    return THEMES.get(name.lower(), THEMES["neon"])


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


def main():
    th = pick_theme()
    dim, frame = th["dim"], th["frame"]

    def pct_color(pct: float) -> str:
        return th["ok"] if pct >= 50 else (th["mid"] if pct >= 20 else th["low"])

    def bar(pct: float, width: int = 6) -> str:
        full, empty = th["bar"]
        filled = max(0, min(width, round(pct / 100 * width)))
        col = pct_color(pct)
        return f"{col}{full * filled}{dim}{empty * (width - filled)}{RST}"

    try:
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            print(f"{th['tok']}{th['tok_icon']} Tokens: -- {dim}{th['sep']}{RST} 5h: -- {dim}{th['sep']}{RST} Wk: --{RST}")
            return
        data = json.loads(raw_input)
    except Exception:
        print(f"{th['tok']}{th['tok_icon']} Tokens: -- {dim}{th['sep']}{RST} 5h: -- {dim}{th['sep']}{RST} Wk: --{RST}")
        return

    sep = f" {frame}{th['sep']}{RST} "
    term_width = data.get("terminal_width", 120)

    # 1. Context tokens
    cw = data.get("context_window") or {}
    tot_tokens = cw.get("total_input_tokens", 0) + cw.get("total_output_tokens", 0)
    max_tokens = cw.get("context_window_size", 1048576)
    used_pct = cw.get("used_percentage")
    if used_pct is None:
        used_pct = (tot_tokens / max_tokens * 100) if max_tokens else 0.0
    ctx_left = 100 - used_pct

    tok_str = (
        f"{th['tok']}{BOLD}{th['tok_icon']} {fmt_tokens(tot_tokens)}/{fmt_tokens(max_tokens)}{RST} "
        f"{bar(ctx_left, 8)} {dim}{used_pct:.1f}% used{RST}"
    )

    # 2. Active model
    model_info = data.get("model") or {}
    model_name = " ".join(str(model_info.get(k) or "") for k in ("id", "display_name")).lower()

    is_orch = "orchestrator" in model_name
    is_neon = "neon" in model_name
    is_argon = "argon" in model_name or "g1-pro" in model_name
    is_claude = any(x in model_name for x in ["claude", "sonnet", "opus", "haiku", "3p", "gpt"])
    is_flash = "flash" in model_name
    is_hydrogen = "hydrogen" in model_name or (is_orch and not is_neon)
    is_gemini_active = (not is_argon and not is_claude) or is_orch

    if is_neon:
        gemini_label = "Neon"
    elif is_hydrogen:
        gemini_label = "Hydrogen"
    else:
        gemini_label = "Gemini"

    # 3. Quotas
    quota = data.get("quota") or {}
    g_5h = quota.get("gemini-5h") or {}
    g_wk = quota.get("gemini-weekly") or {}
    a_5h = quota.get("gemini-argon-5h") or quota.get("argon-5h") or {}
    a_wk = (
        quota.get("gemini-argon-wtu-weekly")
        or quota.get("gemini-argon-weekly")
        or quota.get("argon-weekly")
        or {}
    )
    p_5h = quota.get("3p-5h") or {}
    p_wk = quota.get("3p-weekly") or {}

    if not g_5h or not g_wk or not a_wk or not p_5h or not p_wk:
        for k, v in quota.items():
            kl = k.lower()
            if "argon" in kl:
                if "5h" in kl and not a_5h:
                    a_5h = v
                elif not a_wk:
                    a_wk = v
            elif any(x in kl for x in ["gemini", "hydrogen", "neon"]):
                if "5h" in kl and not g_5h:
                    g_5h = v
                elif "week" in kl and not g_wk:
                    g_wk = v
            elif any(x in kl for x in ["3p", "claude", "sonnet"]):
                if "5h" in kl and not p_5h:
                    p_5h = v
                elif "week" in kl and not p_wk:
                    p_wk = v

    def render_bucket(name: str, b_5h: dict, b_wk: dict, active: bool, compact: bool = False) -> str:
        icon = th["icons"].get(name, "•")
        if active:
            label = f"{th['active']}{BOLD}{th['star']} {icon} {name}{RST}"
        else:
            label = f"{th['label']}{icon} {name}{RST}"
        parts = []
        for tag, b in (("5h", b_5h), ("Wk", b_wk)):
            if b and b.get("remaining_fraction") is not None:
                p = b["remaining_fraction"] * 100
                col = pct_color(p)
                txt = f"{dim}{tag}{RST} {bar(p, 4 if compact else 6)} {col}{p:.0f}%{RST}"
                if not compact:
                    txt += f" {dim}({fmt_time(b.get('reset_in_seconds', 0))}){RST}"
                parts.append(txt)
        if not parts:
            return f"{label} {dim}--{RST}"
        return f"{label} " + f" {dim}•{RST} ".join(parts)

    def buckets(compact: bool):
        return (
            render_bucket(gemini_label, g_5h, g_wk, is_gemini_active, compact),
            render_bucket("Argon 4", a_5h, a_wk, is_argon, compact),
            render_bucket("Claude", p_5h, p_wk, is_claude, compact),
        )

    if term_width >= 130:
        g, a, cl = buckets(False)
        output = f"{tok_str}{sep}{g}{sep}{a}{sep}{cl}"
    elif term_width >= 90:
        tok_c = f"{th['tok']}{th['tok_icon']} {fmt_tokens(tot_tokens)}/{fmt_tokens(max_tokens)}{RST} {dim}({used_pct:.0f}%){RST}"
        g, a, cl = buckets(True)
        output = f"{tok_c}{sep}{g}{sep}{a}{sep}{cl}"
    else:
        tok_c = f"{th['tok']}{th['tok_icon']} {fmt_tokens(tot_tokens)}{RST}"
        g, a, cl = buckets(True)
        active_part = a if is_argon else (cl if is_claude else g)
        if not is_argon and a_wk.get("remaining_fraction") == 0:
            output = f"{tok_c}{sep}{active_part}{sep}{th['low']}Argon: 0%{RST}"
        else:
            output = f"{tok_c}{sep}{active_part}"

    print(output)


if __name__ == "__main__":
    main()

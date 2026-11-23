#!/usr/bin/env python3
"""
Antigravity CLI (agy) Custom Statusline  -  7 themes: neon | ember | matrix | beskar | arctic | sunset | luna
Renders context tokens + 5h / weekly quotas (with progress bars) for:
- Unified GEMINI MODELS pool (Gemini 4 Neon, Gemini 4 Argon, Gemini 4 Hydrogen,
  Orchestrator (Neon), Orchestrator (Argon), Gemini 3.8 Flash)
- Claude / 3P pool

Theme selection (first match wins):
  1. argv[1]                           e.g.  agy_statusline.py ember
  2. env  AGY_STATUSLINE_THEME
  3. file ~/.agy_statusline_theme      (one word)
  4. default: neon
"""

import json
import os
import re
import shutil
import sys
import unicodedata

if sys.platform == "win32":
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

RST = "\033[0m"
BOLD = "\033[1m"
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _char_width(ch: str, next_ch: str = "") -> int:
    if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    if next_ch == "\ufe0f":
        return 2
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def visible_width(s: str) -> int:
    plain = _ANSI_RE.sub("", s)
    total = 0
    n = len(plain)
    for i, ch in enumerate(plain):
        nxt = plain[i + 1] if i + 1 < n else ""
        total += _char_width(ch, nxt)
    return total


def truncate_ansi(s: str, max_width: int) -> str:
    if max_width <= 0:
        return ""
    if visible_width(s) <= max_width:
        return s
    limit = max(1, max_width - 1)
    out = []
    width = 0
    i = 0
    n = len(s)
    while i < n:
        m = _ANSI_RE.match(s, i)
        if m:
            out.append(m.group(0))
            i = m.end()
            continue
        ch = s[i]
        nxt = s[i + 1] if i + 1 < n else ""
        w = _char_width(ch, nxt)
        if width + w > limit:
            break
        out.append(ch)
        width += w
        i += 1
        if nxt == "\ufe0f":
            out.append(nxt)
            i += 1
    return "".join(out) + f"{RST}…"


def detect_width(data: dict) -> int:
    tw = data.get("terminal_width")
    if isinstance(tw, (int, float)) and tw > 0:
        return int(tw)
    env_cols = os.environ.get("COLUMNS", "")
    if env_cols.isdigit() and int(env_cols) > 0:
        return int(env_cols)
    cols = shutil.get_terminal_size(fallback=(0, 0)).columns
    if cols > 0:
        return cols
    try:
        fd = os.open("/dev/tty", os.O_RDONLY)
        try:
            cols = os.get_terminal_size(fd).columns
            if cols > 0:
                return cols
        finally:
            os.close(fd)
    except OSError:
        pass
    return 80


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
            with open(os.path.expanduser("~/.agy_statusline_theme"), encoding="utf-8") as f:
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
    term_width = detect_width(data)
    budget = max(20, term_width - 2)

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

    # 2. Active model (Unified GEMINI MODELS pool: Neon, Argon, Hydrogen,
    #    Orchestrator (Neon), Orchestrator (Argon), Gemini 3.8 Flash)
    model_info = data.get("model") or {}
    model_name = " ".join(str(model_info.get(k) or "") for k in ("id", "display_name")).lower()

    is_orch = "orchestrator" in model_name
    is_neon = "neon" in model_name
    is_argon = "argon" in model_name or "g1-pro" in model_name
    is_claude = any(x in model_name for x in ["claude", "sonnet", "opus", "haiku", "3p", "gpt"])
    is_flash = "flash" in model_name
    is_hydrogen = "hydrogen" in model_name
    is_gemini_active = not is_claude

    if is_orch and is_argon:
        gemini_label, gemini_icon_key = "Orch Argon", "Argon 4"
    elif is_orch and is_neon:
        gemini_label, gemini_icon_key = "Orch Neon", "Neon"
    elif is_orch:
        gemini_label, gemini_icon_key = "Orchestrator", "Gemini"
    elif is_argon:
        gemini_label, gemini_icon_key = "Argon 4", "Argon 4"
    elif is_neon:
        gemini_label, gemini_icon_key = "Neon", "Neon"
    elif is_hydrogen:
        gemini_label, gemini_icon_key = "Hydrogen", "Hydrogen"
    elif is_flash:
        gemini_label, gemini_icon_key = "Flash", "Gemini"
    else:
        gemini_label, gemini_icon_key = "Gemini", "Gemini"

    # 3. Quotas (Unified GEMINI MODELS pool + Claude/3P pool)
    quota = data.get("quota") or {}
    g_5h = quota.get("gemini-5h") or quota.get("gemini-argon-5h") or quota.get("argon-5h") or {}
    g_wk = (
        quota.get("gemini-weekly")
        or quota.get("gemini-argon-weekly")
        or quota.get("gemini-argon-wtu-weekly")
        or quota.get("argon-weekly")
        or {}
    )
    p_5h = quota.get("3p-5h") or {}
    p_wk = quota.get("3p-weekly") or {}

    if not g_5h or not g_wk or not p_5h or not p_wk:
        for k, v in quota.items():
            if not isinstance(v, dict):
                continue
            kl = k.lower()
            if any(x in kl for x in ["gemini", "hydrogen", "neon", "argon", "flash", "orchestrator"]):
                if "5h" in kl and not g_5h:
                    g_5h = v
                elif "week" in kl and not g_wk:
                    g_wk = v
            elif any(x in kl for x in ["3p", "claude", "sonnet", "opus", "gpt"]):
                if "5h" in kl and not p_5h:
                    p_5h = v
                elif "week" in kl and not p_wk:
                    p_wk = v

    def render_bucket(
        name: str,
        b_5h: dict,
        b_wk: dict,
        active: bool,
        bar_width: int = 6,
        show_timers: bool = True,
        icon_key: str = "",
    ) -> str:
        icon = th["icons"].get(icon_key or name, "•")
        if active:
            label = f"{th['active']}{BOLD}{th['star']} {icon} {name}{RST}"
        else:
            label = f"{th['label']}{icon} {name}{RST}"
        parts = []
        for tag, b in (("5h", b_5h), ("Wk", b_wk)):
            if b and b.get("remaining_fraction") is not None:
                p = b["remaining_fraction"] * 100
                col = pct_color(p)
                if bar_width > 0:
                    txt = f"{dim}{tag}{RST} {bar(p, bar_width)} {col}{p:.0f}%{RST}"
                else:
                    txt = f"{dim}{tag}{RST} {col}{p:.0f}%{RST}"
                if show_timers:
                    t_str = fmt_time(b.get("reset_in_seconds") or 0)
                    if t_str != "-":
                        txt += f" {dim}({t_str}){RST}"
                parts.append(txt)
        if not parts:
            return f"{label} {dim}--{RST}"
        return f"{label} " + f" {dim}•{RST} ".join(parts)

    def buckets(bar_width: int, show_timers: bool):
        return (
            render_bucket(gemini_label, g_5h, g_wk, is_gemini_active, bar_width, show_timers, gemini_icon_key),
            render_bucket("Claude", p_5h, p_wk, is_claude, bar_width, show_timers, "Claude"),
        )

    tok_med = f"{th['tok']}{th['tok_icon']} {fmt_tokens(tot_tokens)}/{fmt_tokens(max_tokens)}{RST} {dim}({used_pct:.0f}%){RST}"
    tok_short = f"{th['tok']}{th['tok_icon']} {fmt_tokens(tot_tokens)}{RST}"

    def active_only(bar_width: int) -> str:
        g, cl = buckets(bar_width, False)
        active_part = cl if is_claude else g
        return f"{tok_short}{sep}{active_part}"

    # Pick the richest layout whose actual rendered width fits inside the terminal
    candidates = (
        lambda: sep.join((tok_str, *buckets(6, True))),   # Full: token bar + 6-char bars + timers
        lambda: sep.join((tok_med, *buckets(4, True))),   # Medium-full: compact tokens + 4-char bars + timers
        lambda: sep.join((tok_med, *buckets(4, False))),  # Compact: all buckets + 4-char bars, no timers
        lambda: sep.join((tok_med, *buckets(0, False))),  # Tight: all buckets, percentages only
        lambda: active_only(4),                           # Narrow: active model + 4-char bars
        lambda: active_only(0),                           # Ultra-narrow: active model, percentages only
    )

    output = ""
    for build in candidates:
        candidate = build()
        output = candidate
        if visible_width(candidate) <= budget:
            break
    else:
        output = truncate_ansi(output, budget)

    print(output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
agy-theme - switch the agy statusline theme on the fly (cross-platform).
  agy-theme            -> next theme (cycle)
  agy-theme prev       -> previous theme
  agy-theme ember      -> set a specific theme
  agy-theme list       -> show themes (current marked with *)
"""

import os
import sys

THEMES = ["neon", "ember", "matrix", "beskar", "arctic", "sunset", "luna"]
THEME_FILE = os.path.expanduser("~/.agy_statusline_theme")


def read_current() -> str:
    try:
        with open(THEME_FILE, encoding="utf-8") as f:
            val = f.read().strip().lower()
            if val in THEMES:
                return val
    except OSError:
        pass
    return "neon"


def main() -> int:
    cur = read_current()
    idx = THEMES.index(cur) if cur in THEMES else 0
    arg = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "next"

    if arg == "next":
        new = THEMES[(idx + 1) % len(THEMES)]
    elif arg == "prev":
        new = THEMES[(idx - 1) % len(THEMES)]
    elif arg == "list":
        for t in THEMES:
            prefix = "* " if t == cur else "  "
            print(f"{prefix}{t}")
        return 0
    elif arg in THEMES:
        new = arg
    else:
        print(f"Unknown theme '{arg}'. Available: {' '.join(THEMES)}", file=sys.stderr)
        return 1

    with open(THEME_FILE, "w", encoding="utf-8") as f:
        f.write(f"{new}\n")

    print(f"Statusline theme: {new}  (applies on next agy redraw, i.e. your next message)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# AGY Statusline 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)]()
[![Platform: Antigravity CLI](https://img.shields.io/badge/Tool-Antigravity%20CLI%20(agy)-purple.svg)]()

A lightweight, **zero-dependency** statusline extension for Google's **Antigravity CLI (`agy`)**.  
Renders real-time session context token usage, 5-hour rolling quotas, and weekly quota limits (with progress bars) for **Gemini / Gemini 4 Neon / Gemini 4 Hydrogen**, **Gemini 4 Argon**, and **Claude / 3P** models directly in your terminal footer. Ships with **7 switchable themes**.

---

## 📸 Preview

```text
◈ 60k/524k ▰▰▰▰▰▰▰▱ 11.4% used ▕ ◆ ⚡ Neon 5h ▰▰▰▰▰▱ 82% (2h) • Wk ▰▰▱▱▱▱ 35% (6d) ▕ ☄ Argon 4 Wk ▰▰▰▰▰▰ 100% (5d18h) ▕ ❖ Claude 5h ▰▰▰▰▰▰ 100% (5h) • Wk ▰▱▱▱▱▱ 12% (3d)
```

## 🎨 Themes

| Theme | Palette | Icons / bars |
| :-- | :-- | :-- |
| `neon` (default) | cyan / magenta / violet | ⚡ 💠 ☄ ❖ `▰▱` |
| `ember` | orange / red / gold | 🌋 💧 ⚔️ 🛡️ `█░` |
| `matrix` | greens | λ ∆ Ω Ψ `▓░` |
| `beskar` | steel / gold | ⚔ ⛏ ☠ ⚜ `■□` |
| `arctic` | ice blue / white | ✺ ❆ ◇ ✱ `▮▯` |
| `sunset` | pink / orange / purple | 🌅 🌴 🔮 🦋 `●○` |
| `luna` | deep purple / lavender | 🔮 ✧ ✦ ❋ `◆◇` |

Switch on the fly (the choice is stored in `~/.agy_statusline_theme`, shared by all terminals):

```bash
th              # next theme (zsh alias installed by install.sh)
th prev | th list | th ember
```

Inside `agy`: type `/th` for a picker, or `/th <name>` (run `/skills reload` once after installing). Theme resolution order: `argv[1]`, env `AGY_STATUSLINE_THEME`, the theme file, then `neon`.

### Responsive Terminal Layouts
- **Wide Screens (≥ 130 columns):** Full layout — context window tokens + Gemini / Hydrogen quotas (5h / weekly) + Argon 4 quota (weekly WTU) + Claude/3P quotas (5h / weekly) with exact reset countdowns.
- **Medium Screens (90–129 columns):** Compact tokens badge + compact percentages for all active quota buckets without verbose timers.
- **Narrow Screens (< 90 columns):** Minimalist view focused solely on the currently active model (with automatic red warning if Argon 4 is depleted).

---

## ✨ Key Features

- 🪙 **Context Window Tokens:** Real-time token consumption (`input + output`) and percentage of available session window.
- ⚡ **Gemini 4 Argon WTU Tracking:** Monitors specialized weekly Work-Through-Units (`gemini-argon-wtu-weekly`) and highlights depleted limits (red `0%`) with reset time.
- ⏳ **5-Hour Rolling Quotas:** Remaining quota percentage and exact countdown to reset (`Xh Ym` / `Xm`).
- 📅 **Weekly Quota Tracking:** Long-term quota capacity and reset schedule (`Xd Yh`).
- 🌟 **Active Model Detection:** Automatically highlights the currently active model with a star (`★`) and dynamically labels the standard Gemini bucket as `Neon` (for **Gemini 4 Neon** and **Orchestrator (Neon)**), `Hydrogen` (for **Gemini 4 Hydrogen** and **Orchestrator (Argon)**, highlighting both `★ Hydrogen` and `★ Argon 4`), or `Gemini` (for Flash/other models).
- 🎨 **Adaptive ANSI Color Coding:**
  - 🟢 **≥ 50%** remaining — Safe (Green)
  - 🟡 **20% – 50%** — Warning (Yellow)
  - 🔴 **< 20%** — Depleted / Low (Red)
- ⚡ **Zero External Dependencies:** Built entirely with Python's standard library (`sys`, `json`). Executes in **< 15 ms**.

---

## 🛠️ Quick Installation

### Option 1: One-Line Auto Install

Clone the repository and run the automated installer:

```bash
git clone https://github.com/Arielkap/agy-statusline.git ~/.agy-statusline
cd ~/.agy-statusline
chmod +x install.sh
./install.sh
```

The installer will:
1. Symlink `agy_statusline.py` to `~/bin/agy_statusline.py` and `agy-theme` to `~/bin/agy-theme`.
2. Install the `/th` skill into `~/.gemini/skills/th` and add the `th` alias to `~/.zshrc`.
3. Automatically configure `~/.gemini/antigravity-cli/settings.json` with the necessary statusline hook and permissions.

---

### Option 2: Manual Setup

1. **Clone or copy the script:**
   ```bash
   git clone https://github.com/Arielkap/agy-statusline.git ~/.agy-statusline
   mkdir -p ~/bin
   ln -sf ~/.agy-statusline/agy_statusline.py ~/bin/agy_statusline.py
   chmod +x ~/bin/agy_statusline.py
   ```

2. **Add to Antigravity CLI configuration:**  
   Open `~/.gemini/antigravity-cli/settings.json` and add:

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "$HOME/bin/agy_statusline.py",
       "enabled": true,
       "stack_with_default": true
     }
   }
   ```

   > **Tip:** Setting `"stack_with_default": true` preserves Antigravity's built-in footer (git branch, keybindings) while stacking your live token/quota metrics right below it.

---

## 🧪 Testing

You can test the statusline anytime by piping mock telemetry JSON into stdin:

```bash
echo '{"terminal_width": 140, "model": {"id": "gemini-4-hydrogen-high", "display_name": "Gemini 4 Hydrogen (High)"}, "context_window": {"total_input_tokens": 125000, "total_output_tokens": 25000, "context_window_size": 1048576, "used_percentage": 14.3}, "quota": {"gemini-5h": {"remaining_fraction": 0.85, "reset_in_seconds": 3600}, "gemini-weekly": {"remaining_fraction": 0.95, "reset_in_seconds": 518400}, "gemini-argon-wtu-weekly": {"remaining_fraction": 1.0, "reset_in_seconds": 498000}, "3p-5h": {"remaining_fraction": 1.0, "reset_in_seconds": 18000}, "3p-weekly": {"remaining_fraction": 0.5, "reset_in_seconds": 259200}}}' | python3 agy_statusline.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

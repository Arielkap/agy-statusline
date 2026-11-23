# AGY Pulse ⚡

> *Real-time token & quota pulse for Google's Antigravity CLI (`agy`).*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)]()
[![Platform: Antigravity CLI](https://img.shields.io/badge/Tool-Antigravity%20CLI%20(agy)-purple.svg)]()

**AGY Pulse** (`agy-statusline`) is a lightweight, **zero-dependency** statusline extension for Google's **Antigravity CLI (`agy`)**.  
Renders real-time session context token usage, 5-hour rolling quotas, and weekly quota limits (with progress bars) for the unified **GEMINI MODELS** pool (**Gemini 4 Neon**, **Gemini 4 Argon**, **Gemini 4 Hydrogen**, **Orchestrator (Neon)**, **Orchestrator (Argon)**, **Gemini 3.8 Flash**) and **Claude / 3P** models directly in your terminal footer. Ships with **7 switchable themes**.

---

## 📸 Preview

```text
◈ 60k/1.0M ▰▰▰▰▰▰▰▱ 5.7% used ▕ ◆ ☄ Argon 4 5h ▰▰▰▰▰▰ 95% • Wk ▰▰▰▰▰▰ 98% (6d23h) ▕ ❖ Claude 5h ▰▰▰▰▰▰ 100% (5h) • Wk ▰▱▱▱▱▱ 12% (3d)
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

### Responsive Terminal Layouts (Auto-Fit)
AGY Pulse measures the actual rendered display width (stripping ANSI codes and accounting for wide Unicode/emoji glyphs) and automatically picks the richest layout that fits inside the terminal width:
- **Full:** Token progress bar + both quota pools (`GEMINI MODELS` + `Claude / 3P`) with 6-block bars and reset countdowns.
- **Medium-Full:** Compact token badge + both pools with 4-block bars and reset countdowns.
- **Compact:** Compact token badge + both pools with 4-block bars (no timers).
- **Tight:** Compact token badge + both pools as percentages (no bars).
- **Narrow / Ultra-Narrow:** Minimalist view focused on the active model pool, with ANSI-safe truncation as a final guard.

---

## ✨ Key Features

- 🪙 **Context Window Tokens:** Real-time token consumption (`input + output`) and percentage of available session window.
- 🌌 **Unified GEMINI MODELS Pool:** Tracks the shared 5-hour and weekly quota across all 6 models in the group (`Gemini 4 Neon`, `Gemini 4 Argon`, `Gemini 4 Hydrogen`, `Orchestrator (Neon)`, `Orchestrator (Argon)`, `Gemini 3.8 Flash`).
- ⏳ **5-Hour Rolling Quotas:** Remaining quota percentage and countdown to reset (`Xh Ym` / `Xm`) when active.
- 📅 **Weekly Quota Tracking:** Long-term 7-day quota capacity and reset schedule (`Xd Yh`).
- 🌟 **Active Model Detection:** Automatically highlights the currently active pool with a star (`★`) and dynamically adapts the Gemini pool label and icon to match your active model (`Neon`, `Argon 4`, `Hydrogen`, `Orch Neon`, `Orch Argon`, `Flash`, or `Gemini`).
- 🎨 **Adaptive ANSI Color Coding:**
  - 🟢 **≥ 50%** remaining — Safe (Green)
  - 🟡 **20% – 50%** — Warning (Yellow)
  - 🔴 **< 20%** — Depleted / Low (Red)
- ⚡ **Zero External Dependencies:** Built entirely with Python's standard library (`sys`, `json`). Executes in **< 15 ms**.

---

## 🛠️ Quick Installation

### macOS / Linux

#### Option 1: One-Line Auto Install

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

#### Option 2: Manual Setup

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

### Windows (PowerShell / Windows Terminal)

#### Option 1: One-Line Auto Install

Open **Windows Terminal (PowerShell)** and run:

```powershell
irm https://raw.githubusercontent.com/Arielkap/agy-statusline/main/install.ps1 | iex
```

Or clone first and run locally:

```powershell
git clone https://github.com/Arielkap/agy-statusline.git "$env:USERPROFILE\.agy-statusline"
cd "$env:USERPROFILE\.agy-statusline"
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

The installer will:
1. Verify Python 3.8+ and install `agy_statusline.py`, `agy_theme.py`, `agy-theme.cmd`, and `th.cmd` into `%USERPROFILE%\bin` (and add it to your User `PATH`).
2. Install the `/th` skill into `%USERPROFILE%\.gemini\skills\th`.
3. Configure `%USERPROFILE%\.gemini\antigravity-cli\settings.json` with `cmd /c`-safe quoting (handles spaces in Windows usernames) and UTF-8 encoding.

Open a **new** Windows Terminal tab, launch `agy`, run `/skills reload`, and try `/th` (or `th` / `th ember` in PowerShell or CMD).

#### Option 2: Manual Setup (Windows)

In `%USERPROFILE%\.gemini\antigravity-cli\settings.json` (ensure `%USERPROFILE%\bin` is in `PATH` and contains `agy_statusline.cmd` — this avoids space/quote issues in Windows usernames):

```json
{
  "statusLine": {
    "type": "command",
    "command": "agy_statusline.cmd",
    "enabled": true,
    "stack_with_default": true
  }
}
```

---

## 🧪 Testing

You can test the statusline anytime by piping mock telemetry JSON into stdin:

```bash
echo '{"terminal_width": 140, "model": {"id": "gemini-4-argon-medium", "display_name": "Gemini 4 Argon (Medium)"}, "context_window": {"total_input_tokens": 125000, "total_output_tokens": 25000, "context_window_size": 1048576, "used_percentage": 14.3}, "quota": {"gemini-5h": {"remaining_fraction": 0.9499, "reset_in_seconds": 0}, "gemini-weekly": {"remaining_fraction": 0.9825, "reset_in_seconds": 602580}, "3p-5h": {"remaining_fraction": 1.0, "reset_in_seconds": 18000}, "3p-weekly": {"remaining_fraction": 0.5, "reset_in_seconds": 259200}}}' | python3 agy_statusline.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

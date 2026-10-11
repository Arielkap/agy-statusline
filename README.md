# AGY Statusline 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange.svg)]()
[![Platform: Antigravity CLI](https://img.shields.io/badge/Tool-Antigravity%20CLI%20(agy)-purple.svg)]()

A lightweight, **zero-dependency** statusline extension for Google's **Antigravity CLI (`agy`)**.  
Renders real-time session context token usage, 5-hour rolling quotas, and weekly quota limits for both **Gemini** and **Claude / 3P** models directly in your terminal footer.

---

## 📸 Preview

```text
🪙 Tokens: 188k/1.0M (13.8% used) │ ★ Gemini 5h: 76% (14m) • Wk: 95% (6d1h) │ Claude 5h: 100% (4h28m) • Wk: 42% (4d20h)
```

### Responsive Terminal Layouts
- **Wide Screens (≥ 115 columns):** Full layout — context window tokens + Gemini quotas (5h / weekly) + Claude/3P quotas (5h / weekly) with reset countdowns.
- **Medium Screens (75–114 columns):** Compact tokens badge + active model quotas + secondary model summary.
- **Narrow Screens (< 75 columns):** Minimalist view focused solely on the currently active model.

---

## ✨ Key Features

- 🪙 **Context Window Tokens:** Real-time token consumption (`input + output`) and percentage of available session window.
- ⏳ **5-Hour Rolling Quotas:** Remaining quota percentage and exact countdown to reset (`Xh Ym` / `Xm`).
- 📅 **Weekly Quota Tracking:** Long-term quota capacity and reset schedule (`Xd Yh`).
- 🌟 **Active Model Detection:** Automatically highlights the currently active model with a star (`★`).
- 🎨 **Adaptive ANSI Color Coding:**
  - 🟢 **≥ 50%** remaining — Safe (Green)
  - 🟡 **20% – 50%** — Warning (Yellow)
  - 🔴 **< 20%** — Depleted / Low (Red)
- ⚡ **Zero External Dependencies:** Built entirely with Python's standard library (`sys`, `json`). Executes in **< 30 ms**.

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
1. Symlink `agy_statusline.py` to `~/bin/agy_statusline.py`.
2. Automatically configure `~/.gemini/antigravity-cli/settings.json` with the necessary statusline hook and permissions.

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
echo '{"terminal_width": 140, "model": {"display_name": "Gemini 3.8 Flash"}, "context_window": {"total_input_tokens": 125000, "total_output_tokens": 25000, "context_window_size": 1048576, "used_percentage": 14.3}, "quota": {"gemini-5h": {"remaining_fraction": 0.85, "reset_in_seconds": 3600}, "gemini-weekly": {"remaining_fraction": 0.95, "reset_in_seconds": 518400}, "3p-5h": {"remaining_fraction": 1.0, "reset_in_seconds": 18000}, "3p-weekly": {"remaining_fraction": 0.5, "reset_in_seconds": 259200}}}' | python3 agy_statusline.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/bin"
TARGET_LINK="${TARGET_DIR}/agy_statusline.py"
SETTINGS_FILE="${HOME}/.gemini/antigravity-cli/settings.json"

echo "==> Preparing bin directory: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"

echo "==> Symlinking statusline script: ${TARGET_LINK}"
chmod +x "${SCRIPT_DIR}/agy_statusline.py"
ln -sf "${SCRIPT_DIR}/agy_statusline.py" "${TARGET_LINK}"

echo "==> Symlinking theme switcher: ${TARGET_DIR}/agy-theme"
chmod +x "${SCRIPT_DIR}/agy-theme"
ln -sf "${SCRIPT_DIR}/agy-theme" "${TARGET_DIR}/agy-theme"

echo "==> Installing /th skill into ~/.gemini/skills/th"
mkdir -p "${HOME}/.gemini/skills/th"
cp "${SCRIPT_DIR}/skills/th/SKILL.md" "${HOME}/.gemini/skills/th/SKILL.md"

ZSHRC="${HOME}/.zshrc"
if [ -f "${ZSHRC}" ] && ! grep -q "agy-theme" "${ZSHRC}"; then
    echo "==> Adding 'th' alias to ${ZSHRC}"
    printf '\n# agy statusline theme switcher (th = next, th prev, th ember, th list)\nalias th="$HOME/bin/agy-theme"\n' >> "${ZSHRC}"
fi

if [ -f "${SETTINGS_FILE}" ]; then
    echo "==> Updating settings.json in Antigravity CLI..."
    python3 -c "
import json
p = '${SETTINGS_FILE}'
with open(p, 'r') as f:
    cfg = json.load(f)

cfg['statusLine'] = {
    'type': 'command',
    'command': '${TARGET_LINK}',
    'enabled': True,
    'stack_with_default': True
}

allows = cfg.setdefault('permissions', {}).setdefault('allow', [])
cmd_rule = 'command(${TARGET_LINK})'
if cmd_rule not in allows:
    allows.append(cmd_rule)

with open(p, 'w') as f:
    json.dump(cfg, f, indent=2)
"
    echo "==> Configuration in ${SETTINGS_FILE} updated!"
else
    echo "==> Note: ${SETTINGS_FILE} not found. Please configure manually."
fi

echo "==> Installation complete! Launch 'agy', run /skills reload, and try /th (or 'th' in a new zsh tab)."

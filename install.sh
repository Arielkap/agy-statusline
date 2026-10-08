#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/bin"
TARGET_LINK="${TARGET_DIR}/agy_statusline.py"
SETTINGS_FILE="${HOME}/.gemini/antigravity-cli/settings.json"

echo "==> Przygotowywanie katalogu bin: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"

echo "==> Linkowanie skryptu statusline: ${TARGET_LINK}"
chmod +x "${SCRIPT_DIR}/agy_statusline.py"
ln -sf "${SCRIPT_DIR}/agy_statusline.py" "${TARGET_LINK}"

if [ -f "${SETTINGS_FILE}" ]; then
    echo "==> Aktualizacja settings.json w Antigravity CLI..."
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
    echo "==> Konfiguracja w ${SETTINGS_FILE} zaktualizowana!"
else
    echo "==> Uwaga: Nie znaleziono ${SETTINGS_FILE}. Skonfiguruj go ręcznie."
fi

echo "==> Instalacja zakończona pomyślnie! Uruchom 'agy' i ciesz się stopką limitów."

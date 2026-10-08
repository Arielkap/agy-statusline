# AGY Statusline 🚀

Lekki, zero-dependency skrypt statusline dla **Antigravity CLI (`agy`)**, wyświetlający w czasie rzeczywistym zużycie tokenów kontekstu oraz limity 5-godzinne i tygodniowe (Gemini i Claude / 3P).

---

## 📸 Podgląd (Preview)

```text
🪙 Tokeny: 188k/1.0M (13.8% zajęte) │ ★ Gemini 5h: 76% (14m) • Tydz: 95% (6d1h) │ Claude 5h: 100% (4h28m) • Tydz: 42% (4d20h)
```

- **Szeroki ekran (>= 115 kolumn)**: Pełny widok – tokeny kontekstu + limity Gemini (5h / tydzień) + limity Claude/3P (5h / tydzień) z odliczaniem do resetu.
- **Średni ekran (75–114 kolumn)**: Zwinięty licznik tokenów i podsumowanie limitów.
- **Wąski ekran (< 75 kolumn)**: Minimalistyczny widok skupiony na aktywnym modelu.

---

## ✨ Funkcje (Features)

- 🪙 **Tokeny kontekstu**: Dokładna liczba tokenów w oknie sesji (`in + out`) wraz z procentem zapełnienia.
- ⏳ **Limit 5-godzinny (5h Rolling Quota)**: Pozostały procent limitu oraz czas do resetu (`Xh Ym` / `Xm`).
- 📅 **Limit tygodniowy (Weekly Quota)**: Stan tygodniowego limitu wraz z czasem do odnowienia (`Xd Yh`).
- 🌟 **Wykrywanie aktywnego modelu**: Automatyczne oznaczanie bieżącego modelu gwiazdką (`★`).
- 🎨 **Kolorowanie ANSI**:
  - 🟢 `>= 50%` pozostałego limitu – zielony
  - 🟡 `20% – 50%` – żółty
  - 🔴 `< 20%` – czerwony
- ⚡ **Zero zależności**: Działa na czystym Pythonie 3 (`sys`, `json`). Błyskawiczny czas wykonania (~30 ms).

---

## 🛠️ Instalacja (Installation)

### 1. Klonowanie repozytorium lub pobranie skryptu
```bash
git clone https://github.com/Arielkap/agy-statusline.git ~/Agents/agy-statusline
mkdir -p ~/bin
ln -sf ~/Agents/agy-statusline/agy_statusline.py ~/bin/agy_statusline.py
chmod +x ~/Agents/agy-statusline/agy_statusline.py
```

### 2. Konfiguracja w Antigravity CLI
Dodaj konfigurację do pliku `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "/Users/ariello/bin/agy_statusline.py",
    "enabled": true,
    "stack_with_default": true
  }
}
```

> **Wskazówka**: Flaga `"stack_with_default": true` zachowuje wbudowaną stopkę Antigravity (skróty, gałąź git) i wyświetla linię tokenów/limitów pod nią.

---

## 🧪 Testowanie manualne

Możesz przetestować działanie skryptu przekazując przykładowy JSON na `stdin`:

```bash
echo '{"terminal_width": 140, "model": {"display_name": "Gemini 3.8 Flash"}, "context_window": {"total_input_tokens": 125000, "total_output_tokens": 25000, "context_window_size": 1048576, "used_percentage": 14.3}, "quota": {"gemini-5h": {"remaining_fraction": 0.85, "reset_in_seconds": 3600}, "gemini-weekly": {"remaining_fraction": 0.95, "reset_in_seconds": 518400}, "3p-5h": {"remaining_fraction": 1.0, "reset_in_seconds": 18000}, "3p-weekly": {"remaining_fraction": 0.5, "reset_in_seconds": 259200}}}' | ./agy_statusline.py
```

---

## 📄 Licencja

MIT License – zobacz plik [LICENSE](LICENSE).

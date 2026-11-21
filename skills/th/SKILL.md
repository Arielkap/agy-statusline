---
name: th
description: Switch the agy statusline theme on the fly. Usage - /th (opens a picker), /th next, /th prev, /th list, /th <neon|ember|matrix|beskar|arctic|sunset|luna>.
---

# Statusline theme switcher

Behaviour depends on the argument the user typed after `/th`.

## No argument -> show a picker

1. Run `~/bin/agy-theme list` to learn the current theme (marked with `*`).
2. Call the `ask_question` tool ONCE, single-select, with the question "Wybierz motyw statusline" and exactly these 7 options, in this order, with the current theme's option prefixed by `(aktualny) `:
   - `neon   ⚡ ◆ ▰▰▰▱  cyjan / magenta / fiolet`
   - `ember  🌋 ★ ███░  pomarańcz / czerwień / złoto`
   - `matrix λ ▶ ▓▓▓░  zielenie`
   - `beskar ⚔ ✪ ■■■□  stal / złoto (Mandalorian)`
   - `arctic ✺ ❄ ▮▮▮▯  lodowy błękit / biel`
   - `sunset 🌅 ☀ ●●●○  róż / pomarańcz / fiolet`
   - `luna   🔮 ☾ ◆◆◆◇  fiolet / lawenda`
3. Take the first word of the chosen option as the theme name and run `~/bin/agy-theme <name>`.
4. Reply with one short line confirming the theme.

## With an argument -> no picker

Run exactly one command, no analysis:

```bash
~/bin/agy-theme <argument>
```

(`next`, `prev`, `list`, or a theme name). Reply with one short line: the active theme (or the list for `list`). If the script reports an unknown theme, show the valid names it printed.

Always end with the usual status footer.

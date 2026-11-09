"""The Mini App "home" page, served by Vercel at /mini.

A single self-contained HTML page (no build step, no external assets except
Telegram's own script). Tiles are generated from config.SOCIAL_LINKS, so the
hub and the bottom keyboard always show the same apps.

Tapping a tile navigates the webview in place — that keeps the user inside
Telegram. Iframes are deliberately not used: TikTok, Instagram and friends
block framing.
"""

from __future__ import annotations

import json

import config


def _apps() -> list[dict]:
    return [
        {"emoji": emoji, "name": label, "url": url.strip()}
        for emoji, label, url in config.SOCIAL_LINKS
        if url and url.strip()
    ]


def render_html() -> str:
    apps_json = json.dumps(_apps(), ensure_ascii=False).replace("</", "<\\/")
    wa_number = str(getattr(config, "WHATSAPP_NUMBER", "") or "").strip()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>Social Hub</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  :root {{
    --bg: var(--tg-theme-bg-color, #ffffff);
    --card: var(--tg-theme-secondary-bg-color, #f2f2f7);
    --text: var(--tg-theme-text-color, #111111);
    --hint: var(--tg-theme-hint-color, #8a8a8e);
    --accent: var(--tg-theme-button-color, #2ea6ff);
    --accent-text: var(--tg-theme-button-text-color, #ffffff);
    --radius: 18px;
  }}
  * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    min-height: 100vh;
    padding: calc(14px + env(safe-area-inset-top)) 16px calc(24px + env(safe-area-inset-bottom));
    -webkit-user-select: none;
    user-select: none;
  }}
  header {{ position: sticky; top: calc(env(safe-area-inset-top)); z-index: 5; background: var(--bg); padding-bottom: 10px; }}
  h1 {{ font-size: 24px; margin: 6px 0 2px; letter-spacing: -0.02em; }}
  .sub {{ color: var(--hint); font-size: 13px; margin: 0 0 12px; }}
  .search {{ position: relative; }}
  .search input {{
    width: 100%; border: 0; outline: 0; border-radius: 14px;
    background: var(--card); color: var(--text);
    padding: 12px 14px; font-size: 15px; font-family: inherit;
  }}
  h2 {{ font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: var(--hint); margin: 18px 2px 10px; font-weight: 700; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
  @media (min-width: 430px) {{ .grid {{ grid-template-columns: repeat(4, 1fr); }} }}
  .tile {{
    position: relative; background: var(--card); border-radius: var(--radius);
    padding: 14px 8px 12px; display: flex; flex-direction: column;
    align-items: center; gap: 9px; cursor: pointer;
    transition: transform .12s ease, opacity .12s ease; border: 0; width: 100%;
    font-family: inherit; color: var(--text);
  }}
  .tile:active {{ transform: scale(.96); }}
  .icon {{
    width: 50px; height: 50px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; background: rgba(127,127,127,.13);
  }}
  .name {{ font-size: 11.5px; font-weight: 600; text-align: center; line-height: 1.2; }}
  .pin {{
    position: absolute; top: 5px; right: 5px; border: 0; background: transparent;
    color: var(--hint); font-size: 13px; padding: 4px 5px; cursor: pointer; opacity: .55;
  }}
  .tile.pinned .pin {{ opacity: 1; color: #f5b301; }}
  .badge {{
    position: absolute; bottom: 5px; right: 7px; font-size: 9px;
    color: var(--hint); background: var(--bg); border-radius: 6px; padding: 1px 4px;
  }}
  #empty {{ color: var(--hint); text-align: center; margin-top: 40px; font-size: 14px; }}
  footer {{ color: var(--hint); font-size: 11.5px; text-align: center; margin-top: 26px; line-height: 1.5; }}
</style>
</head>
<body>
<header>
  <h1>Social Hub</h1>
  <p class="sub">Tap an app to open it right here.</p>
  <div class="search"><input id="q" type="search" placeholder="Search apps…" autocomplete="off"></div>
</header>

<main>
  <section id="pinnedSec" hidden>
    <h2>Pinned</h2>
    <div id="pinnedGrid" class="grid"></div>
  </section>
  <section>
    <h2 id="allTitle">All apps</h2>
    <div id="grid" class="grid"></div>
  </section>
  <p id="empty" hidden>No app matches that search.</p>
  <footer>Tap ★ to pin an app.<br>Pinned apps stay at the top on this device.</footer>
</main>

<script>
  const APPS = {apps_json};
  const WA_NUMBER = {json.dumps(wa_number)};
  const tg = window.Telegram ? window.Telegram.WebApp : null;
  try {{ if (tg) {{ tg.ready(); tg.expand(); }} }} catch (e) {{}}

  const platform = (tg && tg.platform) ? tg.platform : 'web';
  const isPhone = platform === 'android' || platform === 'ios';

  function keyFor(app) {{ return app.name.toLowerCase(); }}
  function urlFor(app) {{
    if (keyFor(app) === 'whatsapp' && isPhone && WA_NUMBER) {{
      return 'https://wa.me/' + WA_NUMBER.replace(/[^0-9]/g, '');
    }}
    return app.url;
  }}

  let pins = [];
  try {{ pins = JSON.parse(localStorage.getItem('sociobot.pins') || '[]'); }} catch (e) {{ pins = []; }}
  if (!Array.isArray(pins)) pins = [];

  const grid = document.getElementById('grid');
  const pinnedGrid = document.getElementById('pinnedGrid');
  const pinnedSec = document.getElementById('pinnedSec');
  const allTitle = document.getElementById('allTitle');
  const empty = document.getElementById('empty');
  const q = document.getElementById('q');

  function makeTile(app) {{
    const b = document.createElement('button');
    b.className = 'tile' + (pins.includes(keyFor(app)) ? ' pinned' : '');
    b.type = 'button';
    b.setAttribute('aria-label', 'Open ' + app.name);
    b.innerHTML = '<span class="pin" role="button" aria-label="Pin">★</span>' +
                  '<span class="icon">' + app.emoji + '</span>' +
                  '<span class="name"></span>' +
                  (keyFor(app) === 'whatsapp' && isPhone ? '<span class="badge">app</span>' : '');
    b.querySelector('.name').textContent = app.name;

    b.addEventListener('click', function (ev) {{
      if (ev.target.classList.contains('pin')) {{
        ev.stopPropagation();
        togglePin(app);
        return;
      }}
      try {{ tg && tg.HapticFeedback && tg.HapticFeedback.impactOccurred('light'); }} catch (e) {{}}
      window.location.href = urlFor(app);
    }});
    return b;
  }}

  function togglePin(app) {{
    const k = keyFor(app);
    pins = pins.includes(k) ? pins.filter(function (x) {{ return x !== k; }}) : pins.concat([k]);
    try {{ localStorage.setItem('sociobot.pins', JSON.stringify(pins)); }} catch (e) {{}}
    try {{ tg && tg.HapticFeedback && tg.HapticFeedback.selectionChanged(); }} catch (e) {{}}
    render();
  }}

  function render() {{
    const term = q.value.trim().toLowerCase();
    const shown = APPS.filter(function (a) {{ return a.name.toLowerCase().indexOf(term) !== -1; }});
    const pinnedApps = shown.filter(function (a) {{ return pins.includes(keyFor(a)); }});
    const rest = shown.filter(function (a) {{ return !pins.includes(keyFor(a)); }});

    grid.replaceChildren.apply(grid, rest.map(makeTile));
    pinnedGrid.replaceChildren.apply(pinnedGrid, pinnedApps.map(makeTile));
    pinnedSec.hidden = pinnedApps.length === 0;
    allTitle.textContent = pinnedApps.length ? 'All apps' : 'Apps';
    empty.hidden = shown.length !== 0;
  }}

  q.addEventListener('input', render);
  render();
</script>
</body>
</html>
"""

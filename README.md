# Sociobot 🔗

A Telegram bot with a bottom keyboard full of social apps. Tap one and it
opens **inside Telegram as a Mini App** — no external browser, no leaving the
chat.

```
👋 Hey Ada!

Tap any social app on the keyboard below — it opens right here
inside Telegram as a Mini App.

👇 Pick a platform

Keyboard at the bottom of the chat:

[ 🎵 TikTok ]      [ 📸 Instagram ]
[ 📘 Facebook ]    [ 🐦 X / Twitter ]
[ ▶️ YouTube ]     [ 💬 WhatsApp ]

              [ 🏠 Home ]
```

---

## Setup (5 minutes)

### 1. Get your bot token
1. Open **@BotFather** in Telegram.
2. Send `/mybots` → pick your bot → **API Token**.
   (If you never made one: send `/newbot` and follow the prompts.)
3. Copy the token — it looks like `123456789:AAH...`.

### 2. Put the token in `.env`
Open the file **`.env`** in this folder (create it by copying `.env.example`
if it isn't there) and paste the token:

```
BOT_TOKEN=123456789:AAH-your-real-token-here
```

> Never share this token or commit it anywhere. It is the password to your bot.

### 3. Add your links
Open **`config.py`**. It already points at each app's own site (TikTok,
Instagram, Facebook, X, …). To point at **your** profile instead, swap the URL:

```python
SOCIAL_LINKS = [
    ("🎵", "TikTok",    "https://www.tiktok.com/@myusername"),
    ("📸", "Instagram", "https://www.instagram.com/myusername"),
    ...
]
```

* Use the full `https://...` link to your profile.
* Set a link to `""` to hide that button.
* Add your own rows with any emoji + name + link.

### 4. Start the bot
Double-click **`run.bat`**.

It installs everything the first time, then starts the bot. Leave the black
window open — closing it stops the bot.

### 5. Test it
Open your bot in Telegram and send `/start`. Tap a button.

---

## Commands

| Command  | What it does                  |
| -------- | ----------------------------- |
| `/start` | Welcome message + all buttons |
| `/links` | Show all links again          |
| `/help`  | Short explanation             |

---

## Good to know

**It really opens inside Telegram.** Each button is a Mini App button, so the
site opens over the chat with a Telegram header and a close button — not the
external browser.

**Telegram only allows `http://` and `https://` links** in buttons — custom
app links like `instagram://` are blocked by Telegram, so always use `https://`.

**WhatsApp uses WhatsApp Web** (`https://web.whatsapp.com`): it shows the QR
code inside the Mini App. Scan it once from your phone (WhatsApp → Linked
devices) and you can chat right there in Telegram. Use `https://wa.me/<number>`
instead if you'd rather open a direct chat with one number.

**🏠 Home** is a normal keyboard button (not a Mini App): tapping it sends
"Home" and the bot replies with the welcome screen and keyboard again.

**Editing links:** change `config.py`, then restart the bot (Ctrl+C in the
black window, then `run.bat` again). Users get the new buttons the next time
they press `/start`.

---

## Files

| File             | What it's for                                  |
| ---------------- | ---------------------------------------------- |
| `config.py`      | **Your links and message text** — edit this    |
| `.env`           | Your secret bot token (never share)            |
| `bot.py`         | The bot code — no need to touch it             |
| `api/index.py`   | Vercel entry point (used only on Vercel)       |
| `pyproject.toml` | Vercel entrypoint + dependency list            |
| `set_webhook.py` | Connects Telegram to Vercel — run once         |
| `vercel.json`    | Vercel deployment settings                     |
| `run.bat`        | Double-click to start the bot on your PC       |
| `requirements.txt` | Python packages needed                       |

---

## Running it 24/7 (hosting)

A bot only replies while it's running. These options keep it online 24/7.

### Free options compared

| Host | Cost | Card needed | Always on? | Setup |
|---|---|---|---|---|
| **Vercel** (chosen — webhook) | $0 | No | ✅ Yes (1–3s cold start) | Easy |
| **Render** (free web service) | $0 | Usually no | Sleeps when idle → wake it with a free ping | ⭐ Easy |
| **Oracle Cloud** (Always Free VM) | $0 forever | Yes (verification only) | ✅ Yes | Hard (~30 min, one time) |
| **Koyeb** (free) | $0 | Card for verification | Wakes on each message (2–5s delay) | Easy |
| **Hugging Face Spaces** | $0 | No | May sleep when unused | Medium |
| Free "Telegram bot" hosts | $0 | No | Varies | Avoid — see warning |

The honest truth: **free tiers change often** and none of them are as reliable
as $5/month. But all of the above can genuinely run this bot for $0.

---

## Option 1 — Vercel (free)

Vercel can't run a long-lived program, so on Vercel the bot uses **webhook
mode**: Telegram pushes each message to a serverless function. That code is
already written (`api/index.py`), and `pyproject.toml` tells Vercel where to
find it.

> **Vercel Hobby is for personal projects only.** If this bot is for a
> business or commercial brand, Vercel's terms require the Pro plan (~$20/mo).

### Deploy

1. Push this folder to GitHub (commands under "Put it on GitHub" below).
2. **vercel.com** → **Add New…** → **Project** → import your repo.
3. Framework preset: **Other**. Leave build settings empty.
4. **Environment Variables** (add before deploying):
   * `BOT_TOKEN` — from @BotFather
   * `WEBHOOK_SECRET` — any random text you invent, e.g. `socio-9f3k2`
     (extra security; only Telegram can then call your endpoint)
5. **Deploy** and wait ~1 minute.
6. Copy the production URL, e.g. `https://sociobot.vercel.app`.

### Connect Telegram (one time)

Run this on your PC:

```powershell
.\.venv\Scripts\python.exe set_webhook.py https://sociobot.vercel.app
```

It should print `Webhook connected: https://sociobot.vercel.app/`. Now message
your bot.

**Check it's alive:** open `https://sociobot.vercel.app/` in a browser — it
should say *"Sociobot webhook is alive."*

### Good to know

* **Cold starts:** after a quiet period the first reply can take 1–5 seconds.
  Telegram waits up to 60 seconds, so nothing is lost.
* **Limits:** Hobby includes ~1M function calls and 100 GB-hours/month. A link
  bot uses a tiny fraction.
* **Changes:** push to GitHub and Vercel redeploys automatically. The URL
  stays the same, so the webhook keeps working.
* **Go back to running locally:** run
  `python set_webhook.py --remove`, then `run.bat`.
* **Don't run both:** while the webhook is set, polling (local `run.bat`) won't
  receive messages — that's expected, not a bug.
* **Vercel CLI (alternative):** `npm i -g vercel`, then `vercel --prod`, and
  add the env vars with `vercel env add BOT_TOKEN`.

---

## Option 2 — Render free (also $0)

Free web services can't keep a program running, so the bot runs in **webhook
mode** instead of polling. That mode is already built into `bot.py` — you just
set one extra variable.

1. Push this folder to GitHub (see the commands under "Put it on GitHub" below).
2. Go to **render.com** → **New** → **Blueprint** → pick your repo.
   Render reads `render.yaml` and configures everything.
3. It asks for two values:
   * `BOT_TOKEN` = your token from @BotFather
   * `WEBHOOK_URL` = the address Render gives you, e.g.
     `https://sociobot-abc1.onrender.com`
     (you can deploy once, copy the URL, then edit the variable and redeploy)
4. Wait for the build (3–5 minutes). Logs should show
   `Bot is running in webhook mode`.
5. **Stop it sleeping:** Render free services spin down after 15 idle minutes.
   Create a free account at **cron-job.org**, add a job that opens your app URL
   (`https://sociobot-abc1.onrender.com/`) every **10 minutes**. That keeps it
   awake within the 750 free hours/month.

> First reply after a long idle period can take ~30–50 seconds while the
> server wakes up. After that it's instant.

---

## Option 3 — Oracle Cloud Always Free (best long-term $0)

The only option that is free forever, always on, with no sleeping and no
rewrite. Needs a card for identity verification (nothing is charged).

1. Sign up at **oracle.com/cloud/free** and create an **Always Free** VM:
   Ubuntu 22.04, shape `VM.Standard.E2.1.Micro` (or Ampere `A1.Flex`).
2. Download the SSH key when prompted.
3. Connect: `ssh -i yourkey.pem ubuntu@YOUR_SERVER_IP`
4. Install and run:
   ```bash
   sudo apt update && sudo apt install -y python3-venv git
   git clone https://github.com/YOURNAME/sociobot.git
   cd sociobot
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   echo "BOT_TOKEN=your-token" > .env
   .venv/bin/python bot.py      # test it works
   ```
5. Keep it running after you disconnect with `tmux`, or properly with systemd:
   ```bash
   sudo tee /etc/systemd/system/sociobot.service >/dev/null <<'EOF'
   [Unit]
   Description=Sociobot
   After=network-online.target

   [Service]
   WorkingDirectory=/home/ubuntu/sociobot
   ExecStart=/home/ubuntu/sociobot/.venv/bin/python bot.py
   Restart=always
   User=ubuntu

   [Install]
   WantedBy=multi-user.target
   EOF
   sudo systemctl enable --now sociobot
   ```
   No firewall ports needed — polling makes only outgoing connections.

---

## Option 4 — Koyeb free

**koyeb.com** → **Create Service** → GitHub → Dockerfile. Add `BOT_TOKEN` and
`WEBHOOK_URL` (`https://your-app.koyeb.app`) as environment variables. Free
instances wake when a message arrives, so the first reply may be a few seconds
slow.

## Option 5 — Hugging Face Spaces (no card at all)

Create a **Docker** Space, upload this project, and add `BOT_TOKEN` as a
Secret under Settings. It runs `python bot.py` in polling mode. Free Spaces may
sleep after long inactivity — a daily visit to the Space page keeps it alive.

---

## ⚠️ About free "Telegram bot hosting" sites

Sites that advertise "free Telegram bot hosting" are usually run by hobbyists.
Your `BOT_TOKEN` gives full control of your bot, so a bad host can read it and
take over the bot. Only use one you trust, and regenerate the token with
`/revoke` in @BotFather if you ever stop using it.

---

## Put it on GitHub

```powershell
git init
git add .
git commit -m "sociobot"
# create an EMPTY repo on github.com, then:
git remote add origin https://github.com/YOURNAME/sociobot.git
git push -u origin main
```

`.gitignore` and `.dockerignore` already keep `.venv` and `.env` out. **Never
commit `.env`** — set `BOT_TOKEN` in the host's dashboard instead.

## How the two modes work

* **Polling** (default): the bot asks Telegram for messages. Used locally,
  on Railway, VPS, Oracle, Hugging Face. Needs no public URL.
* **Webhook**: Telegram pushes messages to your app's URL. Used on Render,
  Koyeb, and other free web hosts. Enabled automatically when `WEBHOOK_URL`
  is set, e.g. `WEBHOOK_URL=https://sociobot.onrender.com`. The port comes
  from `PORT` (defaults to 8080).

## Main points

* Update links by editing `config.py` and pushing to GitHub — the host
  redeploys automatically.
* Only ONE copy should run at a time. Stop your local `run.bat` once hosting
  is live, or the two fight over messages.
* Switch modes freely: remove `WEBHOOK_URL` and the bot goes back to polling.

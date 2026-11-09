"""
EDIT THIS FILE TO CUSTOMISE YOUR BOT.
Everything the bot shows to users lives here. No coding needed.

After changing anything, restart the bot (Ctrl+C, then run it again).
"""

# ---------------------------------------------------------------------------
# 1. THE SOCIAL APPS
# ---------------------------------------------------------------------------
# Format:  ("emoji", "Button name", "https://link")
#
# These point at each app's own site, so tapping opens that app's page and
# offers "Open in app" to go straight into the installed app.
# To point at YOUR profile instead, use e.g. https://www.instagram.com/yourname
# Leave the URL as "" (two quote marks, nothing inside) to hide that button.
# Only http:// and https:// links are allowed by Telegram.
# Tip: use "https://" for every link so it works on Android and iPhone.

SOCIAL_LINKS = [
    ("🎵", "TikTok",    "https://www.tiktok.com"),
    ("📸", "Instagram", "https://www.instagram.com"),
    ("📘", "Facebook",  "https://www.facebook.com"),
    ("🐦", "X / Twitter", "https://x.com"),
    ("▶️", "YouTube",   "https://www.youtube.com"),
    ("💬", "WhatsApp",  "https://web.whatsapp.com"),
    ("👻", "Snapchat",  "https://www.snapchat.com"),
    ("💼", "LinkedIn",  "https://www.linkedin.com"),
    ("🧵", "Threads",   "https://www.threads.net"),
    ("🎮", "Discord",   "https://discord.com"),
    ("📌", "Pinterest", "https://www.pinterest.com"),
    ("👽", "Reddit",    "https://www.reddit.com"),
]

# How many buttons per row (2 looks best on phones).
BUTTONS_PER_ROW = 2


# ---------------------------------------------------------------------------
# 2. THE MESSAGE TEXT
# ---------------------------------------------------------------------------
# {name} is replaced with the user's first name.
# HTML is allowed: <b>bold</b>, <i>italic</i>, <a href="...">link</a>

WELCOME_TEXT = (
    "👋 Hey {name}!\n\n"
    "Tap any social app on the keyboard below — it opens right here "
    "inside Telegram as a Mini App.\n\n"
    "👇 <b>Pick a platform</b>"
)

# Shown for /links and for any message the bot doesn't understand.
LINKS_TEXT = "🔗 <b>All the apps</b>\n\nPick one on the keyboard below 👇"


# ---------------------------------------------------------------------------
# 3. STUFF YOU PROBABLY DON'T NEED TO TOUCH
# ---------------------------------------------------------------------------
# Your bot token is read from the .env file, NOT from here (safer).
# Set it in .env like this:  BOT_TOKEN=123456:ABC-your-token

"""
EDIT THIS FILE TO CUSTOMISE YOUR BOT.
Everything the bot shows to users lives here. No coding needed.

After changing anything, restart the bot (Ctrl+C, then run it again).
"""

# ---------------------------------------------------------------------------
# 1. YOUR SOCIAL PROFILES
# ---------------------------------------------------------------------------
# Format:  ("emoji", "Button name", "https://your-profile-link")
#
# Leave the URL as "" (two quote marks, nothing inside) to hide that button.
# Only http:// and https:// links are allowed by Telegram.
# Tip: use "https://" for every link so it works on Android and iPhone.

SOCIAL_LINKS = [
    ("🎵", "TikTok",    "https://www.tiktok.com/@yourname"),
    ("📸", "Instagram", "https://www.instagram.com/yourname"),
    ("📘", "Facebook",  "https://www.facebook.com/yourname"),
    ("🐦", "X / Twitter", "https://x.com/yourname"),
    ("▶️", "YouTube",   "https://www.youtube.com/@yourname"),
    ("💬", "WhatsApp",  "https://wa.me/2340000000000"),
    ("👻", "Snapchat",  "https://www.snapchat.com/add/yourname"),
    ("💼", "LinkedIn",  "https://www.linkedin.com/in/yourname"),
    ("🧵", "Threads",   "https://www.threads.net/@yourname"),
    ("🎮", "Discord",   ""),
    ("📌", "Pinterest", ""),
    ("🤖", "Telegram Channel", ""),
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
    "Welcome to my page. Tap any button below to open one of my "
    "social media profiles — it opens right here inside Telegram.\n\n"
    "👇 <b>Pick a platform</b>"
)

# Shown for /links and for any message the bot doesn't understand.
LINKS_TEXT = "🔗 <b>All my links</b>\n\nTap a button to open a profile:"


# ---------------------------------------------------------------------------
# 3. STUFF YOU PROBABLY DON'T NEED TO TOUCH
# ---------------------------------------------------------------------------
# Your bot token is read from the .env file, NOT from here (safer).
# Set it in .env like this:  BOT_TOKEN=123456:ABC-your-token

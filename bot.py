"""Sociobot — a Telegram "link in bio" bot.

Users tap a button and the social profile opens inside Telegram's
built-in browser. Edit config.py to change the links and message text.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from telegram import (
    KeyboardButton,
    LinkPreviewOptions,
    ReplyKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.constants import ParseMode
from telegram.error import InvalidToken
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Keyboard
# ---------------------------------------------------------------------------
def build_keyboard() -> ReplyKeyboardMarkup | None:
    """Turn the links in config.py into Mini App buttons on the bottom keyboard.

    Each button is a web_app button, so tapping it opens the site inside
    Telegram as a Mini App instead of the external browser.
    """
    buttons = [
        KeyboardButton(text=f"{emoji} {label}", web_app=WebAppInfo(url=url.strip()))
        for emoji, label, url in config.SOCIAL_LINKS
        if url and url.strip()
    ]

    if not buttons:
        logger.warning("No links are set in config.py — the keyboard will be empty.")
        return None

    per_row = max(1, config.BUTTONS_PER_ROW)
    rows = [buttons[i : i + per_row] for i in range(0, len(buttons), per_row)]
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Choose a platform",
    )


async def send_links(update: Update, text: str) -> None:
    """Send a text message together with the social buttons."""
    await update.effective_message.reply_text(
        text,
        reply_markup=build_keyboard(),
        parse_mode=ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = (user.first_name if user else None) or "there"
    await send_links(update, config.WELCOME_TEXT.format(name=name))


async def links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_links(update, config.LINKS_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_links(
        update,
        "ℹ️ <b>How this works</b>\n\n"
        "The apps are on the keyboard at the bottom of the chat. Tap one "
        "and it opens inside Telegram as a Mini App — you never leave.\n\n"
        "Commands:\n"
        "/start — welcome message\n"
        "/links — show the keyboard\n"
        "/help — this message",
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_links(update, "Here are all the apps 👇 tap one on the keyboard.")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Something went wrong while handling an update", exc_info=context.error)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    is_placeholder = "AAExampleToken" in token or "your-real-token" in token

    if not token or is_placeholder:
        raise SystemExit(
            "\n  BOT_TOKEN is missing or still the example text.\n\n"
            "  1. Open the .env file in this folder.\n"
            "  2. Paste your token from @BotFather after BOT_TOKEN=\n"
            "     (format: 123456789:AAH...)\n"
            "  3. Save the file and run this again.\n"
        )

    if not any(url and url.strip() for _, _, url in config.SOCIAL_LINKS):
        raise SystemExit(
            "\n  You haven't added any links yet.\n"
            "  Open config.py and put your profile links in SOCIAL_LINKS.\n"
        )

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("links", links))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    app.add_error_handler(on_error)

    # Webhook mode is used by free hosts (Render, Koyeb, etc.) because they
    # don't allow a long-running process. Locally and on Railway/VPS we use
    # polling, which is simpler and needs no public URL.
    webhook_url = os.getenv("WEBHOOK_URL", "").strip().rstrip("/")

    try:
        if webhook_url:
            port = int(os.getenv("PORT", "8080"))
            path = "webhook"
            logger.info("Bot is running in webhook mode on port %s", port)
            app.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=path,
                webhook_url=f"{webhook_url}/{path}",
                secret_token=os.getenv("WEBHOOK_SECRET") or None,
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
            )
        else:
            logger.info("Bot is running in polling mode. Press Ctrl+C to stop.")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
    except InvalidToken:
        raise SystemExit(
            "\n  Telegram rejected the BOT_TOKEN.\n"
            "  Check that you copied the whole token from @BotFather\n"
            "  (it looks like 123456789:AAH... on a single line).\n"
        )


if __name__ == "__main__":
    main()

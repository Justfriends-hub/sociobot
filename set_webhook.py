"""Connect your Telegram bot to your Vercel deployment.

Run this ONCE from your PC, after the Vercel deploy is finished:

    python set_webhook.py https://your-project.vercel.app

To go back to running locally with run.bat:

    python set_webhook.py --remove

It reads BOT_TOKEN (and optional WEBHOOK_SECRET) from your .env file.
"""

from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv
from telegram import Bot, Update

load_dotenv()


async def run(url: str, token: str, secret: str) -> None:
    async with Bot(token) as bot:
        if url:
            full_url = url.rstrip("/") + "/api/webhook"
            await bot.set_webhook(
                url=full_url,
                secret_token=secret or None,
                allowed_updates=[Update.MESSAGE],
                drop_pending_updates=True,
            )
            print("Webhook connected:", full_url)
        else:
            await bot.delete_webhook(drop_pending_updates=True)
            print("Webhook removed. You can run the bot locally again.")

        info = await bot.get_webhook_info()
        print("Pending updates:", info.pending_update_count)
        if info.last_error_message:
            print("Last error:", info.last_error_message)


def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    secret = os.getenv("WEBHOOK_SECRET", "").strip()

    if not token or "AAExampleToken" in token:
        raise SystemExit("Set your real BOT_TOKEN in .env first.")

    args = [a for a in sys.argv[1:]]
    if "--remove" in args:
        asyncio.run(run("", token, secret))
        return

    url = args[0] if args else os.getenv("WEBHOOK_URL", "").strip()
    if not url:
        raise SystemExit(
            "Usage: python set_webhook.py https://your-project.vercel.app\n"
            "   or: python set_webhook.py --remove"
        )

    asyncio.run(run(url, token, secret))


if __name__ == "__main__":
    main()

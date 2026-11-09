"""Health check: tells you exactly why the bot is (or isn't) receiving messages.

Run:  .\\.venv\\Scripts\\python.exe doctor.py
"""

from __future__ import annotations

import asyncio
import os
import urllib.request

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


async def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or "AAExampleToken" in token:
        raise SystemExit("BOT_TOKEN is missing in .env")

    async with Bot(token) as bot:
        me = await bot.get_me()
        print(f"Bot            : @{me.username} ({me.first_name})")
        print(f"Token          : ...{token[-6:]}")

        info = await bot.get_webhook_info()
        print(f"Webhook URL    : {info.url or '(none — Telegram has nowhere to send messages)'}")
        print(f"Pending updates: {info.pending_update_count}")
        print(f"Last error     : {info.last_error_message or 'none'}")
        print(f"Last error time: {info.last_error_date or 'none'}")
        print(f"Secret set here: {bool(os.getenv('WEBHOOK_SECRET'))}")

        if info.url:
            try:
                with urllib.request.urlopen(info.url, timeout=20) as r:
                    body = r.read(200).decode("utf-8", "replace")
                print(f"Health check   : {r.status} — {body}")
            except Exception as exc:  # noqa: BLE001
                print(f"Health check   : FAILED — {exc}")

        print()
        if not info.url:
            print(">> No webhook is set. Run: python set_webhook.py https://YOUR-PROJECT.vercel.app")
        elif "403" in (info.last_error_message or ""):
            print(">> Telegram is being rejected (403). WEBHOOK_SECRET in .env does not match Vercel.")
        elif "500" in (info.last_error_message or ""):
            print(">> The Vercel function crashed (500). Check the runtime logs on Vercel.")
        elif "404" in (info.last_error_message or ""):
            print(">> Wrong URL (404). Re-run set_webhook.py with the correct Vercel domain.")
        else:
            print(">> Webhook looks configured. If the bot is still silent, check Vercel logs.")


if __name__ == "__main__":
    asyncio.run(main())

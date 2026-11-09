"""Telegram webhook endpoint for Vercel.

Telegram sends every update to:
    https://<your-project>.vercel.app/api/webhook

Vercel runs this file as a short-lived function. The bot has no stored state,
so each request builds a fresh Application, handles the update, and shuts down.
"""

from __future__ import annotations

import asyncio
import json
import os
from http.server import BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

import bot as bot_module


def build_app() -> Application:
    """Same handlers as bot.py, without the polling loop."""
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", bot_module.start))
    app.add_handler(CommandHandler("links", bot_module.links))
    app.add_handler(CommandHandler("help", bot_module.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_module.unknown))
    app.add_error_handler(bot_module.on_error)
    return app


async def handle_update(data: dict) -> None:
    if not data.get("update_id"):
        return
    app = build_app()
    await app.initialize()
    try:
        update = Update.de_json(data, app.bot)
        if update is not None:
            await app.process_update(update)
    finally:
        await app.shutdown()


class handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, text: str = "") -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        # Simple health check — opening this URL in a browser should show this.
        self._reply(200, "Sociobot webhook is alive.")

    def do_POST(self) -> None:
        secret = os.getenv("WEBHOOK_SECRET", "").strip()
        if secret:
            sent = self.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if sent != secret:
                self._reply(403, "forbidden")
                return

        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            data = json.loads(raw or b"{}")
        except (ValueError, TypeError):
            self._reply(400, "bad request")
            return

        try:
            asyncio.run(handle_update(data))
        except Exception:
            # Always answer 200 so Telegram doesn't retry the same update forever.
            bot_module.logger.exception("Failed to process update")
            self._reply(200, "error logged")
            return

        self._reply(200, "ok")

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass

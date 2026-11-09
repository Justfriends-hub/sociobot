"""Telegram webhook endpoint for Vercel (WSGI).

Vercel's Python runtime loads ONE app, so this WSGI callable answers every
path on the deployment. Telegram POSTs updates to the site root; a browser
opening the root gets a health check.

Why WSGI instead of a BaseHTTPRequestHandler: Vercel CLI 65+ requires a single
ASGI/WSGI entrypoint declared in pyproject.toml, and does not accept a
BaseHTTPRequestHandler class as that entrypoint.
"""

from __future__ import annotations

import asyncio
import json
import os

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


def _respond(status: str, text: str):
    body = text.encode("utf-8")
    headers = [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    return status, headers, body


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()

    if method != "POST":
        status, headers, body = _respond("200 OK", "Sociobot webhook is alive.")
        start_response(status, headers)
        return [body]

    secret = os.getenv("WEBHOOK_SECRET", "").strip()
    if secret:
        sent = environ.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN", "")
        if sent != secret:
            status, headers, body = _respond("403 Forbidden", "forbidden")
            start_response(status, headers)
            return [body]

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        raw = environ["wsgi.input"].read(length) if length else b"{}"
        data = json.loads(raw or b"{}")
    except (ValueError, TypeError, KeyError):
        status, headers, body = _respond("400 Bad Request", "bad request")
        start_response(status, headers)
        return [body]

    try:
        asyncio.run(handle_update(data))
    except Exception:
        # Always answer 200 so Telegram does not retry the same update forever.
        bot_module.logger.exception("Failed to process update")
        status, headers, body = _respond("200 OK", "error logged")
        start_response(status, headers)
        return [body]

    status, headers, body = _respond("200 OK", "ok")
    start_response(status, headers)
    return [body]

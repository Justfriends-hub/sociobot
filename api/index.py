"""Telegram webhook endpoint for Vercel (WSGI).

Vercel's Python runtime loads ONE app, so this WSGI callable answers every
path on the deployment. Telegram POSTs updates to the site root.

Diagnostics:
    GET  /              -> health + whether BOT_TOKEN is configured
    GET  /?selftest=1   -> calls Telegram with the DEPLOYED token and reports
                           the bot username / webhook state (no secrets shown)
    POST /              -> Telegram update
"""

from __future__ import annotations

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

import bot as bot_module

# Filled by the error handler during a request so the WSGI layer can report it.
_handler_errors: list[str] = []


async def _collect_error(update, context) -> None:
    _handler_errors.append(type(context.error).__name__)
    bot_module.logger.error("Handler error: %s", context.error)


def build_app() -> Application:
    """Same handlers as bot.py, without the polling loop."""
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", bot_module.start))
    app.add_handler(CommandHandler("links", bot_module.links))
    app.add_handler(CommandHandler("help", bot_module.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_module.unknown))
    app.add_error_handler(_collect_error)
    return app


def run_async(coro):
    """Run a coroutine even if this thread already has an event loop running."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # A loop is already running here (some hosts do this); use a fresh loop
    # in a separate thread instead of crashing with "asyncio.run() cannot...".
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


async def handle_update(data: dict) -> None:
    if not data.get("update_id"):
        return
    del _handler_errors[:]
    app = build_app()
    await app.initialize()
    try:
        update = Update.de_json(data, app.bot)
        if update is not None:
            await app.process_update(update)
    finally:
        await app.shutdown()

    if _handler_errors:
        raise RuntimeError(_handler_errors[0])


async def _selftest() -> str:
    async with Bot(os.environ["BOT_TOKEN"]) as bot:
        me = await bot.get_me()
        info = await bot.get_webhook_info()
        return (
            f"selftest ok: @{me.username} | webhook={info.url or 'none'} | "
            f"pending={info.pending_update_count} | "
            f"last_error={info.last_error_message or 'none'}"
        )


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
        query = environ.get("QUERY_STRING", "")
        if "selftest" in query:
            try:
                text = run_async(_selftest())
            except Exception as exc:  # noqa: BLE001
                # Only the exception class — never echo the token.
                text = f"selftest failed: {type(exc).__name__}"
            status, headers, body = _respond("200 OK", text)
            start_response(status, headers)
            return [body]

        token_state = "set" if os.getenv("BOT_TOKEN", "").strip() else "MISSING"
        status, headers, body = _respond(
            "200 OK", f"Sociobot webhook is alive. bot_token={token_state}"
        )
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
        run_async(handle_update(data))
    except Exception as exc:  # noqa: BLE001
        bot_module.logger.exception("Failed to process update")
        # 500 makes the failure visible in Telegram's getWebhookInfo.
        status, headers, body = _respond(
            "500 Internal Server Error", f"error:{type(exc).__name__}"
        )
        start_response(status, headers)
        return [body]

    status, headers, body = _respond("200 OK", "ok")
    start_response(status, headers)
    return [body]

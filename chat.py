
import logging
import asyncio
import json
import urllib.request
import urllib.error

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ==================================
# API KEYS - මෙතැන Keys දාන්න
# ==================================

TELEGRAM_TOKEN = "9055311886:AAEno4YCqPkVNMBMaQHj6eQ6YmcTu81Qj8w"
GEMINI_API_KEY = "AQ.Ab8RN6LV3YFEZPd-7dQdsavW9Ee5yhTuesemUqsbQkrpETCd4g"

MODEL = "gemini-2.5-flash"

# ==================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def ask_gemini(message):

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
    )

    payload = {
        "contents": [{
            "parts": [{"text": message}]
        }]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["candidates"][0]["content"]["parts"][0]["text"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "ආයුබෝවන්! 🤖\n"
        "මම Gemini AI Assistant Bot.\n"
        "ඕනෑම දෙයක් මගෙන් අසන්න."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message.text

    wait = await update.message.reply_text("🤖 Thinking...")

    try:

        answer = await asyncio.to_thread(ask_gemini, message)

        await wait.delete()

        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i + 4000])

    except urllib.error.HTTPError as e:

        error = e.read().decode("utf-8")
        logging.error("Gemini API Error: %s", error)

        await wait.edit_text(
            f"Gemini API Error: HTTP {e.code}\n"
            "API Key සහ Google API access පරීක්ෂා කරන්න."
        )

    except Exception as e:

        logging.exception("Bot Error")

        await wait.edit_text(
            "දෝෂයක් ඇතිවුණා. නැවත උත්සාහ කරන්න."
        )


def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Gemini AI Bot is running...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

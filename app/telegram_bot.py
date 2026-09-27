import requests
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_notification(result):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    level_emoji = {
        "green": "🟢",
        "yellow": "🟡",
        "red": "🔴"
    }

    emoji = level_emoji.get(result["level"], "⚪")

    message = f"""{emoji} Fishing Net Alert

Вердикт: {result['verdict']}
Уровень: {result['level']}

Объяснение:
{result['explanation']}"""

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload)
    except Exception:
        pass

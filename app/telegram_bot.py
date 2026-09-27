import logging
import os

import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LEVEL_EMOJI = {"green": "🟢", "yellow": "🟡", "red": "🔴"}


async def send_notification(result: dict):
    """Шлём вердикт в чат. Без ключей — молча пропускаем."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    lines = [
        f"{LEVEL_EMOJI.get(result['level'], '⚪')} Fishing Net Alert",
        "",
        f"Вердикт: {result['verdict']}",
    ]
    if result.get("subject"):
        lines.append(f"Тема: {result['subject']}")
    lines += ["", f"Объяснение: {result['explanation']}"]
    if result.get("advice"):
        lines.append(f"Рекомендация: {result['advice']}")

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "\n".join(lines),
    }
    try:
        # без parse_mode HTML: спецсимволы в теме письма не сломают сообщение
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
            timeout=10,
        )
    except Exception:
        logger.warning("Не удалось отправить уведомление в Telegram")

"""
Менеджер LLM: ходим в DeepSeek за глубоким анализом письма.

Промпт держим в одном месте, чтобы его было удобно тюнить.
Ответ парсим аккуратно: модели любят оборачивать JSON в markdown-блоки.
"""

import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"

SYSTEM_PROMPT = """Ты — старший аналитик SOC с многолетним опытом расследования фишинговых кампаний.
Тебе приходит входящее письмо. Реши, опасно ли оно, и объясни решение так, чтобы понял сотрудник без технического бэкграунда.

Методика анализа (проверь каждый пункт):
1. Отправитель и контекст: соответствует ли адрес заявленной организации? Нет ли подмены домена, случайных символов, бесплатных почтовых сервисов у "корпоративного" письма?
2. Манипулятивные техники: срочность и дедлайны, запугивание штрафами и блокировками, требование секретности, апелляция к авторитету руководства, дефицит времени, приманка наградой или страхом.
3. Запрашиваемое действие: просят ли деньги, смену реквизитов, пароли, коды из СМС, переход по ссылке, открытие вложения, отход от привычных бизнес-процедур?
4. Язык и стиль: давление, отсутствие конкретики, нехарактерный тон для деловой переписки, странные формулировки.
5. Технический контекст: ссылки, домены, вложения, расхождение отображаемого имени и реального адреса.

Правила вердикта:
- red: есть сочетание манипулятивной техники и опасного запроса (деньги, данные, доступ).
- yellow: что-то настораживает, но доказательств недостаточно (неожиданный тон, мягкая срочность, непроверенные ссылки).
- green: обычная деловая или личная переписка без манипуляций и опасных запросов.

Формат ответа — СТРОГО один JSON-объект, без markdown и пояснений:
{
  "level": "green" | "yellow" | "red",
  "verdict": "Безопасное" | "Подозрительное" | "Фишинг",
  "explanation": "2-4 предложения простым языком: что именно опасно и почему",
  "techniques": ["список найденных манипулятивных техник"],
  "confidence": 0.0-1.0,
  "advice": "одно короткое действие для получателя, например: перезвоните отправителю по известному номеру"
}"""

USER_TEMPLATE = """Проанализируй письмо.

Тема: {subject}
Текст:
{body}"""


def _extract_json(raw: str) -> dict:
    """Срезаем markdown-обёртку, если модель всё-таки её добавила."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("В ответе модели нет JSON-объекта")
    return json.loads(raw[start:end + 1])


async def get_llm_analysis(subject: str, body: str) -> dict:
    """Отправляем письмо в DeepSeek и возвращаем разобранный вердикт."""
    if not DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY не задан, глубокий анализ пропущен")
        return {
            "level": "yellow",
            "verdict": "Ошибка анализа",
            "explanation": "Не задан ключ DeepSeek, глубокий анализ недоступен",
            "techniques": [],
            "confidence": 0.0,
            "advice": "проверьте файл .env",
        }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(subject=subject, body=body)},
        ],
        "temperature": 0.15,
        "max_tokens": 700,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }

    try:
        # для MVP синхронный requests норм, позже переведу на httpx
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return _extract_json(content)
    except Exception as exc:
        logger.exception("DeepSeek не ответил")
        return {
            "level": "yellow",
            "verdict": "Ошибка анализа",
            "explanation": f"LLM недоступна: {exc}",
            "techniques": [],
            "confidence": 0.0,
            "advice": "повторите проверку позже",
        }

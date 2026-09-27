

from app.llm_manager import get_llm_analysis

RED_FLAG_CATEGORIES = {
    "urgency": [
        "срочно", "немедленно", "в течение часа", "до конца дня",
        "как можно скорее", "времени нет", "urgent", "immediately",
        "asap", "within an hour", "by end of day",
    ],
    "secrecy": [
        "не обсуждай", "не обсуждайте", "никому не говори", "конфиденциально",
        "секретно", "лично для вас", "do not discuss", "confidential",
        "keep it secret", "between us",
    ],
    "authority": [
        "я директор", "от имени руководителя", "генеральный директор",
        "руководство требует", "главный бухгалтер требует", "i am the ceo",
        "from the management", "your manager",
    ],
    "money": [
        "оплати", "оплатите", "переведи", "переведите", "реквизиты",
        "новый счет", "счет поставщика", "изменились реквизиты",
        "подарочная карта", "invoice", "wire transfer", "payment details",
        "new bank account", "gift card",
    ],
    "credentials": [
        "подтверди пароль", "подтвердите пароль", "введите пароль", "логин",
        "пароль", "банковская карта", "cvv", "код из смс",
        "verify your account", "update your password",
        "enter your credentials", "one-time code",
    ],
    "threat": [
        "заблокируем", "блокировка", "штраф", "суд", "приостановим",
        "аккаунт будет удален", "suspended", "penalty", "legal action",
        "final notice",
    ],
    "reward": [
        "вы выиграли", "лотерея", "приз", "бонус начислен", "you won",
        "lottery", "prize", "reward waiting", "cashback expired",
    ],
}

CATEGORY_NAMES = {
    "urgency": "давление срочностью",
    "secrecy": "требование секретности",
    "authority": "имитация руководства",
    "money": "денежная просьба мимо процедур",
    "credentials": "запрос учётных данных",
    "threat": "угроза и запугивание",
    "reward": "приманка наградой",
}


YELLOW_SCORE = 1
RED_SCORE = 3


def quick_check(subject: str, body: str) -> dict:
    """Прогоняем текст по словарю и считаем очки по категориям."""
    text = f"{subject} {body}".lower()

    matched = []
    for category, flags in RED_FLAG_CATEGORIES.items():
        if any(flag in text for flag in flags):
            matched.append(category)

    score = len(matched)
    reasons = [CATEGORY_NAMES[c] for c in matched]

    if score >= RED_SCORE:
        return {
            "level": "red",
            "verdict": "Фишинг",
            "explanation": "Явные признаки социальной инженерии: " + ", ".join(reasons),
            "techniques": matched,
        }

    if score >= YELLOW_SCORE:
        return {
            "level": "yellow",
            "verdict": "Подозрительное",
            "explanation": "Есть настораживающие признаки: " + ", ".join(reasons),
            "techniques": matched,
        }

    return {
        "level": "unknown",
        "verdict": "Требуется анализ",
        "explanation": "Быстрая проверка не нашла явных признаков",
        "techniques": [],
    }


async def analyze_email_content(email) -> dict:
    """
    Главный вход анализатора: сначала эвристика, потом LLM.
    Красный вердикт от эвристики в LLM не отправляем — незачем тратить
    деньги на очевидные случаи.
    """
    quick_result = quick_check(email.subject, email.body)

    if quick_result["level"] == "red":
        return quick_result

    return await get_llm_analysis(email.subject, email.body)

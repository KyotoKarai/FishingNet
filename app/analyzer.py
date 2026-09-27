from app.llm_manager import get_llm_analysis

def quick_check(subject, body):
    text = f"{subject} {body}".lower()

    red_flags = [
        "срочно",
        "немедленно",
        "не обсуждай",
        "не обсуждайте",
        "конфиденциально",
        "в течение часа",
        "заблокируем",
        "блокировка",
        "штраф",
        "оплати",
        "оплатите",
        "переведи",
        "переведите",
        "подтверди пароль",
        "подтвердите пароль",
        "логин",
        "пароль",
        "банковская карта",
        "реквизиты",
        "счет поставщика",
        "новый счет"
    ]

    found = []

    for flag in red_flags:
        if flag in text:
            found.append(flag)

    if len(found) >= 3:
        return {
            "level": "red",
            "verdict": "Фишинг",
            "explanation": f"Обнаружены признаки социальной инженерии: {', '.join(found)}"
        }

    if len(found) >= 1:
        return {
            "level": "yellow",
            "verdict": "Подозрительное",
            "explanation": f"Есть подозрительные признаки: {', '.join(found)}"
        }

    return {
        "level": "unknown",
        "verdict": "Требуется анализ",
        "explanation": "Быстрая проверка не выявила явных признаков"
    }

async def analyze_email_content(email):
    quick_result = quick_check(email.subject, email.body)

    if quick_result["level"] == "red":
        return quick_result

    llm_result = await get_llm_analysis(email.subject, email.body)

    return llm_result

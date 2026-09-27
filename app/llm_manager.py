import requests
import os
import json

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

async def get_llm_analysis(subject, body):
    prompt = f"""
    Ты эксперт по кибербезопасности. Проанализируй письмо на фишинг.
    
    Тема: {subject}
    Текст: {body}
    
    Верни ТОЛЬКО JSON без пояснений:
    {{
        "level": "green" | "yellow" | "red",
        "verdict": "Безопасное" | "Подозрительное" | "Фишинг",
        "explanation": "Краткое объяснение"
    }}
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        return {
            "level": "yellow",
            "verdict": "Ошибка анализа",
            "explanation": f"LLM недоступна: {str(e)}"
        }

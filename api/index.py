import os
import requests
import json
from openai import OpenAI

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Необходимо задать BOT_TOKEN и OPENAI_API_KEY в переменных окружения")

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openrouter.ai/api/v1")

def handler(event, context):
    try:
        update = json.loads(event['body'])
        if not update:
            return {'statusCode': 400, 'body': 'No JSON received'}

        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            user_message = update["message"]["text"]

            # Генерация ответа через OpenRouter
            try:
                response = client.chat.completions.create(
                    model="anthropic/claude-3-haiku",
                    messages=[
                        {"role": "system", "content": "Ты — Friday, саркастичный и умный ассистент. Отвечай на русском, используй кириллицу."},
                        {"role": "user", "content": user_message}
                    ]
                )
                ai_response = response.choices[0].message.content
            except Exception as e:
                ai_response = f"Ошибка генерации ответа: {e}"

            # Отправка ответа через Telegram API
            try:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    data={"chat_id": chat_id, "text": ai_response}
                )
            except Exception as e:
                print("Ошибка отправки сообщения в Telegram:", e)

        return {'statusCode': 200, 'body': 'ok'}

    except Exception as e:
        print("Ошибка:", e)
        return {'statusCode': 500, 'body': f"Server error: {e}"}

import os
import requests
from openai import OpenAI
from vercel import Request, Response

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Необходимо задать BOT_TOKEN и OPENAI_API_KEY в переменных окружения")

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openrouter.ai/api/v1")

def handler(request: Request) -> Response:
    try:
        update = request.json()
        if not update:
            return Response.json({'error': 'No JSON received'}, status=400)

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

        return Response.json({'status': 'ok'})

    except Exception as e:
        print("Ошибка:", e)
        return Response.json({'error': f"Server error: {e}"}, status=500)

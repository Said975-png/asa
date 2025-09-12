import os
import requests
from flask import Flask, request
from openai import OpenAI
import traceback

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Необходимо задать BOT_TOKEN и OPENAI_API_KEY в переменных окружения")

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openrouter.ai/api/v1")
app = Flask(__name__)

@app.route("/api/index", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return "No JSON received", 400

        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            user_message = update["message"]["text"]

            # Логируем сообщение
            with open("history.txt", "a", encoding="utf-8") as f:
                user = update["message"]["from"]
                user_id = user.get("id", "unknown")
                username = user.get("username", "Нет username")
                first_name = user.get("first_name", "Нет имени")
                f.write(f"ID: {user_id}, Username: {username}, Name: {first_name}, Message: {user_message}\n")

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
                print(traceback.format_exc())

        return "ok", 200

    except Exception as e:
        print("Ошибка в webhook:", e)
        print(traceback.format_exc())
        return f"Server error: {e}", 500

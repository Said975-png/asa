import os
import requests
import json
from openai import OpenAI
from http.server import BaseHTTPRequestHandler

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Необходимо задать BOT_TOKEN и OPENAI_API_KEY в переменных окружения")

client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openrouter.ai/api/v1")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            if not update:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'No JSON received')
                return

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

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')

        except Exception as e:
            print("Ошибка:", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server error: {e}".encode('utf-8'))

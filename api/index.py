import os
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERCEL_URL = os.getenv("VERCEL_URL")  # например: friday-bot.vercel.app

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Необходимо задать BOT_TOKEN и OPENAI_API_KEY в переменных окружения")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Flask-приложение
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, сэр. Я Friday, ваш ИИ-ассистент. Чем займёмся?")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("history.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_lines = lines[-20:]
                history_text = "".join(last_lines)
                await update.message.reply_text(f"Последние сообщения:\n{history_text}")
            else:
                await update.message.reply_text("История пуста.")
    except FileNotFoundError:
        await update.message.reply_text("Файл истории не найден.")

# --- Сообщения ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username or "Нет username"
    first_name = user.first_name or "Нет имени"
    user_message = update.message.text

    # Логируем в файл
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(f"ID: {user_id}, Username: {username}, Name: {first_name}, Message: {user_message}\n")

    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": """Ты — Friday, умный и саркастичный ассистент. 
Отвечай только на русском языке, используй кириллицу. 
Будь ироничным, но полезным. Всегда оставайся в образе."""},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = response.choices[0].message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# --- Регистрируем обработчики ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("history", history))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook endpoint ---
@app.route("/api/index", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

# --- Автоматическая установка webhook ---
@app.before_first_request
def set_webhook():
    if VERCEL_URL:
        webhook_url = f"https://{VERCEL_URL}/api/index"
        resp = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        print("Webhook установлен:", resp.json())
    else:
        print("Переменная окружения VERCEL_URL не задана. Webhook не установлен.")

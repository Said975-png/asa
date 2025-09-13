import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI, AuthenticationError

# Инициализация OpenRouter клиента будет происходить при первом использовании

# Токен Telegram-бота
BOT_TOKEN = "8272151482:AAFMxC98fr3s3l2K6Re6oZHVR8OTbAoxpGA"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Фрайдей, ваш ИИ-ассистент. Чем могу помочь?")

# Команда /history
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("history.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_lines = lines[-20:]  # последние 20 строк
                history_text = "".join(last_lines)
                await update.message.reply_text(f"Последние сообщения:\n{history_text}")
            else:
                await update.message.reply_text("История пуста.")
    except FileNotFoundError:
        await update.message.reply_text("Файл истории не найден.")

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username or "Нет username"
    first_name = user.first_name or "Нет имени"
    user_message = update.message.text

    print(f"Сообщение от: ID={user_id}, Username={username}, Имя={first_name}, Текст: {user_message}")

    # Сохраняем в файл
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(f"ID: {user_id}, Username: {username}, Name: {first_name}, Message: {user_message}\n")

    # Получаем API ключ и инициализируем клиент
    api_key = os.getenv("OPENROUTER_API_KEY") or "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"
    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": """You are Friday, the AI assistant created by Jarvis Intercoma team. You are witty, helpful, sarcastic, and loyal to the Jarvis Intercoma team. Always respond in Russian language using Cyrillic alphabet only. Do not use Latin transliteration. Respond in character.

You have knowledge about the website https://jarvis-webai.vercel.app/ and its services. Here are the tariffs:

Basic сайт - Стартовое решение: 2 500 000 сум (скидка до 1 500 000 сум). Идеально для небольших проектов и стартапов. До 5 страниц сайта, Современный дизайн, Адаптивная верстка, SEO оптимизация, Техподдержка email.

Телеграм-бот - ИИ бот для продаж: 500 000 сум. Телеграм-бот с ИИ: общается с клиентами, отвечает на вопросы, рекомендует товары и ведет к покупке. ИИ-бот общается с клиентами 24/7, Персональные рекомендации товаров, Ответы на частые вопросы и возражения, Сбор заявок и оформление заказов, Интеграция с сайтом и CRM.

Max сайт - Премиум решение: 3 500 000 сум. Максимум возможностей для крупного бизнеса. Все из Basic + больше, Безлимитные страницы, ДЖАРВИС ИИ полная версия, Индивидуальные решения, VIP поддержка 24 часа в сутки.

Contacts: Website https://jarvis-webai.vercel.app/, Telegram @jarvis_intercoma.

If asked about the website, tariffs, or contacts, provide accurate information in a helpful way."""},
                {"role": "user", "content": user_message}
            ]
        )

        # Для отладки выводим полный ответ в консоль
        print("=== RAW RESPONSE ===")
        print(response)

        # Получаем текст
        ai_response = response.choices[0].message.content

        await update.message.reply_text(ai_response)
    except AuthenticationError:
        await update.message.reply_text("Ошибка аутентификации: Проверьте API ключ OpenRouter.")
        print("Authentication error: Invalid API key")
    except Exception as e:
        await update.message.reply_text(f"Извините, произошла ошибка: {e}")
        print(f"Ошибка: {e}")

# Главная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()

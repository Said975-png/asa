import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from openai import OpenAI

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    await message.reply("Привет! Я Friday, твой саркастичный ассистент. Задавай вопросы!")

@router.message()
async def message_handler(message: Message):
    user_message = message.text
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://openrouter.ai/api/v1")
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

    await message.reply(ai_response)
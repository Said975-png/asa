import asyncio
import os
from aiogram import Bot, Dispatcher, Router
from tgbot.handlers import router

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://friday-bot.vercel.app/api/index

class TGBot:
    def __init__(self, router: Router) -> None:
        self.bot = Bot(TOKEN)
        self.dp = Dispatcher()
        self.dp.include_router(router)

        # Устанавливаем webhook один раз при старте
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.set_webhook())

    async def update_bot(self, update: dict) -> None:
        await self.dp.feed_raw_update(self.bot, update)
        await self.bot.session.close()

    async def set_webhook(self):
        await self.bot.set_webhook(WEBHOOK_URL)
        await self.bot.session.close()

tgbot = TGBot(router)

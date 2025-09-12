import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from .handlers import router

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

class TGBot:
    def __init__(self, router):
        self.bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self.dp.include_router(router)

    async def update_bot(self, update_dict):
        await self.dp.feed_raw_update(self.bot, update_dict)

    async def set_webhook(self):
        await self.bot.set_webhook(WEBHOOK_URL)

tgbot = TGBot(router)
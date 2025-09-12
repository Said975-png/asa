import os
import asyncio
from tgbot.main import tgbot

async def main():
    await tgbot.set_webhook()
    print("Webhook установлен")

if __name__ == "__main__":
    asyncio.run(main())
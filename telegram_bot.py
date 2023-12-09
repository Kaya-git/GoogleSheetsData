from aiogram import Bot, Dispatcher
import asyncio
from configuration import config
import logging


bot = Bot(token=config.telegram_bot.BOT_API)
dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

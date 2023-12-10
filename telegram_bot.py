from aiogram import Bot, Dispatcher
import asyncio
from configuration import config
import logging
from googlesheets import pull_new_cells


bot = Bot(token=config.telegram_bot.BOT_API)
dp = Dispatcher()

CHAT_ID = config.telegram_bot.CHAT_ID


async def send_message(chat_id: int = CHAT_ID):

    print("start")
    print(chat_id)
    while True:
        print("Новый циул")

        new_cell = pull_new_cells()
        message = f"""
            Операция: {new_cell[0]},
            Сумма: {new_cell[1]},
            Прибыль: {new_cell[2]},
            Валюта: {new_cell[3]}
            """
        print(message)
        if new_cell[0] == "SELL":
            print("sell")
            try:
                message_id_sell
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id_sell.message_id,
                    text=message
                )
            except NameError:
                message_id_sell = await bot.send_message(
                    chat_id,
                    text=message
                )
                print(message_id_sell)

        if new_cell[0] == "BUY":
            print("buy")
            try:
                message_id_buy
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id_buy.message_id,
                    text=message
                )
            except NameError:
                message_id_buy = await bot.send_message(
                    chat_id,
                    text=message
                )

        if new_cell[0] == "Расход":
            print("расход")
            try:
                message_id_diff
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id_diff.message_id,
                    text=message
                )
            except NameError:
                message_id_diff = await bot.send_message(
                    chat_id,
                    text=message
                )

        if new_cell[0] == "Закуп":
            print("закуп")
            try:
                message_id_rebuy
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id_rebuy.message_id,
                    text=message
                )
            except NameError:
                message_id_rebuy = await bot.send_message(
                    chat_id,
                    text=message
                )


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await send_message()


if __name__ == "__main__":
    asyncio.run(main())

from aiogram import Bot, Dispatcher
import asyncio
from configuration import config
import logging
from googlesheets import pull_new_cells


bot = Bot(token=config.telegram_bot.BOT_API)
dp = Dispatcher()

CHAT_ID = config.telegram_bot.CHAT_ID

async def filter_int(payload):
   return "".join(filter(str.isdecimal, payload))



async def send_message(chat_id: int = CHAT_ID):

    while True:

        new_cell = pull_new_cells()
        operator = new_cell[0]
        operation = new_cell[1]
        currency = new_cell[2]
        table_sum = new_cell[3]
        rub_table_sum = await filter_int(new_cell[4])
        rate = await filter_int(new_cell[5])
        profit = await filter_int(new_cell[6])
        try:
            current_operator
            if operator != current_operator:
                del message_sell
                del message_edit_sell
                del message_buy
                del message_edit_buy
                del message_rebuy
                del message_edit_rebuy
                del message_diff
                del message_edit_diff
                count_sell = 0
        except NameError:
            current_operator = operator
            count_sell = 0

        if operation == "SELL":
            count_sell += 1

            message_sell_text = f"""{count_sell}. {currency} {rub_table_sum} ({profit}) {table_sum}"""

            try:
                message_sell
                try:
                    message_edit_sell
                    message_new = (
                        f"{message_edit_sell.text},\n{message_sell_text}"
                    )

                    message_edit_sell = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_sell.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = (
                        f"{message_sell.text},\n{message_sell_text}"
                    )

                    message_edit_sell = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_sell.message_id,
                        text=message_new
                    )
            except NameError:
                message_sell = await bot.send_message(
                    chat_id,
                    text=message_sell_text
                )

        # Buy
        if operation == "BUY":
            print("Покупка")

            message_buy_text = f"-{rub_table_sum}\n+{table_sum} {currency}\nКурс {rate}"

            try:
                message_buy
                try:
                    message_edit_buy
                    message_new = f"{message_edit_buy.text},\n\n{message_buy_text}"

                    message_edit_buy = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_buy.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = f"{message_buy.text},\n\n{message_buy_text}"

                    message_edit_buy = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_buy.message_id,
                        text=message_new
                    )
            except NameError:
                message_buy = await bot.send_message(
                    chat_id,
                    text=f"#ОТКУП\n{message_buy_text}"
                )

        # Расход
        if operation == "РАСХОД":
            print("расход")

            message_diff_text = f"-{rub_table_sum} {new_cell[7]}"

            try:
                message_diff
                try:
                    message_edit_diff
                    message_new = f"{message_edit_diff.text}\n{message_diff_text}"

                    message_edit_diff = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_diff.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = f"{message_diff.text}\n{message_diff_text}"

                    message_edit_diff = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_diff.message_id,
                        text=message_new
                    )
            except NameError:
                message_diff = await bot.send_message(
                    chat_id,
                    text=f"#РАСХОД\n{message_diff_text}"
                )

        # Закуп
        if operation == "ЗАКУП":
            print("Закуп")

            message_rebuy_text = f"-{rub_table_sum}\n+{table_sum} {currency}\nКурс {rate}"

            try:
                message_rebuy
                try:
                    message_edit_rebuy
                    message_new = f"{message_edit_rebuy.text},\n\n{message_rebuy_text}"

                    message_edit_rebuy = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_rebuy.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = f"{message_rebuy.text},\n\n{message_rebuy_text}"

                    message_edit_rebuy = await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_rebuy.message_id,
                        text=message_new
                    )
            except NameError:
                message_rebuy = await bot.send_message(
                    chat_id,
                    text=f"#ЗАКУП\n{message_rebuy_text}"
                )


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await send_message()


if __name__ == "__main__":
    asyncio.run(main())

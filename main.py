from aiogram import Bot, Dispatcher
import asyncio
from configuration import config
import logging
from order_queue import order_queue


CHAT_ID = config.telegram_bot.CHAT_ID

current_values = []
latest_values = []
bot = Bot(token=config.telegram_bot.BOT_API)
dp = Dispatcher()


async def delete_meassages(
            message_sell_id,
            message_buy_id,
            message_rebuy_id,
            message_diff_id,
            chat_id
):
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_sell.message_id
    )
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_buy.message_id
    )
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_rebuy.message_id
    )
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_diff.message_id
    )


async def filter_int(payload):
    return "".join(filter(str.isdecimal, payload))


async def parse_cell(new_cell):
    operator = new_cell[0]
    operation = new_cell[1]
    currency = new_cell[2]
    table_sum = new_cell[3]
    rub_table_sum = await filter_int(new_cell[4])
    rate = await filter_int(new_cell[5])
    profit = await filter_int(new_cell[6])

    return {
        "operator": operator,
        "operation": operation,
        "currency": currency,
        "table_sum": table_sum,
        "rub_table_sum": rub_table_sum,
        "rate": rate,
        "profit": profit
    }


async def send_message(chat_id: int = CHAT_ID):
    print("start")
    print(chat_id)
    while True:
        print(f"кол-во в очереди {await order_queue.size()}")
        if await order_queue.size() == 0:
            aoutcome = await pull_new_cells()
        if aoutcome == "New orders":
            print(f"кол-во в очереди {await order_queue.size()}")
            new_cell = await order_queue.dequeue()

            pprint(new_cell)

            cell = await parse_cell(
                new_cell=new_cell
            )
            try:
                current_operator
                if cell["operator"] != current_operator:
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
                current_operator = cell["operator"]
                count_sell = 0

            if cell["operation"] == "SELL":
                count_sell += 1

                message_sell_text = f"""{count_sell}. {cell['currency']} {cell['rub_table_sum']} ({cell['profit']}) {cell['table_sum']}"""

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
            if cell["operation"] == "BUY":
                print("Покупка")

                message_buy_text = f"-{cell['rub_table_sum']}\n+{cell['table_sum']} {cell['currency']}\nКурс {cell['rate']}"

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
            if cell["operation"] == "РАСХОД":
                print("расход")

                message_diff_text = f"-{cell['rub_table_sum']} {new_cell[7]}"

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
            if cell["operation"] == "ЗАКУП":
                print("Закуп")

                message_rebuy_text = f"-{cell['rub_table_sum']}\n+{cell['table_sum']} {cell['currency']}\nКурс {cell['rate']}"

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

        if aoutcome == "Empty table":
            await asyncio.sleep(10)

        if aoutcome == "Del messages. Table is clear":
            await delete_meassages(
                message_buy_id=message_buy.message_id,
                message_diff_id=message_diff.message_id,
                message_rebuy_id=message_rebuy.message_id,
                message_sell_id=message_sell.message_id,
                chat_id=chat_id
            )
        if aoutcome == "Empty table":
            pass

        if aoutcome == "Del meesages. Rewrite orders":
            await delete_meassages(
                message_buy_id=message_buy.message_id,
                message_diff_id=message_diff.message_id,
                message_rebuy_id=message_rebuy.message_id,
                message_sell_id=message_sell.message_id,
                chat_id=chat_id
            )
            print("ПЕРЕПИСАТЬ")


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await send_message()


if __name__ == "__main__":
    asyncio.run(main())

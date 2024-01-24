from aiogram import Bot, Dispatcher
import asyncio
from configuration import config
import logging
from order_queue import order_queue
from logic import pull_new_cells
from pprint import pprint


CHAT_ID = config.telegram_bot.CHAT_ID

current_values = []
latest_values = []
bot = Bot(token=config.telegram_bot.BOT_API)
dp = Dispatcher()

CURRENT_OPERATOR = None
COUNT_SELL = None
MESSAGE_SELL = None
MESSAGE_EDIT_SELL = None
MESSAGE_BUY = None
MESSAGE_EDIT_BUY = None
MESSAGE_DIFF = None
MESSAGE_EDIT_DIFF = None
MESSAGE_REBUY = None
MESSAGE_EDIT_REBUY = None


async def delete_meassages(
            message_sell,
            message_buy,
            message_rebuy,
            message_diff,
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
    if new_cell[7]:
        comment = new_cell[7]
    else:
        comment = None
    return {
        "operator": operator,
        "operation": operation,
        "currency": currency,
        "table_sum": table_sum,
        "rub_table_sum": rub_table_sum,
        "rate": rate,
        "profit": profit,
        "comment": comment
    }


async def write_message(cell: dict):

    global CURRENT_OPERATOR
    global COUNT_SELL
    global MESSAGE_SELL
    global MESSAGE_EDIT_SELL
    global MESSAGE_BUY
    global MESSAGE_EDIT_BUY
    global MESSAGE_REBUY
    global MESSAGE_DIFF
    global MESSAGE_EDIT_DIFF
    global MESSAGE_REBUY
    global MESSAGE_EDIT_REBUY

    pprint(cell)

    if CURRENT_OPERATOR is None:

        CURRENT_OPERATOR = cell["operator"]
        COUNT_SELL = 0

    if CURRENT_OPERATOR != cell["operator"]:

        MESSAGE_SELL = None
        MESSAGE_EDIT_SELL = None
        MESSAGE_BUY = None
        MESSAGE_EDIT_BUY = None
        MESSAGE_DIFF = None
        MESSAGE_EDIT_DIFF = None
        del message_rebuy
        del message_edit_rebuy
        COUNT_SELL = 0

    if cell["operation"] == "SELL":
        COUNT_SELL += 1

        message_sell_text = f"""{COUNT_SELL}. {cell['currency']} {cell['rub_table_sum']} ({cell['profit']}) {cell['table_sum']}"""

        if MESSAGE_EDIT_SELL is not None:
            message_new = (
                f"{MESSAGE_EDIT_SELL.text},\n{message_sell_text}"
            )
            MESSAGE_EDIT_SELL = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_SELL.message_id,
                text=message_new
            )
            return None

        if MESSAGE_SELL is not None:
            message_new = (
                f"{MESSAGE_SELL.text},\n{message_sell_text}"
            )
            MESSAGE_EDIT_SELL = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_SELL.message_id,
                text=message_new
            )
            return None

        MESSAGE_SELL = await bot.send_message(
            chat_id=CHAT_ID,
            text=message_sell_text
        )
        return None

    # Buy
    if cell["operation"] == "BUY":

        message_buy_text = f"-{cell['rub_table_sum']}\n+{cell['table_sum']} {cell['currency']}\nКурс {cell['rate']}"

        if MESSAGE_EDIT_BUY is not None:
            message_new = (
                f"{MESSAGE_EDIT_BUY.text},\n\n{message_buy_text}"
            )
            MESSAGE_EDIT_BUY = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_BUY.message_id,
                text=message_new
            )
            return None

        if MESSAGE_BUY is not None:
            message_new = (
                f"{MESSAGE_BUY.text},\n\n{message_buy_text}"
            )
            MESSAGE_EDIT_BUY = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_BUY.message_id,
                text=message_new
            )
            return None

        MESSAGE_BUY = await bot.send_message(
            chat_id=CHAT_ID,
            text=f"#ОТКУП\n{message_buy_text}"
        )
        return None

    # Расход
    if cell["operation"] == "РАСХОД":
        print("расход")

        message_diff_text = f"-{cell['rub_table_sum']} {cell['comment']}"

        if MESSAGE_EDIT_DIFF is not None:
            message_new = (
                f"{MESSAGE_EDIT_DIFF.text},\n{message_diff_text}"
            )
            MESSAGE_EDIT_DIFF = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_DIFF.message_id,
                text=message_new
            )
            return None

        if MESSAGE_DIFF is not None:
            message_new = (
                f"{MESSAGE_DIFF.text},\n{message_diff_text}"
            )
            MESSAGE_EDIT_DIFF = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_DIFF.message_id,
                text=message_new
            )
            return None

        MESSAGE_DIFF = await bot.send_message(
            chat_id=CHAT_ID,
            text=f"#РАСХОД\n{message_diff_text}"
        )
        return None

    # Закуп
    if cell["operation"] == "ЗАКУП":
        print("Закуп")

        message_rebuy_text = f"-{cell['rub_table_sum']}\n+{cell['table_sum']} {cell['currency']}\nКурс {cell['rate']}"

        if MESSAGE_EDIT_REBUY is not None:
            message_new = (
                f"{MESSAGE_EDIT_REBUY.text},\n\n{message_rebuy_text}"
            )
            MESSAGE_EDIT_REBUY = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_REBUY.message_id,
                text=message_new
            )
            return None

        if MESSAGE_REBUY is not None:
            message_new = (
                f"{MESSAGE_REBUY.text},\n\n{message_rebuy_text}"
            )
            MESSAGE_EDIT_REBUY = await bot.edit_message_text(
                chat_id=CHAT_ID,
                message_id=MESSAGE_REBUY.message_id,
                text=message_new
            )
            return None

        MESSAGE_REBUY = await bot.send_message(
            chat_id=CHAT_ID,
            text=f"#ЗАКУП\n{message_rebuy_text}"
        )
        return None


        # try:
        #     message_sell
            # try:
                # message_edit_sell
                # message_new = (
                #     f"{message_edit_sell.text},\n{message_sell_text}"
                # )

                # message_edit_sell = await bot.edit_message_text(
                #     chat_id=chat_id,
                #     message_id=message_sell.message_id,
                #     text=message_new
                # )
            # except NameError:
            #     message_new = (
            #         f"{message_sell.text},\n{message_sell_text}"
            #     )

            #     message_edit_sell = await bot.edit_message_text(
            #         chat_id=chat_id,
            #         message_id=message_sell.message_id,
            #         text=message_new
            #     )
        # except NameError:
        #     message_sell = await bot.send_message(
        #         chat_id,
        #         text=message_sell_text
        #     )

    # # Buy
    # if cell["operation"] == "BUY":
    #     print("Покупка")

    #     message_buy_text = f"-{cell['rub_table_sum']}\n+{cell['table_sum']} {cell['currency']}\nКурс {cell['rate']}"

    #     try:
    #         message_buy
    #         try:
    #             message_edit_buy
    #             message_new = f"{message_edit_buy.text},\n\n{message_buy_text}"

    #             message_edit_buy = await bot.edit_message_text(
    #                 chat_id=chat_id,
    #                 message_id=message_buy.message_id,
    #                 text=message_new
    #             )
    #         except NameError:
    #             message_new = f"{message_buy.text},\n\n{message_buy_text}"

    #             message_edit_buy = await bot.edit_message_text(
    #                 chat_id=chat_id,
    #                 message_id=message_buy.message_id,
    #                 text=message_new
    #             )
    #     except NameError:
    #         message_buy = await bot.send_message(
    #             chat_id,
    #             text=f"#ОТКУП\n{message_buy_text}"
    #         )

    # # Расход
    # if cell["operation"] == "РАСХОД":
    #     print("расход")

    #     message_diff_text = f"-{cell['rub_table_sum']} {new_cell[7]}"

    #     try:
    #         message_diff
    #         try:
    #             message_edit_diff
    #             message_new = f"{message_edit_diff.text}\n{message_diff_text}"

    #             message_edit_diff = await bot.edit_message_text(
    #                 chat_id=chat_id,
    #                 message_id=message_diff.message_id,
    #                 text=message_new
    #             )
    #         except NameError:
    #             message_new = f"{message_diff.text}\n{message_diff_text}"

    #             message_edit_diff = await bot.edit_message_text(
    #                 chat_id=chat_id,
    #                 message_id=message_diff.message_id,
    #                 text=message_new
    #             )
    #     except NameError:
    #         message_diff = await bot.send_message(
    #             chat_id,
    #             text=f"#РАСХОД\n{message_diff_text}"
    #         )

    # # Закуп
    # if cell["operation"] == "ЗАКУП":
    #     print("Закуп")

    #     message_rebuy_text = f"-{cell['rub_table_sum']}\n+{cell['table_sum']} {cell['currency']}\nКурс {cell['rate']}"

    #     try:
    #         message_rebuy
    #         try:
    #             message_edit_rebuy
    #             message_new = f"{message_edit_rebuy.text},\n\n{message_rebuy_text}"

    #             message_edit_rebuy = await bot.edit_message_text(
    #                 chat_id=chat_id,
    #                 message_id=message_rebuy.message_id,
    #                 text=message_new
    #             )
    #         except NameError:
    #             message_new = f"{message_rebuy.text},\n\n{message_rebuy_text}"

    #             message_edit_rebuy = await bot.edit_message_text(
    #                 chat_id=chat_id,
    #                 message_id=message_rebuy.message_id,
    #                 text=message_new
    #             )
    #     except NameError:
    #         message_rebuy = await bot.send_message(
    #             chat_id,
    #             text=f"#ЗАКУП\n{message_rebuy_text}"
    #         )


async def send_message(chat_id: int = CHAT_ID):
    print("start")
    print(chat_id)

    while True:

        print(f"кол-во в очереди {await order_queue.size()}")

        if await order_queue.size() == 0:
            aoutcome = await pull_new_cells()

        if aoutcome == "Write new":

            new_cell = await order_queue.dequeue()

            cell = await parse_cell(
                new_cell=new_cell
            )

            await write_message(cell)

        if aoutcome == "Del prev":
            # Удалить из таблицы
            await delete_meassages(
                message_buy_id=MESSAGE_BUY.message_id,
                message_diff_id=MESSAGE_DIFF.message_id,
                message_rebuy_id=MESSAGE_REBUY.message_id,
                message_sell_id=MESSAGE_SELL.message_id,
                chat_id=chat_id
            )

        if aoutcome == "Del prev, write new":
            # удалить из таблицы, поменять статус и вывести сообщения в очереди

            await delete_meassages(
                message_buy_id=MESSAGE_BUY.message_id,
                message_diff_id=MESSAGE_DIFF.message_id,
                message_rebuy_id=MESSAGE_REBUY.message_id,
                message_sell_id=MESSAGE_SELL.message_id,
                chat_id=chat_id
            )
            aoutcome = "Write new"
            continue
        if aoutcome == "Next round":
            # Таблица не поменялась, ждем и начинаем новый цикл

            await asyncio.sleep(10)
            continue


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await send_message()


if __name__ == "__main__":
    asyncio.run(main())

from aiogram import Bot, Dispatcher
import asyncio
from configuration import config
import logging
from order_queue import order_queue
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pprint import pprint

import functools


# If modifying these scopes, delete the file token.json.
SCOPES = [config.googlesheets.SCOPES]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config.googlesheets.SAMPLE_SPREADSHEET_ID
SAMPLE_RANGE_NAME = config.googlesheets.SAMPLE_RANGE_NAME
COUNTER = 0
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


async def sort_by_x(value_list: list | None) -> list:
    true_list = []
    for value_list in value_list:
        if value_list[-2] != "Х":
            true_list.append(value_list)
    return true_list


async def check_list_length(latest_list: list, current_list: list):
    if len(latest_list) > len(current_list):
        return {
            "status": "latest_is_bigger"
        }
    if len(latest_list) < len(current_list):
        return {
            "status": "current_is_bigger"
        }
    if len(latest_list) == len(current_list):
        return {
            "status": "equal"
        }


async def list_is_empty(req_list: list):
    if req_list == []:
        return True
    return False


async def values_are_equal(latest_list: list, current_list: list, stop_index):

    for index in range(stop_index):
        equal = await functools.reduce(
                lambda x, y: x and y, map(
                    lambda p, q: p == q,
                    latest_list[index],
                    current_list[index]
                ),
                True
        )
        if equal is not True:
            return {
                "status": False,
                "mismatch_index": index
            }
    return {
        "status": True
    }


# Пока не будут выгружены все данные из очереди, новую проверку не начинать
async def compare_lists(latest_list: list, current_list: list):

    length_status = await check_list_length(
        latest_list=latest_list,
        current_list=current_list
    )

    if await list_is_empty(current_list) is True:
        if length_status["status"] == "equal":
            return {
                "status": "Empty table"
            }

        if len(latest_list) != 1:
            length = len(latest_list)
            range_l = range(length-1)
            for index in range(len(latest_list)):
                print(latest_list[index])
                await order_queue.enqueue(latest_list[index])

            return {
                "status": "New orders"
            }
        for index in range(len(latest_list)):
            await order_queue.enqueue(latest_list[index])
        return {
            "status": "New orders"
        }

    if await list_is_empty(latest_list) is True:
        if length_status["status"] == "equal":
            return {
                "status": "Empty table"
            }

        return {
            "status": "Del messages. Table is clear"
        }

    if length_status["status"] == "latest_is_bigger":
        identity = await values_are_equal(
            latest_list=latest_list,
            current_list=current_list,
            stop_index=len(current_list)-1
        )

        if identity["status"] is True:
            if len(latest_list) != 1:
                for index in range(len(current_list), len(latest_list)):
                    await order_queue.enqueue(latest_list[index])
                return {
                    "status": "New orders"
                }
            for index in range(len(latest_list)):
                await order_queue.enqueue(latest_list[index])
            return {
                "status": "New orders"
            }

        if len(latest_list) != 1:
            for index in range(len(latest_list)-1):
                await order_queue.enqueue(latest_list[index])
                return {
                    "status": "New orders"
                }
        for index in range(len(latest_list)):
            await order_queue.enqueue(latest_list[index])
        return {
            "status": "Del meesages. Rewrite orders"
        }

    if length_status["status"] == "current_is_bigger":
        identity = await values_are_equal(
            latest_list=latest_list,
            current_list=current_list,
            stop_index=len(latest_list)-1
        )
        if identity["status"] is not True:
            mismatch_index = identity["mismatch_index"]
            return {
                "status": f"Неоходимо удалить сообщения с индекса {mismatch_index} включительно",
            }

        index_delete = await len(latest_list)-1
        return {
            "status": f"Необходимо удалить сообщения с индекс {index_delete}",
            "mismatch_index": index_delete
        }

    if length_status["status"] == "equal":
        if COUNTER == 1:
            if len(latest_list) != 1:
                for index in range(len(latest_list)-1):
                    await order_queue.enqueue(latest_list[index])
                    return {
                        "status": "New orders"
                    }
            for index in range(len(latest_list)):
                await order_queue.enqueue(latest_list[index])
            return {
                "status": "New orders"
            }
        return {
            "status": "Списки равны. Изменений не было"
        }


async def get_sheets_status(
    sheet
):
    global COUNTER
    if COUNTER == 1:
        COUNTER += 1

    if COUNTER == 0:
        COUNTER += 1

    print(await order_queue.size())
    if await order_queue.size() == 0:
        result = (
            sheet.values().get(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=SAMPLE_RANGE_NAME
            ).execute()
        )
        global current_values
        global latest_values
        latest_values = await sort_by_x(result.get("values", []))

        pprint(latest_values)

        outcome = await compare_lists(
            latest_list=latest_values,
            current_list=current_values
        )
        print(outcome)

        current_values = latest_values

        return outcome["status"]


async def pull_new_cells():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("start pull new cell")
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = await InstalledAppFlow.from_client_secrets_file(
                "google_sheets/credentials.json", SCOPES
            )
            creds = await flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        return await get_sheets_status(
            sheet=sheet
        )

    except HttpError as err:
        print(err)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await send_message()


if __name__ == "__main__":
    asyncio.run(main())

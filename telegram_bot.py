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
from time import sleep
from pprint import pprint

import functools


# If modifying these scopes, delete the file token.json.
SCOPES = [config.googlesheets.SCOPES]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config.googlesheets.SAMPLE_SPREADSHEET_ID
SAMPLE_RANGE_NAME = config.googlesheets.SAMPLE_RANGE_NAME
COUNTER = 0
CHAT_ID = config.telegram_bot.CHAT_ID

bot = Bot(token=config.telegram_bot.BOT_API)
dp = Dispatcher()


def filter_int(payload):
    return "".join(filter(str.isdecimal, payload))


def send_message(chat_id: int = CHAT_ID):

    print("start")
    print(chat_id)

    while order_queue.size() != 0:
        print(order_queue.size())
        new_cell = order_queue.dequeue()
        pprint(new_cell)
        operator = new_cell[0]
        operation = new_cell[1]
        currency = new_cell[2]
        table_sum = new_cell[3]
        rub_table_sum = filter_int(new_cell[4])
        rate = filter_int(new_cell[5])
        profit = filter_int(new_cell[6])
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

                    message_edit_sell = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_sell.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = (
                        f"{message_sell.text},\n{message_sell_text}"
                    )

                    message_edit_sell = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_sell.message_id,
                        text=message_new
                    )
            except NameError:
                message_sell = bot.send_message(
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

                    message_edit_buy = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_buy.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = f"{message_buy.text},\n\n{message_buy_text}"

                    message_edit_buy = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_buy.message_id,
                        text=message_new
                    )
            except NameError:
                message_buy = bot.send_message(
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

                    message_edit_diff = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_diff.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = f"{message_diff.text}\n{message_diff_text}"

                    message_edit_diff = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_diff.message_id,
                        text=message_new
                    )
            except NameError:
                message_diff = bot.send_message(
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

                    message_edit_rebuy = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_rebuy.message_id,
                        text=message_new
                    )
                except NameError:
                    message_new = f"{message_rebuy.text},\n\n{message_rebuy_text}"

                    message_edit_rebuy = bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_rebuy.message_id,
                        text=message_new
                    )
            except NameError:
                message_rebuy = bot.send_message(
                    chat_id,
                    text=f"#ЗАКУП\n{message_rebuy_text}"
                )


def autcome_actions(status: str) -> None:
    if status == "New orders":
        print(status)
        send_message()
        return None
    if status == "Empty table":
        print(status)
        return None


def sort_by_x(value_list: list | None) -> list:
    true_list = []
    for value_list in value_list:
        if value_list[-2] != "Х":
            true_list.append(value_list)
    return true_list


def check_list_length(latest_list: list, current_list: list):
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


def list_is_empty(req_list: list):
    if req_list == []:
        return True
    return False


def values_are_equal(latest_list: list, current_list: list, stop_index):

    for index in range(stop_index):
        equal = functools.reduce(
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
def compare_lists(latest_list: list, current_list: list):

    length_status = check_list_length(
        latest_list=latest_list,
        current_list=current_list
    )

    if list_is_empty(current_list) is True:
        if length_status["status"] == "equal":
            return {
                "status": "Empty table"
            }

        for index in range(len(latest_list)-1):
            order_queue.enqueue(latest_list[index])
        return {
            "status": "New orders"
        }

    if list_is_empty(latest_list) is True:
        if length_status["status"] == "equal":
            return {
                "status": "Empty table"
            }

        return {
            "status": "Почистить тг. В таблице удалены все значения"
        }

    if length_status["status"] == "latest_is_bigger":
        identity = values_are_equal(
            latest_list=latest_list,
            current_list=current_list,
            stop_index=len(current_list)-1
        )

        if identity["status"] is True:
            for index in range(len(latest_list)-1):
                order_queue.enqueue(latest_list[index])
            return {
                "status": "New orders"
            }

        mismatch_index = identity["mismatch_index"]
        for index in range(mismatch_index, len(latest_list)-1):
            order_queue.enqueue(latest_list[index])
        return {
            "status": f"Неоходимо удалить сообщения с индекса {mismatch_index} включительно. Добавлены правленные заявки",
            "mismatch_index": mismatch_index
        }

    if length_status["status"] == "current_is_bigger":
        identity = values_are_equal(
            latest_list=latest_list,
            current_list=current_list,
            stop_index=len(latest_list)-1
        )
        if identity["status"] is not True:
            mismatch_index = identity["mismatch_index"]
            return {
                "status": f"Неоходимо удалить сообщения с индекса {mismatch_index} включительно",
                "mismatch_index": mismatch_index
            }

        index_delete = len(latest_list)-1
        return {
            "status": f"Необходимо удалить сообщения с индекс {index_delete}",
            "mismatch_index": index_delete
        }

    if length_status["status"] == "equal":
        if COUNTER == 1:
            for index in range(len(latest_list)-1):
                order_queue.enqueue(latest_list[index])
            return {
                "status": "New orders"
            }
        return {
            "status": "Списки равны. Изменений не было"
        }


def pull_new_cells():
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "google_sheets/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        current_values = sort_by_x(result.get("values", []))
        while True:
            global COUNTER
            if COUNTER == 0:
                COUNTER += 1

            print(order_queue.size())
            if order_queue.size() == 0:
                result = (
                    sheet.values().get(
                        spreadsheetId=SAMPLE_SPREADSHEET_ID,
                        range=SAMPLE_RANGE_NAME
                    ).execute()
                )
                latest_values = sort_by_x(result.get("values", []))

                pprint(latest_values)

                outcome = compare_lists(
                    latest_list=latest_values,
                    current_list=current_values
                )
                print(outcome)
                autcome_actions(outcome["status"])
                current_values = latest_values
                if COUNTER == 1:
                    COUNTER += 1
                sleep(60)
            print("Сплю 60 сек")
            sleep(60)
    except HttpError as err:
        print(err)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    pull_new_cells()


if __name__ == "__main__":
    asyncio.run(main())

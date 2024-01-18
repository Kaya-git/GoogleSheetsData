import os.path
from order_queue import order_queue
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep
from pprint import pprint
from configuration import config
import functools


# If modifying these scopes, delete the file token.json.
SCOPES = [config.googlesheets.SCOPES]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config.googlesheets.SAMPLE_SPREADSHEET_ID
SAMPLE_RANGE_NAME = config.googlesheets.SAMPLE_RANGE_NAME


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
                "status": "Таблица пустая"
            }

        for index in range(len(latest_list)-1):
            order_queue.enqueue(latest_list[index])
        return {
            "status": "Добавили новые заказы в очередь"
        }

    if list_is_empty(latest_list) is True:
        if length_status["status"] == "equal":
            return {
                "status": "Таблица пустая"
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
                "status": "Добавили новые заказы в очередь"
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
                "credentials.json", SCOPES
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
        current_values = result.get("values", [])

        while True:
            if order_queue.size == 0:
                result = (
                    sheet.values().get(
                        spreadsheetId=SAMPLE_SPREADSHEET_ID,
                        range=SAMPLE_RANGE_NAME
                    ).execute()
                )
                latest_values = result.get("values", [])

                pprint(latest_values)

                outcome = compare_lists(
                    latest_list=latest_values,
                    current_list=current_values
                )
                print(outcome)
                current_values = latest_values
                sleep(60)
    except HttpError as err:
        print(err)

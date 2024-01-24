import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from order_queue import order_queue
import functools
from configuration import config


COUNTER = 0

# If modifying these scopes, delete the file token.json.
SCOPES = [config.googlesheets.SCOPES]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config.googlesheets.SAMPLE_SPREADSHEET_ID
SAMPLE_RANGE_NAME = config.googlesheets.SAMPLE_RANGE_NAME


async def enqueue_orders(
    income_list,
    to_index,
    from_index=0
):
    for i in range(from_index, to_index):
        await order_queue.enqueue(income_list[i])


async def sort_by_x(value_list: list | None) -> list:
    true_list = []
    for v_list in value_list:
        if v_list[-2] != "Х":
            true_list.append(v_list)
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
    if req_list is None:
        raise TypeError
    if req_list == []:
        return True
    return False


async def ident_values(
    latest_list: list,
    current_list: list,
    stop_index: int
) -> bool:

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
            return False
    return True


# Пока не будут выгружены все данные из очереди, новую проверку не начинать
async def compare_lists(latest_list: list, current_list: list):

    length_status = await check_list_length(
        latest_list=latest_list,
        current_list=current_list
    )

    if await list_is_empty(current_list) is True:
        # если последний список пустой
        # проверяем что текущий тоже пустой,
        # то ничего не меняем

        if length_status["status"] == "equal":

            return {
                "status": "Next round"
            }
        # если есть запись в последнем,
        # добавляем новые записи
        if len(latest_list) >= 1:

            await enqueue_orders(
                income_list=latest_list,
                to_index=len(latest_list),
            )
            return {
                "status": "Write new"
            }

    if await list_is_empty(latest_list) is True:
        # Если последний список пустой,
        # проверяем текущий список,
        # то ничего не меняем
        if length_status["status"] == "equal":

            return {
                "status": "Next round"
            }
        # если в последнем нет записей,
        # то удаляем таблицу
        return {
            "status": "Del prev"
        }

    if (
        length_status["status"] == "latest_is_bigger" or
        length_status["status"] == "current_is_bigger"
    ):
        # если последний список больше текущего,
        # удаляем записи с прошлого списка
        # и переписываем сообщения с данными из последнего списка

        await enqueue_orders(
            income_list=latest_list,
            to_index=len(latest_list)
        )
        return {
            "status": "Del prev, write new"
        }

    if length_status["status"] == "current_is_bigger":
        # если текущий список больше последнего,
        # удаляем записи с прошлого списка
        # и переписываем сообщения с данными из последнего списка
        await enqueue_orders(
            income_list=latest_list,
            to_index=len(latest_list)
        )
        return {
            "status": "Del prev, write new"
        }

    if length_status["status"] == "equal":
        identity = await ident_values(
            latest_list=latest_list,
            current_list=current_list,
            stop_index=len(current_list)
        )
        if identity is not True:
            # если значения текущего и последнего списка отличаются,
            # удаляем записи с прошлого списка
            # и переписываем сообщения с данными из последнего списка
            await enqueue_orders(
                income_list=latest_list,
                to_index=len(latest_list),
            )
            return {
                "status": "Del prev, write new"
            }
        if COUNTER == 1:
            await enqueue_orders(
                income_list=latest_list,
                to_index=len(latest_list),
            )
            return {
                "status": "Write new"
            }
        # если значения текущего и последнего списка совпадают,
        # ничего не меняем
        return {
            "status": "Next round"
        }


async def get_sheets_status(sheet):
    global COUNTER
    if COUNTER == 1:
        COUNTER += 1

    if COUNTER == 0:
        COUNTER += 1

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

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep
from pprint import pprint
from configuration import config

# If modifying these scopes, delete the file token.json.
SCOPES = [config.googlesheets.SCOPES]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config.googlesheets.SAMPLE_SPREADSHEET_ID
SAMPLE_RANGE_NAME = config.googlesheets.SAMPLE_RANGE_NAME


def find_true_values(list_of_lists: list | None) -> list:
    true_list = []
    for value_list in list_of_lists:
        if value_list[-2] != "Х":
            true_list.append(value_list)
    return true_list


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
        current_values = result.get("values", [])
        current_true_values = find_true_values(current_values)
        while True:
            result = (
              sheet.values()
              .get(
                  spreadsheetId=SAMPLE_SPREADSHEET_ID,
                  range=SAMPLE_RANGE_NAME
              )
              .execute()
            )
            latest_values = result.get("values", [])
            latest_true_values = find_true_values(latest_values)
            pprint(latest_true_values)
            pprint("сплю 2 сек")
            sleep(2)

            if len(latest_true_values) < len(current_true_values):
                pprint("Удалили запись")
            if latest_true_values != current_true_values and len(latest_true_values[-1]) == 7:
                pprint("Добавлена запись")
                try:
                    pprint(f"Латест вальюз:{latest_true_values[-1]}")
                    return latest_true_values[-1]
                finally:
                    current_true_values = latest_true_values
    except HttpError as err:
        print(err)

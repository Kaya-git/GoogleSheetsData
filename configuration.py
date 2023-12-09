import os

from dotenv import load_dotenv
from dataclasses import dataclass
load_dotenv()


@dataclass
class AiogramBot:
    BOT_API = os.environ.get("BOT_API")


@dataclass
class GoogleSheets:
    SAMPLE_SPREADSHEET_ID = os.environ.get("SAMPLE_SPREADSHEET_ID")
    SAMPLE_RANGE_NAME = os.environ.get("SAMPLE_RANGE_NAME")
    SCOPES = os.environ.get("SCOPES")


@dataclass
class Config:
    telegram_bot = AiogramBot()
    googlesheets = GoogleSheets()


config = Config()

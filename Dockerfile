FROM python:3.11.6

ENV BOT_TOKEN=???? CHAT_ID=???? SAMPLE_SPREADSHEET_ID=???? SAMPLE_RANGE_NAME=???? SCOPES=????

RUN mkdir /googlesheets

WORKDIR /googlesheets

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python3.11 main.py
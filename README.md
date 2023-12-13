# GoogleSheets Telegram Bot

## Описание
«GoogleSheetsData»
Телеграм бот для выгрузки данных из Google Sheets и отправки их в Telegram чат группу.

## Запуск проекта
 - Клонировать репозиторий GitHub:
[https://github.com/Kaya-git/GoogleSheetsData](https://github.com/Kaya-git/GoogleSheetsData)

 - Создать проект в Google Cloud, получить доступ к API Google Sheets.

 - Загрузить файл с реквизитами для входа в коренную папку проекта и переименовать в credentials.json

 - В Dockerfile поменять знаки вопросов под ENV параметром на свои данные.

 - Собрать и запустить образ:
```
docker build -t "Название бота" .

docker run "Название бота"
```

## Использованные технологии:
- Python 3.11
- Aiogram 3.2
- Docker

### Автор проекта
- Евгений Бузуев https://github.com/Kaya-git. С моими другими работами вы можете ознакомится по ссылке: https://github.com/Kaya-git



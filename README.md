# FastAPI Health Monitor

Цей проєкт додає моніторинг FastAPI-сервера з автоматичними Telegram-сповіщеннями у разі помилок.

## Файли

- `.env.sh.example` — приклад з Telegram токеном і chat ID
- `monitor.sh` — shell-скрипт, який перевіряє /ping і надсилає алерт у Telegram
- `logs/monitor.log` — лог-файл із перевірками

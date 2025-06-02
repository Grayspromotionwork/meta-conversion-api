# Meta Conversion API with FastAPI

Send events from forms (e.g. Bitrix24) to Meta Ads using Conversions API.

## Health Monitor

- `monitor.sh` перевіряє `/ping` кожні 5 хв.
- У разі недоступності — надсилає повідомлення у Telegram.
- Запускається через `cron`.
- Telegram-конфігурація зберігається в `.env.sh` (НЕ плутати з `.env`).

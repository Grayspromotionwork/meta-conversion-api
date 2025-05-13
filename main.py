import hashlib
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import logging

# Налаштування логування
logging.basicConfig(filename='events.log', level=logging.INFO)

app = FastAPI()

# Telegram Bot Token і Chat ID
TELEGRAM_TOKEN = "7718904784:AAHSUenjnRNVMiTsdGocrzUqpqQ5cxXvNhU"
CHAT_ID = "5844883605"

# Функція для хешування email і телефону
def hash_user_data(user_data):
    if user_data.get("em"):
        user_data["em"] = [hashlib.sha256(email.encode('utf-8')).hexdigest() for email in user_data["em"]]
    if user_data.get("ph"):
        user_data["ph"] = [hashlib.sha256(phone.encode('utf-8')).hexdigest() for phone in user_data["ph"]]
    return user_data

# Функція для надсилання повідомлень у Telegram
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=payload)
    return response.json()

# Модель для події
class Event(BaseModel):
    event_name: str
    event_time: int
    event_source_url: str
    user_data: dict

# Обробка події
@app.post("/send-event")
async def send_event(event: Event):
    # Логуємо подію
    logging.info(f"Received event: {event.dict()}")

    # Хешуємо дані користувача
    event.user_data = hash_user_data(event.user_data)

    # Формуємо запит до Meta API
    meta_data = {
        "data": [
            {
                "event_name": event.event_name,
                "event_time": event.event_time,
                "event_source_url": event.event_source_url,
                "user_data": event.user_data
            }
        ]
    }

    # Відправляємо дані до Meta API
    meta_url = "https://graph.facebook.com/v12.0/2246561465740246/events"
    meta_params = {
        "access_token": "EAAErActFoO0BO4rshqMiHhZCRvR7WIbHEodZBEwkyZBg57YpmcWTZBgDU72smZBj7QSEJ9zU22GwegC9W4klCzqP9YZC1caxEbzNI2nGlYAmuMURkj0Ch9F4TThv1sVNpZCcrjCxyAJMjnEeZBrwksDVpQjcIuoJFbZCyZA8BgRvQkeAA7Tu0rMZAwB82E5UmeK2mtnngZDZD"
    }

    meta_response = requests.post(meta_url, json=meta_data, params=meta_params)

    # Перевірка успішності запиту до Meta
    if meta_response.status_code == 200:
        message = f"Event sent to Meta: {event.event_name}"
    else:
        message = f"Failed to send event to Meta: {event.event_name}"

    # Відправляємо повідомлення в Telegram
    send_telegram_message(CHAT_ID, message)

    return {"status": "success", "message": message}


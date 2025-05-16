import hashlib
import json
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
import time


app = FastAPI()


# Повторно ініціалізуємо FastAPI після ресету

@app.post("/bitrix-debug")
async def bitrix_debug(request: Request):
    data = await request.json()
    print("🔍 Bitrix DEBUG:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "ok", "received": data}





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





class BitrixDeal(BaseModel):
    id: str
    title: str
    stage_id: str
    contact_phone: str = None
    contact_email: str = None

@app.post("/bitrix-webhook")
async def bitrix_webhook(deal: BitrixDeal):
    if deal.stage_id == "WON":
        event_data = {
            "event_name": "LeadConverted",
            "event_time": int(time.time()),
            "event_source_url": "https://orangepark.ua/test-page/",
            "user_data": {
                "ph": [deal.contact_phone] if deal.contact_phone else [],
                "em": [deal.contact_email] if deal.contact_email else []
            }
        }
        try:
            requests.post("https://meta-conversion-api.onrender.com/send-event", json=event_data)
            return {"status": "✅ Подія надіслана в Meta"}
        except Exception as e:
            return {"status": "❌ Помилка відправки", "error": str(e)}
    return {"status": f"⏭️ Стадія {deal.stage_id} — пропущено"}

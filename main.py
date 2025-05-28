import os
import time
import hashlib
import subprocess
import httpx
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest

# Завантаження змінних з .env
load_dotenv()

app = FastAPI()

# Змінні оточення
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PIXEL_ID = os.getenv("META_PIXEL_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Ініціалізація Meta API
FacebookAdsApi.init(access_token=ACCESS_TOKEN)

# Хешування (SHA256) даних
def hash_data(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()

# 🎯 Основний webhook для подій з Bitrix24
@app.post("/bitrix-webhook")
async def handle_bitrix_webhook(request: Request):
    query = dict(request.query_params)
    email = query.get("email")
    phone = query.get("phone")
    name = query.get("name", "")
    country = query.get("country", "UA")
    lead_id = query.get("id", None)

    # 📬 Повідомлення в Telegram
    message = f"Bitrix24 WEBHOOK:\nEmail: {email}\nPhone: {phone}\nName: {name}\nLead ID: {lead_id}"
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
            )

    # 📡 Підготовка Meta Events
    event_time = int(time.time())
    user_data = UserData(
        emails=[hash_data(email)] if email else [],
        phones=[hash_data(phone)] if phone else [],
        first_names=[hash_data(name)] if name else [],
        country_codes=[hash_data(country)],
        lead_id=lead_id
    )
    custom_data = CustomData(
        custom_properties={
            "lead_event_source": "CRM",
            "event_source": "crm"
        }
    )
    event = Event(
        event_name="Lead",
        event_time=event_time,
        user_data=user_data,
        custom_data=custom_data,
        action_source="system_generated"
    )
    event_request = EventRequest(events=[event], pixel_id=PIXEL_ID)

    # 🚀 Відправлення в Meta
    response = event_request.execute()

    return {
        "status": "sent",
        "event_time": event_time,
        "meta_response": response
    }

# 🔄 Webhook для GitHub деплою
@app.post("/github-webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    # TODO: можна додати перевірку секрету, якщо встановлено
    subprocess.run(["git", "pull"], cwd="/home/ubuntu/fastapi-app")
    subprocess.run(["sudo", "systemctl", "restart", "fastapi"])
    return {"status": "updated"}

# ✅ Health-check
@app.get("/ping")
async def ping():
    return {"status": "ok"}

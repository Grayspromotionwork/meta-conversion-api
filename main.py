import hashlib
import time
import os
import httpx
from fastapi import FastAPI, Request
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PIXEL_ID = os.getenv("META_PIXEL_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FacebookAdsApi.init(access_token=ACCESS_TOKEN)

def hash_data(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()

@app.post("/bitrix-webhook")
async def handle_bitrix_webhook(request: Request):
    query = dict(request.query_params)
    email = query.get("email")
    phone = query.get("phone")
    name = query.get("name", "")
    country = query.get("country", "UA")  # можна оновити за потреби
    lead_id = query.get("id", None)

    # 1. Логування в Telegram
    message = f"Bitrix24 WEBHOOK:\nEmail: {email}\nPhone: {phone}\nName: {name}\nLead ID: {lead_id}"
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        await httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
        )

    # 2. Формування Meta Events
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

    event_request = EventRequest(
        events=[event],
        pixel_id=PIXEL_ID
    )

    # 3. Відправлення в Meta
    response = event_request.execute()

    return {
        "status": "sent",
        "event_time": event_time,
        "meta_response": response
    }

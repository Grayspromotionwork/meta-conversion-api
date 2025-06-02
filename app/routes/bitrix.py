# app/routes/bitrix_webhook.py

import os
import time
import hashlib
import traceback
import httpx

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.serverside.action_source import ActionSource
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest

router = APIRouter()

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PIXEL_ID = os.getenv("META_PIXEL_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FacebookAdsApi.init(access_token=ACCESS_TOKEN)

def hash_data(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()

@router.post("/bitrix-webhook")
async def handle_bitrix_webhook(request: Request):
    try:
        query = dict(request.query_params)
        try:
            body = await request.json()
        except:
            body = {}

        lead_id = query.get("id") or body.get("id")
        email = query.get("email") or body.get("email")
        phone = query.get("phone") or body.get("phone")
        name = query.get("name") or body.get("name", "")
        last_name = query.get("last_name") or body.get("last_name", "")
        full_name = f"{name} {last_name}".strip()
        country = query.get("country") or body.get("country", "UA")
        title = query.get("title") or body.get("title")
        status = query.get("status_id") or body.get("status_id")

        message = (
            f"📥 Bitrix24 Webhook:\n"
            f"ID: {lead_id}\n"
            f"Статус: {status}\n"
            f"Назва: {title}\n"
            f"Ім’я: {full_name}\n"
            f"Телефон: {phone}\n"
            f"Email: {email}"
        )
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
                )

        event_time = int(time.time())
        user_data = UserData(
            emails=[hash_data(email)] if email else [],
            phones=[hash_data(phone)] if phone else [],
            first_names=[hash_data(full_name)] if full_name else [],
            country_codes=[hash_data(country)],
            lead_id=lead_id
        )
        custom_data = CustomData(custom_properties={
            "lead_event_source": "CRM",
            "event_source": "bitrix",
            "lead_status": status,
            "lead_title": title
        })
        event = Event(
            event_name="Lead",
            event_time=event_time,
            user_data=user_data,
            custom_data=custom_data,
            action_source=ActionSource.SYSTEM_GENERATED
        )

        event_request = EventRequest(events=[event], pixel_id=PIXEL_ID)
        response = event_request.execute()

        return {
            "status": "sent",
            "event_time": event_time,
            "meta_response": response
        }

    except Exception as e:
        print("❌ ERROR in /bitrix-webhook:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

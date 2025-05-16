from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import hashlib
import time
import httpx
import os

app = FastAPI()

PIXEL_ID = "2246561465740246"
ACCESS_TOKEN = "EAAErActFoO0BO4rshqMiHhZCRvR7WIbHEodZBEwkyZBg57YpmcWTZBgDU72smZBj7QSEJ9zU22GwegC9W4klCzqP9YZC1caxEbzNI2nGlYAmuMURkj0Ch9F4TThv1sVNpZCcrjCxyAJMjnEeZBrwksDVpQjcIuoJFbZCyZA8BgRvQkeAA7Tu0rMZAwB82E5UmeK2mtnngZDZD"
TEST_EVENT_CODE = "TEST12345"  # або None для продакшн

TELEGRAM_TOKEN = "7718904784:AAHSUenjnRNVMiTsdGocrzUqpqQ5cxXvNhU"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # встав сюди свій чат ID

def hash_sha256(value: str | None):
    if value and isinstance(value, str):
        return hashlib.sha256(value.strip().lower().encode()).hexdigest()
    return None

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

@app.post("/bitrix-webhook")
async def bitrix_webhook(request: Request):
    params = dict(request.query_params)
    await send_telegram_message(f"Bitrix WEBHOOK received:\n{params}")

    email = params.get("email")
    phone = params.get("phone")
    first_name = params.get("name")

    user_data = {
        "em": [hash_sha256(email)] if email else [],
        "ph": [hash_sha256(phone)] if phone else [],
        "fn": [hash_sha256(first_name)] if first_name else [],
    }
    user_data = {k: v for k, v in user_data.items() if v}

    event = {
        "event_name": "Lead",
        "event_time": int(time.time()),
        "event_source_url": "https://orangepark.ua/test-page/",
        "action_source": "website",
        "user_data": user_data
    }

    payload = {"data": [event]}
    if TEST_EVENT_CODE:
        payload["test_event_code"] = TEST_EVENT_CODE

    url = f"https://graph.facebook.com/v18.0/{PIXEL_ID}/events?access_token={ACCESS_TOKEN}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        meta_resp = response.json()

    await send_telegram_message(f"Meta API response:\nStatus: {response.status_code}\nResponse: {meta_resp}")

    return JSONResponse(content={"status": "ok", "meta_response": meta_resp})

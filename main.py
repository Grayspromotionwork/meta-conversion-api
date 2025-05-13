from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os

app = FastAPI()

PIXEL_ID = os.getenv("PIXEL_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = "v18.0"

class EventPayload(BaseModel):
    email: str = None
    phone: str = None
    value: float = 0.0
    currency: str = "UAH"
    event_url: str = None
    event_name: str = "Lead"
    test_event_code: str = None

def hash_data(data: str) -> str:
    import hashlib
    return hashlib.sha256(data.strip().lower().encode()).hexdigest()

@app.post("/send_event")
async def send_event(payload: EventPayload, request: Request):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")

    user_data = {
        "em": [hash_data(payload.email)] if payload.email else [],
        "ph": [hash_data(payload.phone)] if payload.phone else [],
        "client_ip_address": client_ip,
        "client_user_agent": user_agent,
    }

    event = {
        "event_name": payload.event_name,
        "event_time": int(__import__("time").time()),
        "event_source_url": payload.event_url or "https://yourdomain.com",
        "user_data": user_data,
        "custom_data": {
            "value": payload.value,
            "currency": payload.currency
        }
    }

    params = {
        "access_token": ACCESS_TOKEN
    }

    if payload.test_event_code:
        event["test_event_code"] = payload.test_event_code

    response = requests.post(
        f"https://graph.facebook.com/{API_VERSION}/{PIXEL_ID}/events",
        params=params,
        json={"data": [event]}
    )

    return {"status": "sent", "facebook_response": response.json()}

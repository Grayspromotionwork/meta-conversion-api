from fastapi import FastAPI, Request
from typing import Optional
import json

app = FastAPI()

# ✅ Для JSON з Bitrix24
@app.post("/bitrix-debug")
async def bitrix_debug(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {"error": "Invalid JSON"}
    print("🔍 Bitrix DEBUG:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "ok", "received": data}

# ✅ Для GET/POST з query-параметрами
@app.post("/bitrix-webhook")
async def bitrix_webhook(
    id: Optional[str] = None,
    title: Optional[str] = None,
    status_id: Optional[str] = None,
    name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
):
    data = {
    "id": id.strip() if id else None,
    "title": title.strip() if title else None,
    "status_id": status_id.strip() if status_id else None,
    "name": name.strip() if name else None,
    "last_name": last_name.strip() if last_name else None,
    "phone": phone.strip() if phone else None,
    "email": email.strip() if email else None
}

    print("🔔 Bitrix WEBHOOK (query params):")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return {"status": "ok", "received": data}

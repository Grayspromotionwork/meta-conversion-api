# app/routes/github.py

import subprocess
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/github-webhook")
async def github_webhook(request: Request):
    try:
        await request.json()
        subprocess.run(["git", "pull"], cwd="/home/ubuntu/fastapi-app")
        subprocess.run(["sudo", "systemctl", "restart", "fastapi"])
        return {"status": "updated"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Завантажуємо змінні середовища
load_dotenv()

# Ініціалізуємо FastAPI
app = FastAPI()

# Імпортуємо роутери
from app.routes.bitrix_webhook import router as bitrix_router
from app.routes.github_webhook import router as github_router
from app.routes.ping import router as ping_router

# Підключаємо маршрути
app.include_router(bitrix_router)
app.include_router(github_router)
app.include_router(ping_router)

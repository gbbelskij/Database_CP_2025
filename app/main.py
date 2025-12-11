from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import db
from app.routers import auth, users, homes, devices, rooms, sensors, events, rules, logs, analytics

# Инициализируем схему при старте
db.init_schema()

app = FastAPI(
    title="Smart Home Management Service",
    description=(
        "Сервис управления интеллектуальными домашними устройствами "
        "(освещение, климат, безопасность). SQL-версия без ORM."
    ),
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(homes.router)
app.include_router(devices.router)
app.include_router(rooms.router)
app.include_router(sensors.router)
app.include_router(events.router)
app.include_router(rules.router)
app.include_router(logs.router)
app.include_router(analytics.router)


@app.get("/", tags=["root"], summary="Проверка работоспособности")
def read_root():
    return {"message": "Smart Home API is running"}


@app.get("/health", tags=["root"], summary="Health check")
def health():
    return {"status": "ok"}

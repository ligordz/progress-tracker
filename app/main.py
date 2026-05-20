import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.database import Base, engine

# ⚠️ ВАЖНО: Импортируем модели ДО create_all, чтобы SQLAlchemy их зарегистрировал
from app.models import user, session, goal  # noqa
from app.routers import auth, sessions, analytics, goals #noqa



os.makedirs("./data", exist_ok=True)
# Создаём таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ПРОГРЕСС",
    description="Платформа регистрации образовательных графиков с реализацией единиц системного слежения",
    version="0.1.0"
)

# Инициализируем шаблоны ДО использования
templates = Jinja2Templates(directory="templates")

# Подключаем маршруты API
app.include_router(auth.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(goals.router, prefix="/api")

# Главный маршрут — отдаёт HTML-шаблон
@app.get("/")
async def root_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/analytics")
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

# API-документация остаётся доступной
@app.get("/api")
def api_root():
    return {
        "message": "ПРОГРЕСС API работает",
        "docs": "/docs",
        "version": "0.1.0"
    }
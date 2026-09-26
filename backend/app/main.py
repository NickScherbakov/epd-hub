"""
EPD-Hub: Интеллектуальная платформа мониторинга электронных перевозочных документов
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database import Base, engine
from app.api import api_router
from app.models import (
    User, Document, Change, ChangeTag, 
    Notification, NotificationPreference
)

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create all database tables
Base.metadata.create_all(bind=engine)

# Инициализация приложения
app = FastAPI(
    title="EPD-Hub API",
    description="Real-time мониторинг и анализ электронных перевозочных документов",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "epd-hub-api",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    return {
        "message": "EPD-Hub API",
        "version": "0.1.0",
        "description": "Real-time мониторинг и анализ электронных перевозочных документов",
        "docs": "/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

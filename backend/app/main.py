"""
EPD-Hub: Интеллектуальная платформа мониторинга электронных перевозочных документов
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
from pathlib import Path
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

# Configure static files serving
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    logger.info(f"Mounting static files from: {frontend_path}")
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

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
    """Root endpoint - returns API info"""
    return {
        "message": "EPD-Hub API",
        "version": "0.1.0",
        "description": "Real-time мониторинг и анализ электронных перевозочных документов",
        "docs": "/docs",
        "status": "running",
        "frontend": "/index.html"
    }

@app.get("/index.html")
async def serve_index():
    """Serve the main index.html file"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    else:
        return {"error": "index.html not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

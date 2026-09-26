"""
EPD-Hub: Интеллектуальная платформа мониторинга электронных перевозочных документов
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация приложения
app = FastAPI(
    title="EPD-Hub API",
    description="Real-time мониторинг и анализ электронных перевозочных документов",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "epd-hub-api"}

@app.get("/")
async def root():
    return {
        "message": "EPD-Hub API",
        "version": "0.1.0",
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

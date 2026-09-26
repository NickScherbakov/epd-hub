"""
Конфигурация приложения
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://epd_user:epd_password@localhost:5432/epd_hub"
    )
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Crawler settings
    CRAWLER_INTERVAL_MINUTES: int = 60  # Запуск каждый час
    CRAWLER_TIMEOUT_SECONDS: int = 30
    
    # Notification settings
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
    ENABLE_TELEGRAM_NOTIFICATIONS: bool = os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "false").lower() == "true"
    
    # App settings
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

settings = Settings()

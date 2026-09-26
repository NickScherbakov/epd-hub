"""
Celery configuration for background tasks
"""
from celery import Celery
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "epd_hub",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
)

# Periodic tasks schedule
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'run-crawlers-every-hour': {
        'task': 'app.tasks.scheduled_crawlers.run_all_crawlers',
        'schedule': crontab(minute=0),  # Run at the top of every hour
    },
    'process-notifications-every-30-minutes': {
        'task': 'app.tasks.scheduled_crawlers.process_pending_notifications',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
    },
}

logger.info("Celery configured successfully")

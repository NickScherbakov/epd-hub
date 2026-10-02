"""
EPD-Hub: Celery-задача для асинхронного запроса к NotebookLM.

Задача принимает вопрос, проверяет кэш, при необходимости
запускает браузерную сессию и сохраняет результат в Redis.
"""

import asyncio
import logging

from app.celery_app import celery_app
from app.services.ask_cache import get_cached, set_cached
from app.services.notebooklm_bridge import get_bridge

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.ask_task.ask_notebooklm",
    max_retries=2,
    default_retry_delay=10,
    time_limit=120,        # жёсткий лимит 2 минуты
    soft_time_limit=100,   # мягкий лимит — логируем предупреждение
)
def ask_notebooklm(self, question: str) -> dict:
    """
    Celery-задача: задать вопрос NotebookLM.

    Аргументы:
        question: строка с вопросом пользователя

    Возвращает:
        {
            "answer": str,
            "citations": list[str],
            "success": bool,
            "from_cache": bool
        }
    """
    logger.info(f"[ask_notebooklm] Задача запущена, вопрос: {question[:80]}...")

    # 1. Проверяем кэш
    cached = get_cached(question)
    if cached:
        logger.info("[ask_notebooklm] Ответ из кэша")
        return {**cached, "from_cache": True}

    # 2. Запрос к NotebookLM через браузер
    try:
        bridge = get_bridge()
        # asyncio.run() — Celery-воркер синхронный, запускаем event loop
        result = asyncio.run(bridge.ask(question))
    except Exception as exc:
        logger.exception(f"[ask_notebooklm] Ошибка: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {
                "answer": "Сервис временно недоступен. Попробуйте позже.",
                "citations": [],
                "success": False,
                "from_cache": False,
            }

    # 3. Кэшируем успешный ответ
    set_cached(question, result)

    return {**result, "from_cache": False}

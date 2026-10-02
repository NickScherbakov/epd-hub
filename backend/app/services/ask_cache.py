"""
EPD-Hub: Redis-кэш для ответов NotebookLM.

Одинаковые вопросы не дёргают браузер повторно.
TTL настраивается через переменную окружения ASK_CACHE_TTL_SECONDS (по умолчанию 1 час).
"""

import hashlib
import json
import logging
import os
from typing import Optional

import redis

logger = logging.getLogger(__name__)

# TTL кэша в секундах (по умолчанию 1 час)
CACHE_TTL = int(os.getenv("ASK_CACHE_TTL_SECONDS", 3600))
CACHE_PREFIX = "epd_ask:"

_redis_client: Optional[redis.Redis] = None


def _get_redis() -> Optional[redis.Redis]:
    """Ленивое подключение к Redis."""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
        try:
            _redis_client = redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis недоступен, кэш отключён: {e}")
            _redis_client = None
    return _redis_client


def _cache_key(question: str) -> str:
    """Генерировать ключ кэша из нормализованного текста вопроса."""
    normalized = question.strip().lower()
    h = hashlib.sha256(normalized.encode()).hexdigest()[:16]
    return f"{CACHE_PREFIX}{h}"


def get_cached(question: str) -> Optional[dict]:
    """
    Получить кэшированный ответ на вопрос.
    Возвращает None, если кэша нет или Redis недоступен.
    """
    r = _get_redis()
    if r is None:
        return None
    try:
        key = _cache_key(question)
        raw = r.get(key)
        if raw:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(raw)
    except Exception as e:
        logger.warning(f"Ошибка чтения кэша: {e}")
    return None


def set_cached(question: str, result: dict) -> None:
    """
    Сохранить ответ в кэш.
    Кэшируем только успешные ответы.
    """
    if not result.get("success"):
        return
    r = _get_redis()
    if r is None:
        return
    try:
        key = _cache_key(question)
        r.setex(key, CACHE_TTL, json.dumps(result, ensure_ascii=False))
        logger.debug(f"Cache SET: {key}, TTL={CACHE_TTL}s")
    except Exception as e:
        logger.warning(f"Ошибка записи кэша: {e}")


def invalidate_all() -> int:
    """Очистить весь кэш вопросов. Возвращает количество удалённых ключей."""
    r = _get_redis()
    if r is None:
        return 0
    try:
        keys = r.keys(f"{CACHE_PREFIX}*")
        if keys:
            return r.delete(*keys)
    except Exception as e:
        logger.warning(f"Ошибка очистки кэша: {e}")
    return 0

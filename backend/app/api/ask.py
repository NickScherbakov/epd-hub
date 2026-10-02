"""
EPD-Hub: API эндпоинт /api/ask
Принимает вопрос от фронтенда, запускает Celery-задачу,
возвращает task_id для последующего polling-а результата.

Пользователь видит только /api/ask — источник ответов (NotebookLM) скрыт.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator

from app.tasks.ask_task import ask_notebooklm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ask", tags=["ask"])

# ─── Схемы запроса/ответа ────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Вопрос по теме ЭПД",
        example="Какие документы нужны для мультимодальной перевозки по ЭПД?",
    )

    @validator("question")
    def sanitize(cls, v: str) -> str:
        return v.strip()


class AskTaskResponse(BaseModel):
    task_id: str
    status: str = "queued"
    message: str = "Вопрос принят. Используйте task_id для получения ответа."


class AskResultResponse(BaseModel):
    task_id: str
    status: str                   # queued | processing | done | error
    answer: Optional[str] = None
    citations: Optional[list[str]] = None
    from_cache: Optional[bool] = None


# ─── Эндпоинты ───────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=AskTaskResponse,
    summary="Задать вопрос по ЭПД",
    description=(
        "Принимает вопрос и ставит его в очередь обработки. "
        "Возвращает task_id для проверки результата через GET /api/ask/{task_id}."
    ),
)
async def ask_question(body: AskRequest) -> AskTaskResponse:
    """
    Публичный эндпоинт для вопросов по теме ЭПД.
    Внутренний источник знаний (NotebookLM) пользователю не раскрывается.
    """
    try:
        task = ask_notebooklm.delay(body.question)
        logger.info(f"[/api/ask] Задача поставлена в очередь: {task.id}")
        return AskTaskResponse(task_id=task.id)
    except Exception as e:
        logger.exception(f"[/api/ask] Ошибка постановки задачи: {e}")
        raise HTTPException(status_code=503, detail="Сервис временно недоступен")


@router.get(
    "/{task_id}",
    response_model=AskResultResponse,
    summary="Получить ответ на вопрос",
    description="Проверить статус задачи и получить ответ, когда он готов.",
)
async def get_answer(task_id: str) -> AskResultResponse:
    """
    Polling-эндпоинт. Фронтенд опрашивает его каждые 2–3 секунды
    до получения статуса 'done' или 'error'.
    """
    from celery.result import AsyncResult
    from app.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)

    if result.state == "PENDING":
        return AskResultResponse(task_id=task_id, status="queued")

    if result.state == "STARTED":
        return AskResultResponse(task_id=task_id, status="processing")

    if result.state == "SUCCESS":
        data = result.result or {}
        return AskResultResponse(
            task_id=task_id,
            status="done",
            answer=data.get("answer"),
            citations=data.get("citations", []),
            from_cache=data.get("from_cache", False),
        )

    if result.state == "FAILURE":
        logger.error(f"[/api/ask/{task_id}] Задача завершилась с ошибкой")
        return AskResultResponse(
            task_id=task_id,
            status="error",
            answer="Не удалось получить ответ. Попробуйте ещё раз.",
        )

    # RETRY, REVOKED и прочие состояния
    return AskResultResponse(task_id=task_id, status=result.state.lower())

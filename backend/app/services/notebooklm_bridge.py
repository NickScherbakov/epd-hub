"""
EPD-Hub: NotebookLM Bridge Service
Проксирует вопросы пользователя в NotebookLM через браузерную автоматизацию.
Пользователь взаимодействует только с фронтендом EPD-Hub — источник ответов скрыт.

Адаптировано из notebooklm-skill (MIT, github.com/PleasePrompto/notebooklm-skill)
"""

import asyncio
import hashlib
import json
import logging
import os
import random
import re
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Путь к браузерному состоянию (cookies Google-аккаунта)
BROWSER_STATE_DIR = Path(os.getenv(
    "NOTEBOOKLM_STATE_DIR",
    "/app/data/notebooklm_state"
))

# URL ноутбука из переменной окружения — никогда не попадает на фронтенд
NOTEBOOK_URL = os.getenv("NOTEBOOKLM_NOTEBOOK_URL", "")


class NotebookLMBridge:
    """
    Асинхронный клиент для запросов к NotebookLM через Patchright.
    Один экземпляр на процесс Celery-воркера.
    """

    def __init__(self):
        self._lock = asyncio.Lock()

    async def ask(self, question: str) -> dict:
        """
        Отправить вопрос в NotebookLM и получить ответ.

        Returns:
            {
                "answer": str,          # текст ответа
                "citations": list[str], # источники из ноутбука (если есть)
                "success": bool
            }
        """
        if not NOTEBOOK_URL:
            logger.error("NOTEBOOKLM_NOTEBOOK_URL не задан в переменных окружения")
            return self._error("Сервис временно недоступен")

        # Один вопрос одновременно — браузер не потокобезопасен
        async with self._lock:
            return await self._run_browser_session(question)

    async def _run_browser_session(self, question: str) -> dict:
        """Открыть браузер, задать вопрос, вернуть ответ, закрыть браузер."""
        try:
            from patchright.async_api import async_playwright
        except ImportError:
            logger.error("patchright не установлен. Запустите: pip install patchright")
            return self._error("Зависимость patchright не найдена")

        BROWSER_STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_file = BROWSER_STATE_DIR / "browser_state.json"

        async with async_playwright() as pw:
            # Запускаем Chromium в headless-режиме
            browser = await pw.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ]
            )

            # Загружаем сохранённую сессию Google (если есть)
            context_opts = {"viewport": {"width": 1280, "height": 800}}
            if state_file.exists():
                context_opts["storage_state"] = str(state_file)

            context = await browser.new_context(**context_opts)
            page = await context.new_page()

            try:
                result = await self._interact_with_notebook(page, question)

                # Сохраняем обновлённое состояние сессии
                await context.storage_state(path=str(state_file))
                return result

            except Exception as e:
                logger.exception(f"Ошибка при взаимодействии с NotebookLM: {e}")
                return self._error(f"Ошибка при получении ответа")
            finally:
                await context.close()
                await browser.close()

    async def _interact_with_notebook(self, page, question: str) -> dict:
        """Навигация по NotebookLM и извлечение ответа."""

        logger.info(f"Открываю ноутбук: {NOTEBOOK_URL[:50]}...")
        await page.goto(NOTEBOOK_URL, wait_until="networkidle", timeout=30_000)

        # Проверка авторизации
        if "accounts.google.com" in page.url:
            logger.warning("Требуется авторизация Google. Запустите setup-auth.")
            return self._error(
                "Требуется первичная авторизация. "
                "Обратитесь к администратору."
            )

        # Ждём загрузки интерфейса чата
        await self._wait_for_chat(page)

        # Находим поле ввода
        input_selector = await self._find_input(page)
        if not input_selector:
            return self._error("Не удалось найти поле ввода NotebookLM")

        # Печатаем вопрос с человекоподобными задержками
        await page.click(input_selector)
        await self._human_type(page, input_selector, question)

        # Отправляем (Enter)
        await page.keyboard.press("Enter")

        # Ждём ответа
        answer_text, citations = await self._wait_for_answer(page)

        return {
            "answer": answer_text,
            "citations": citations,
            "success": True
        }

    async def _wait_for_chat(self, page) -> None:
        """Ждём, пока интерфейс чата NotebookLM полностью загрузится."""
        selectors = [
            "textarea[placeholder*='Ask']",
            "textarea[placeholder*='Спросите']",
            "div[contenteditable='true']",
            "input[type='text'][aria-label*='chat']",
        ]
        for sel in selectors:
            try:
                await page.wait_for_selector(sel, timeout=10_000)
                return
            except Exception:
                continue
        # Даём лишние 3 секунды на случай медленной загрузки
        await asyncio.sleep(3)

    async def _find_input(self, page) -> Optional[str]:
        """Найти активный элемент ввода чата."""
        candidates = [
            "textarea[placeholder*='Ask']",
            "textarea[placeholder*='Спросите']",
            "textarea[placeholder*='Type']",
            "div[contenteditable='true'][aria-label]",
            "textarea",
        ]
        for sel in candidates:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    return sel
            except Exception:
                continue
        return None

    async def _human_type(self, page, selector: str, text: str) -> None:
        """Печатать текст с рандомными задержками (имитация человека)."""
        for char in text:
            await page.type(selector, char)
            # 50–150 мс между символами
            await asyncio.sleep(random.uniform(0.05, 0.15))

    async def _wait_for_answer(self, page, timeout: int = 60) -> tuple[str, list]:
        """
        Ждём появления ответа в чате.
        Возвращает (текст_ответа, список_источников).
        """
        # Запоминаем количество существующих сообщений
        initial_count = await self._count_messages(page)

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            await asyncio.sleep(2)

            current_count = await self._count_messages(page)
            if current_count > initial_count:
                # Ждём завершения генерации (исчезновения индикатора загрузки)
                await self._wait_for_generation_complete(page)
                return await self._extract_last_answer(page)

        logger.warning("Таймаут ожидания ответа от NotebookLM")
        return "Ответ не получен в отведённое время. Попробуйте позже.", []

    async def _count_messages(self, page) -> int:
        """Посчитать количество сообщений в чате."""
        selectors = [
            "[data-message-author-role='model']",
            ".response-container",
            ".chat-message",
            "[class*='response']",
        ]
        for sel in selectors:
            try:
                elements = await page.query_selector_all(sel)
                if elements:
                    return len(elements)
            except Exception:
                continue
        return 0

    async def _wait_for_generation_complete(self, page, timeout: int = 45) -> None:
        """Ждём, пока индикатор генерации исчезнет."""
        loading_selectors = [
            "[aria-label*='loading']",
            "[class*='thinking']",
            "[class*='generating']",
            ".loading-indicator",
        ]
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            is_loading = False
            for sel in loading_selectors:
                try:
                    el = await page.query_selector(sel)
                    if el and await el.is_visible():
                        is_loading = True
                        break
                except Exception:
                    continue
            if not is_loading:
                return
            await asyncio.sleep(1)

    async def _extract_last_answer(self, page) -> tuple[str, list]:
        """Извлечь текст последнего ответа и список цитат."""
        # Пробуем разные селекторы ответов NotebookLM
        answer_selectors = [
            "[data-message-author-role='model'] .message-content",
            "[data-message-author-role='model']",
            ".response-container:last-child .response-text",
            ".chat-message:last-child",
        ]

        answer_text = ""
        for sel in answer_selectors:
            try:
                elements = await page.query_selector_all(sel)
                if elements:
                    last = elements[-1]
                    answer_text = await last.inner_text()
                    if answer_text.strip():
                        break
            except Exception:
                continue

        # Извлекаем номера источников из текста ([1], [2], ...)
        citations = re.findall(r'\[(\d+)\]', answer_text)
        citations = list(dict.fromkeys(citations))  # дедупликация с сохранением порядка

        return answer_text.strip(), citations

    @staticmethod
    def _error(message: str) -> dict:
        return {"answer": message, "citations": [], "success": False}


# Синглтон для использования в задачах Celery
_bridge_instance: Optional[NotebookLMBridge] = None


def get_bridge() -> NotebookLMBridge:
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = NotebookLMBridge()
    return _bridge_instance

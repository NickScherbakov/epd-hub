"""
EPD-Hub: Утилита первичной авторизации Google для NotebookLM.

Запускается ОДИН РАЗ вручную администратором на сервере:
    python -m app.services.notebooklm_setup

Открывает браузер, позволяет войти в Google-аккаунт,
сохраняет cookies для последующих headless-сессий.
"""

import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

BROWSER_STATE_DIR = Path(os.getenv(
    "NOTEBOOKLM_STATE_DIR",
    "/app/data/notebooklm_state"
))
NOTEBOOK_URL = os.getenv(
    "NOTEBOOKLM_NOTEBOOK_URL",
    "https://notebooklm.google.com"
)


async def setup_auth():
    """
    Интерактивная авторизация: открывает браузер,
    пользователь вручную входит в Google, cookies сохраняются.
    """
    try:
        from patchright.async_api import async_playwright
    except ImportError:
        print("ОШИБКА: patchright не установлен.")
        print("Запустите: pip install patchright && patchright install chromium")
        return

    BROWSER_STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = BROWSER_STATE_DIR / "browser_state.json"

    print("\n" + "="*60)
    print("EPD-Hub: Первичная авторизация NotebookLM")
    print("="*60)
    print(f"\n1. Откроется браузер")
    print(f"2. Войдите в Google-аккаунт, привязанный к ноутбуку")
    print(f"3. Убедитесь, что ноутбук открылся")
    print(f"4. Нажмите Enter в этом терминале для сохранения сессии\n")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,  # Видимый браузер для ручного входа
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        await page.goto(NOTEBOOK_URL)
        print(f"Браузер открыт. URL: {NOTEBOOK_URL}")
        print("\nВойдите в аккаунт и нажмите Enter здесь когда будете готовы...")

        # Ждём нажатия Enter в терминале
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, input)

        # Сохраняем состояние браузера
        await context.storage_state(path=str(state_file))
        print(f"\n✅ Сессия сохранена: {state_file}")
        print("Теперь EPD-Hub может работать с NotebookLM в headless-режиме.\n")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(setup_auth())

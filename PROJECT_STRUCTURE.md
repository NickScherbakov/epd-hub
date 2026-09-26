# EPD-Hub Project Structure

```
epd-hub/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI приложение
│   │   ├── config.py               # Конфигурация
│   │   ├── models/                 # SQLAlchemy ORM модели
│   │   │   ├── __init__.py
│   │   │   ├── document.py         # Модели документов ЭПД
│   │   │   ├── change.py           # Модели изменений в нормативной базе
│   │   │   ├── notification.py     # Модели уведомлений
│   │   │   └── user.py             # Модели пользователей
│   │   ├── schemas/                # Pydantic схемы для API
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── change.py
│   │   │   └── notification.py
│   │   ├── api/                    # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── documents.py        # CRUD для документов
│   │   │   ├── changes.py          # CRUD для изменений
│   │   │   ├── notifications.py    # Управление уведомлениями
│   │   │   └── monitoring.py       # Real-time мониторинг
│   │   ├── services/               # Бизнес-логика
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py          # Crawler для мониторинга
│   │   │   ├── analyzer.py         # Анализ изменений (LLM)
│   │   │   ├── classifier.py       # Классификация документов
│   │   │   └── notifier.py         # Отправка уведомлений
│   │   ├── crawlers/               # Специфичные crawler'ы
│   │   │   ├── __init__.py
│   │   │   ├── fns_crawler.py      # ФНС (nalog.gov.ru)
│   │   │   ├── mintrans_crawler.py # Минтранс (mintrans.gov.ru)
│   │   │   ├── rosstandart_crawler.py # ГОСТ и стандарты
│   │   │   └── 1c_crawler.py       # 1С форумы и обновления
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   └── db.py               # Database helper'ы
│   │   └── tasks/                  # Celery задачи
│   │       ├── __init__.py
│   │       └── scheduled_crawlers.py
│   ├── migrations/                 # Alembic миграции БД
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_crawlers.py
│   │   └── test_services.py
│   ├── .env.example
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── alembic.ini
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── API.md                      # OpenAPI документация
│   ├── ARCHITECTURE.md             # Архитектура проекта
│   ├── DEPLOYMENT.md               # Инструкции по развертыванию
│   └── CRAWLER_SOURCES.md          # Список источников мониторинга
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── deploy.yml
├── docker-compose.yml              # Production стек
├── requirements.txt
├── README.md
└── PROJECT_STRUCTURE.md
```

## Фазы разработки

### Фаза 1: MVP Crawler + API (Неделя 1-2)
- [x] Инициализация репозитория
- [ ] Базовая структура проекта
- [ ] Database schema для документов и изменений
- [ ] Простой crawler для ФНС (test mode)
- [ ] REST API для получения изменений
- [ ] Background task для запуска crawler'ов каждый час

### Фаза 2: Аналитика и персонализация (Неделя 3-4)
- [ ] Интеграция с OpenAI/LLM для анализа
- [ ] Классификатор документов (ЭТрН, ЭПЛ, ЭЭД и т.д.)
- [ ] Система тегов и категорий
- [ ] Персонализированные feed по ролям
- [ ] Telegram bot для уведомлений

### Фаза 3: Frontend + Монетизация (Неделя 5+)
- [ ] React/TypeScript frontend
- [ ] Система подписок и авторизации
- [ ] Маркетплейс шаблонов
- [ ] Admin панель для управления контентом
- [ ] API для B2B интеграций

## Ключевые источники мониторинга

1. **ФНС** - nalog.gov.ru (письма, приказы)
2. **Минтранс** - mintrans.gov.ru (реестры, постановления)
3. **Ространснадзор** - rostransport.gov.ru
4. **ГОСТ** - gosstandart.gov.ru
5. **1С форумы** - forum.infostart.ru
6. **RSS федеральной юстиции** - regulation.gov.ru
7. **GitHub 1С репозитории** - github.com/1C-Company

## Технологический стек

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Celery
- **Database**: PostgreSQL
- **Frontend**: React 18, TypeScript, Vite
- **DevOps**: Docker, Docker Compose
- **AI/ML**: OpenAI API, LangChain
- **Monitoring**: Telegram Bot API, Email notifications
- **Testing**: pytest, httpx

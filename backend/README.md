# EPD-Hub Backend

FastAPI-based backend for the EPD-Hub platform.

## Quick Start

### 1. Setup Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# Make sure DATABASE_URL points to your PostgreSQL instance
```

### 3. Initialize Database

```bash
# Create all tables
python -c "from app.database import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload
```

Server will be available at: http://localhost:8000

**API Documentation (Swagger):** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

## Run Celery Worker (for background tasks)

```bash
# In a separate terminal
celery -A app.celery_app worker --loglevel=info
```

## Run Celery Beat (for scheduled tasks)

```bash
# In another separate terminal
celery -A app.celery_app beat --loglevel=info
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup (SQLAlchemy)
│   ├── celery_app.py        # Celery configuration
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── change.py
│   │   └── notification.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── change.py
│   │   ├── notification.py
│   │   └── common.py
│   ├── api/                 # API endpoints (routers)
│   │   ├── documents.py     # /api/documents
│   │   ├── changes.py       # /api/changes
│   │   └── notifications.py # /api/notifications
│   ├── crawlers/            # Crawler implementations
│   │   ├── base.py          # Base crawler class
│   │   └── fns_crawler.py   # FNS-specific crawler
│   ├── services/            # Business logic services
│   │   └── crawler_service.py
│   └── tasks/               # Celery tasks
│       └── scheduled_crawlers.py
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration
│   ├── test_api.py          # API endpoint tests
│   ├── test_models.py       # Model tests
│   └── test_crawlers.py     # Crawler tests
├── requirements.txt
├── .env.example
└── pytest.ini
```

## API Endpoints

### Documents
- `GET /api/documents/` - List documents
- `POST /api/documents/` - Create document
- `GET /api/documents/{id}` - Get document
- `PATCH /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document

### Changes
- `GET /api/changes/` - List changes
- `POST /api/changes/` - Create change
- `GET /api/changes/{id}` - Get change
- `PATCH /api/changes/{id}` - Update change
- `DELETE /api/changes/{id}` - Delete change
- `GET /api/changes/{id}/mark-analyzed` - Mark as analyzed

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/` - Create notification
- `GET /api/notifications/{id}` - Get notification
- `PATCH /api/notifications/{id}` - Update notification
- `DELETE /api/notifications/{id}` - Delete notification
- `GET /api/notifications/preferences/{user_id}` - Get user preferences
- `POST /api/notifications/preferences` - Create preference
- `PATCH /api/notifications/preferences/{id}` - Update preference

## Dependencies

Key dependencies are listed in requirements.txt:
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **psycopg2** - PostgreSQL adapter
- **Celery** - Task queue
- **Redis** - Message broker
- **requests** - HTTP client
- **BeautifulSoup4** - Web scraping
- **feedparser** - RSS parsing
- **pytest** - Testing framework

## Database Models

### User
- Email, username, password
- Notification preferences
- Role-based access control

### Document
- Title, description, regulations
- Document type (ЭТрН, ЭПЛ, ЭЭД)
- Source metadata

### Change
- Regulatory changes from various sources
- Status tracking (new, analyzed, archived)
- Affected document types
- Tags for categorization

### Notification
- User notifications
- Delivery channels (email, telegram, web)
- Status tracking (sent, read)

### NotificationPreference
- User's notification settings
- Document type filters
- Source preferences
- Digest mode settings

"""
Services package initialization

Deliberately does NOT eagerly import CrawlerService here: that pulls in
app.models -> app.database, which creates a DB engine at import time
(fails hard if DATABASE_URL isn't set to something reachable). Utility
scripts like notebooklm_setup.py run as `python -m app.services.X`, which
executes this __init__.py first - they shouldn't need a working DB
connection just to launch a browser. Consumers that need CrawlerService
import it directly from app.services.crawler_service.
"""

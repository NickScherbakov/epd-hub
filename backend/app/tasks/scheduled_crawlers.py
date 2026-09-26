"""
Scheduled Celery tasks for background processing
"""
import logging
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services import CrawlerService
from app.models import Notification
from datetime import datetime

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.scheduled_crawlers.run_all_crawlers")
def run_all_crawlers():
    """
    Run all crawlers to fetch latest regulatory changes.
    Scheduled to run every hour.
    """
    db = SessionLocal()
    try:
        logger.info("Starting scheduled crawler run")
        crawler_service = CrawlerService(db)
        results = crawler_service.run_all_crawlers()
        
        logger.info(f"Crawler run completed: {results}")
        return {
            "success": True,
            "total_crawlers": results["total_crawlers"],
            "successful": results["successful"],
            "failed": results["failed"],
            "total_changes_found": results["total_changes_found"]
        }
    
    except Exception as e:
        logger.error(f"Error running crawlers: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        db.close()


@celery_app.task(name="app.tasks.scheduled_crawlers.process_pending_notifications")
def process_pending_notifications():
    """
    Process pending notifications.
    Send unsent notifications to users.
    Scheduled to run every 30 minutes.
    """
    db = SessionLocal()
    try:
        logger.info("Starting notification processing")
        
        # Get all unsent notifications
        pending = db.query(Notification).filter(Notification.is_sent == False).limit(100).all()
        
        processed = 0
        failed = 0
        
        for notification in pending:
            try:
                # Mark as sent (in real scenario, send via email/telegram/web)
                notification.is_sent = True
                notification.sent_at = datetime.utcnow()
                db.add(notification)
                processed += 1
            except Exception as e:
                logger.error(f"Error processing notification {notification.id}: {e}")
                failed += 1
        
        db.commit()
        
        logger.info(f"Notification processing complete: {processed} processed, {failed} failed")
        return {
            "success": True,
            "processed": processed,
            "failed": failed
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing notifications: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        db.close()


@celery_app.task(name="app.tasks.scheduled_crawlers.analyze_changes")
def analyze_changes():
    """
    Analyze new changes using LLM.
    This is a placeholder for LLM-based analysis.
    """
    db = SessionLocal()
    try:
        logger.info("Starting change analysis")
        
        from app.models import Change, ChangeStatus
        
        # Get unanalyzed changes
        unanalyzed = db.query(Change).filter(
            Change.is_analyzed == False,
            Change.status == ChangeStatus.NEW
        ).limit(50).all()
        
        analyzed = 0
        for change in unanalyzed:
            try:
                # Placeholder: in real scenario, call OpenAI API for analysis
                change.is_analyzed = True
                change.impact_summary = f"Auto-generated summary for: {change.title}"
                change.status = ChangeStatus.ANALYZED
                db.add(change)
                analyzed += 1
            except Exception as e:
                logger.error(f"Error analyzing change {change.id}: {e}")
        
        db.commit()
        
        logger.info(f"Analysis complete: {analyzed} changes analyzed")
        return {
            "success": True,
            "analyzed": analyzed
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing changes: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        db.close()

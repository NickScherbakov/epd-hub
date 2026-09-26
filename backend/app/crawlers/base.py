"""
Base crawler class and utilities
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
import requests
from app.models import Change, ChangeSource

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """Base class for all crawlers"""
    
    def __init__(self, db: Session, timeout: int = 30):
        self.db = db
        self.timeout = timeout
        self.source: ChangeSource = None
        self.changes_found = 0
        self.errors = []
    
    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from the source.
        Must return a list of dictionaries with change information.
        """
        pass
    
    @abstractmethod
    def parse_changes(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Parse raw data and extract change information.
        """
        pass
    
    def save_changes(self, changes: List[Dict[str, Any]]) -> int:
        """
        Save parsed changes to database.
        Returns the number of new changes saved.
        """
        new_changes = 0
        
        for change_data in changes:
            # Check if change already exists (by title + source + published_date)
            existing = self.db.query(Change).filter(
                Change.title == change_data.get("title"),
                Change.source == self.source,
                Change.published_date == change_data.get("published_date")
            ).first()
            
            if not existing:
                db_change = Change(
                    title=change_data.get("title", ""),
                    description=change_data.get("description", ""),
                    full_content=change_data.get("full_content"),
                    source=self.source,
                    affected_document_types=change_data.get("affected_document_types"),
                    source_url=change_data.get("source_url"),
                    official_link=change_data.get("official_link"),
                    published_date=change_data.get("published_date"),
                    effective_date=change_data.get("effective_date")
                )
                
                self.db.add(db_change)
                new_changes += 1
        
        try:
            self.db.commit()
            self.changes_found = new_changes
            logger.info(f"Saved {new_changes} new changes from {self.source}")
        except Exception as e:
            self.db.rollback()
            self.errors.append(str(e))
            logger.error(f"Error saving changes: {e}")
        
        return new_changes
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the crawler pipeline.
        Returns statistics about the run.
        """
        try:
            logger.info(f"Starting crawler for {self.source}")
            
            # Fetch data
            raw_data = self.fetch_data()
            logger.info(f"Fetched {len(raw_data)} raw items from {self.source}")
            
            # Parse changes
            changes = self.parse_changes(raw_data)
            logger.info(f"Parsed {len(changes)} changes from {self.source}")
            
            # Save to database
            self.save_changes(changes)
            
            return {
                "success": True,
                "source": self.source,
                "changes_found": self.changes_found,
                "errors": self.errors,
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Crawler failed for {self.source}: {e}")
            self.errors.append(str(e))
            return {
                "success": False,
                "source": self.source,
                "changes_found": 0,
                "errors": self.errors,
                "timestamp": datetime.utcnow()
            }
    
    def _fetch_url(self, url: str) -> Optional[str]:
        """
        Helper method to fetch URL content.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            self.errors.append(f"Failed to fetch {url}: {str(e)}")
            return None

"""
FNS (Federal Tax Service) crawler for monitoring regulatory changes at nalog.gov.ru
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
import logging
from sqlalchemy.orm import Session
from app.crawlers.base import BaseCrawler
from app.models import ChangeSource

logger = logging.getLogger(__name__)


class FNSCrawler(BaseCrawler):
    """Crawler for FNS (nalog.gov.ru) documents and regulatory changes"""
    
    def __init__(self, db: Session, timeout: int = 30):
        super().__init__(db, timeout)
        self.source = ChangeSource.FNS
        self.fns_base_url = "https://www.nalog.gov.ru"
        self.rss_url = "https://www.nalog.gov.ru/rss/"
    
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch RSS feed and parse recent announcements from FNS.
        In a real scenario, this would parse the actual FNS RSS feed or web pages.
        """
        raw_items = []
        
        # Fetch RSS feed
        try:
            logger.info(f"Fetching FNS RSS feed from {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            if feed.status != 200 and feed.entries:
                logger.warning(f"FNS RSS fetch returned status: {feed.status}")
            
            for entry in feed.entries[:10]:  # Get last 10 entries
                raw_items.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "author": entry.get("author", "")
                })
            
            logger.info(f"Fetched {len(raw_items)} items from FNS RSS")
            return raw_items
        
        except Exception as e:
            logger.error(f"Error fetching FNS RSS: {e}")
            self.errors.append(f"RSS fetch error: {str(e)}")
            return []
    
    def parse_changes(self, raw_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Parse FNS RSS entries into standardized change format.
        """
        changes = []
        
        for item in raw_data:
            try:
                # Determine which document types are affected
                affected_types = self._detect_document_types(item.get("title", "") + " " + item.get("summary", ""))
                
                change = {
                    "title": item.get("title", ""),
                    "description": item.get("summary", "")[:500],  # Limit to 500 chars
                    "full_content": item.get("summary", ""),
                    "source_url": item.get("link", ""),
                    "affected_document_types": ",".join(affected_types) if affected_types else None,
                    "published_date": self._parse_date(item.get("published", "")),
                }
                
                changes.append(change)
            
            except Exception as e:
                logger.error(f"Error parsing FNS item: {e}")
                self.errors.append(f"Parse error: {str(e)}")
        
        return changes
    
    def _detect_document_types(self, text: str) -> List[str]:
        """
        Detect which document types are mentioned in the text.
        Returns list of affected document types.
        """
        affected = []
        
        keywords = {
            "ЭТрН": ["ЭТрН", "электронная транспортная накладная", "эТрН"],
            "ЭПЛ": ["ЭПЛ", "электронный путевой лист", "эПЛ"],
            "ЭЭД": ["ЭЭД", "электронный реестр", "эЭД"],
        }
        
        text_lower = text.lower()
        for doc_type, keywords_list in keywords.items():
            for keyword in keywords_list:
                if keyword.lower() in text_lower:
                    if doc_type not in affected:
                        affected.append(doc_type)
                    break
        
        return affected
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string from RSS feed.
        RSS typically uses RFC 2822 format.
        """
        if not date_str:
            return None
        
        try:
            # Try common formats
            for fmt in [
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
            ]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If none work, return None
            logger.warning(f"Could not parse date: {date_str}")
            return None
        
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {e}")
            return None

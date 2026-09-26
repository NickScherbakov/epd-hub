"""
Crawler orchestration service
"""
import logging
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.crawlers import BaseCrawler, FNSCrawler
from app.models import Change

logger = logging.getLogger(__name__)


class CrawlerService:
    """Service for managing and running crawlers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.crawlers = self._initialize_crawlers()
    
    def _initialize_crawlers(self) -> List[BaseCrawler]:
        """Initialize all available crawlers"""
        crawlers = [
            FNSCrawler(self.db),
            # Add more crawlers here in the future
            # MintransCrawler(self.db),
            # RosstandartCrawler(self.db),
        ]
        return crawlers
    
    def run_all_crawlers(self) -> Dict[str, Any]:
        """
        Run all available crawlers.
        Returns summary statistics.
        """
        results = {
            "total_crawlers": len(self.crawlers),
            "successful": 0,
            "failed": 0,
            "total_changes_found": 0,
            "crawler_results": []
        }
        
        for crawler in self.crawlers:
            try:
                logger.info(f"Running crawler: {crawler.source}")
                result = crawler.run()
                
                results["crawler_results"].append(result)
                results["total_changes_found"] += result.get("changes_found", 0)
                
                if result.get("success"):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
            
            except Exception as e:
                logger.error(f"Failed to run crawler {crawler.source}: {e}")
                results["failed"] += 1
                results["crawler_results"].append({
                    "success": False,
                    "source": str(crawler.source),
                    "error": str(e)
                })
        
        logger.info(f"Crawler run complete: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def run_crawler_by_source(self, source: str) -> Dict[str, Any]:
        """
        Run a specific crawler by source name.
        """
        crawler = self._get_crawler_by_source(source)
        
        if not crawler:
            return {
                "success": False,
                "error": f"Crawler not found for source: {source}"
            }
        
        logger.info(f"Running crawler: {source}")
        return crawler.run()
    
    def _get_crawler_by_source(self, source: str) -> BaseCrawler:
        """Get crawler by source name"""
        for crawler in self.crawlers:
            if str(crawler.source) == source:
                return crawler
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about changes in the system"""
        stats = {
            "total_changes": self.db.query(Change).count(),
            "new_changes": self.db.query(Change).filter(Change.status == "new").count(),
            "analyzed_changes": self.db.query(Change).filter(Change.is_analyzed == True).count(),
            "archived_changes": self.db.query(Change).filter(Change.status == "archived").count(),
        }
        return stats

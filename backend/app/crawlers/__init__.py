"""
Crawlers package initialization
"""
from app.crawlers.base import BaseCrawler
from app.crawlers.fns_crawler import FNSCrawler

__all__ = ["BaseCrawler", "FNSCrawler"]

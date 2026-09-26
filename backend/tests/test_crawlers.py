"""
Tests for crawlers
"""
import pytest
from app.crawlers import FNSCrawler
from app.models import Change, ChangeSource


class TestFNSCrawler:
    """Tests for FNS crawler"""
    
    def test_crawler_initialization(self, db):
        """Test crawler initialization"""
        crawler = FNSCrawler(db)
        assert crawler.source == ChangeSource.FNS
        assert crawler.timeout == 30
        assert crawler.changes_found == 0
    
    def test_detect_document_types(self, db):
        """Test document type detection"""
        crawler = FNSCrawler(db)
        
        # Test with ЭТрН
        text = "Новые правила для электронной транспортной накладной ЭТрН"
        types = crawler._detect_document_types(text)
        assert "ЭТрН" in types
        
        # Test with multiple types
        text = "Изменения для ЭТрН и ЭПЛ"
        types = crawler._detect_document_types(text)
        assert "ЭТрН" in types
        assert "ЭПЛ" in types
        
        # Test with no types
        text = "Общие новости"
        types = crawler._detect_document_types(text)
        assert len(types) == 0
    
    def test_parse_changes(self, db):
        """Test parsing changes from raw data"""
        crawler = FNSCrawler(db)
        
        raw_data = [
            {
                "title": "Обновление ЭТрН",
                "summary": "Новые требования к электронной транспортной накладной",
                "link": "http://example.com/news/1",
                "published": "Mon, 26 Sep 2024 10:00:00 +0000"
            }
        ]
        
        changes = crawler.parse_changes(raw_data)
        assert len(changes) > 0
        assert changes[0]["title"] == "Обновление ЭТрН"
        assert changes[0]["source_url"] == "http://example.com/news/1"
    
    def test_save_changes(self, db):
        """Test saving changes to database"""
        crawler = FNSCrawler(db)
        
        changes = [
            {
                "title": "Test Change",
                "description": "Test description",
                "source_url": "http://example.com/test",
                "affected_document_types": "ЭТрН"
            }
        ]
        
        count = crawler.save_changes(changes)
        assert count == 1
        
        # Verify it was saved
        db_changes = db.query(Change).all()
        assert len(db_changes) == 1
        assert db_changes[0].title == "Test Change"
    
    def test_no_duplicate_changes(self, db):
        """Test that duplicate changes are not saved"""
        crawler = FNSCrawler(db)
        
        changes = [
            {
                "title": "Test Change",
                "description": "Test description",
                "source_url": "http://example.com/test",
                "published_date": None
            }
        ]
        
        # Save first time
        count1 = crawler.save_changes(changes)
        assert count1 == 1
        
        # Try to save again - should not create duplicate
        count2 = crawler.save_changes(changes)
        assert count2 == 0
        
        # Verify only one change in database
        db_changes = db.query(Change).all()
        assert len(db_changes) == 1

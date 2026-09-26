"""
Tests for models
"""
import pytest
from datetime import datetime
from app.models import (
    User, UserRole,
    Document, DocumentType,
    Change, ChangeStatus, ChangeSource, ChangeTag,
    Notification, NotificationPreference, NotificationChannel
)


class TestUserModel:
    """Tests for User model"""
    
    def test_create_user(self, db):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_pwd",
            full_name="Test User",
            role=UserRole.READER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == UserRole.READER
        assert user.is_active == True


class TestDocumentModel:
    """Tests for Document model"""
    
    def test_create_document(self, db):
        """Test creating a document"""
        doc = Document(
            title="Test Document",
            description="Test description",
            document_type=DocumentType.ETN,
            regulations="Test regulations",
            source_name="ФНС",
            keywords="test,keywords"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        assert doc.id is not None
        assert doc.title == "Test Document"
        assert doc.document_type == DocumentType.ETN
        assert doc.is_active == True
        assert doc.is_important == False


class TestChangeModel:
    """Tests for Change model"""
    
    def test_create_change(self, db):
        """Test creating a change"""
        change = Change(
            title="Test Change",
            description="Test description",
            source=ChangeSource.FNS,
            status=ChangeStatus.NEW
        )
        db.add(change)
        db.commit()
        db.refresh(change)
        
        assert change.id is not None
        assert change.title == "Test Change"
        assert change.source == ChangeSource.FNS
        assert change.status == ChangeStatus.NEW
        assert change.is_analyzed == False
    
    def test_change_tag_relationship(self, db):
        """Test many-to-many relationship between Change and ChangeTag"""
        tag = ChangeTag(name="Important", color="#FF0000")
        db.add(tag)
        db.commit()
        
        change = Change(
            title="Test",
            description="Test",
            source=ChangeSource.FNS,
            status=ChangeStatus.NEW
        )
        change.tags.append(tag)
        db.add(change)
        db.commit()
        db.refresh(change)
        
        assert len(change.tags) == 1
        assert change.tags[0].name == "Important"


class TestNotificationModel:
    """Tests for Notification models"""
    
    def test_create_notification_preference(self, db):
        """Test creating notification preference"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        pref = NotificationPreference(
            user_id=user.id,
            channel=NotificationChannel.EMAIL,
            enabled=True,
            notify_etrn=True,
            notify_sources="ФНС,Минтранс"
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
        
        assert pref.id is not None
        assert pref.channel == NotificationChannel.EMAIL
        assert pref.enabled == True
    
    def test_create_notification(self, db):
        """Test creating a notification"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        notif = Notification(
            user_id=user.id,
            title="Test Notification",
            message="Test message",
            channel=NotificationChannel.EMAIL,
            is_sent=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        
        assert notif.id is not None
        assert notif.title == "Test Notification"
        assert notif.is_sent == False
        assert notif.is_read == False

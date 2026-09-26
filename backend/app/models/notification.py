"""
Notification model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEB = "web"


class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    
    # Notification settings
    channel = Column(SQLEnum(NotificationChannel), index=True)
    enabled = Column(Boolean, default=True)
    
    # Document type filters
    notify_etrn = Column(Boolean, default=True)
    notify_epl = Column(Boolean, default=True)
    notify_eed = Column(Boolean, default=True)
    
    # Source filters (comma-separated or JSON)
    notify_sources = Column(String(500), default="ФНС,Минтранс")  # Which sources to track
    
    # Frequency
    digest_mode = Column(Boolean, default=False)  # True = daily digest, False = real-time
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notification_settings")
    
    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id}, channel={self.channel})>"


class Notification(Base):
    """Sent notifications tracking"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    change_id = Column(Integer, ForeignKey('changes.id', ondelete='CASCADE'), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # Notification content
    title = Column(String(255))
    message = Column(Text)
    channel = Column(SQLEnum(NotificationChannel), index=True)
    
    # Status
    is_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    
    # Delivery details
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    change = relationship("Change", back_populates="notifications")
    document = relationship("Document", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, channel={self.channel})>"

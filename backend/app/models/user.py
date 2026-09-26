"""
User model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base


class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    ANALYST = "analyst"
    READER = "reader"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255), nullable=True)
    
    role = Column(SQLEnum(UserRole), default=UserRole.READER)
    is_active = Column(Boolean, default=True)
    
    # Notification preferences
    notification_email = Column(Boolean, default=True)
    notification_telegram = Column(Boolean, default=False)
    telegram_chat_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notification_settings = relationship("NotificationPreference", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

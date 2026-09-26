"""
Document model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base


class DocumentType(str, Enum):
    """Types of electronic transportation documents"""
    ETN = "ЭТрН"  # Электронная транспортная накладная
    EPL = "ЭПЛ"   # Электронная путевого листа
    EED = "ЭЭД"   # Электронный реестр документов
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(500), index=True)
    description = Column(Text, nullable=True)
    document_type = Column(SQLEnum(DocumentType), index=True)
    
    # Document content and metadata
    regulations = Column(Text)  # Which regulations this document relates to
    requirements = Column(Text, nullable=True)  # Key requirements
    keywords = Column(String(500), nullable=True)  # Comma-separated keywords
    
    # Source and references
    source_url = Column(String(500), nullable=True)
    source_name = Column(String(100), index=True)  # e.g., "ФНС", "Минтранс"
    
    # Status
    is_active = Column(Boolean, default=True)
    is_important = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)  # When document was officially published
    
    # Relationships
    changes = relationship("Change", back_populates="document", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, type={self.document_type})>"

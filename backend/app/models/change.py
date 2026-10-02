"""
Change model - tracks changes in regulatory documents
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base


class ChangeStatus(str, Enum):
    """Status of a regulatory change"""
    NEW = "new"
    ANALYZED = "analyzed"
    ARCHIVED = "archived"
    IMPORTANT = "important"


class ChangeSource(str, Enum):
    """Source of the change"""
    FNS = "ФНС"
    MINTRANS = "Минтранс"
    ROSSTANDART = "Ространиц"
    FEDERAL_JUSTICE = "Федеральная юстиция"
    FORUM = "Форум 1С"
    OTHER = "other"


# Association table for many-to-many relationship between Change and Tag
# Named distinctly from the `change_tags` table below (ChangeTag model) -
# that table holds the actual tags; this one only links changes to tags.
change_tags_association = Table(
    'change_tag_links',
    Base.metadata,
    Column('change_id', Integer, ForeignKey('changes.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('change_tags.id', ondelete='CASCADE'))
)


class ChangeTag(Base):
    """Tags for categorizing changes"""
    __tablename__ = "change_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(255), nullable=True)
    color = Column(String(7), default="#808080")  # Hex color code
    
    changes = relationship("Change", secondary=change_tags_association, back_populates="tags")
    
    def __repr__(self):
        return f"<ChangeTag(id={self.id}, name={self.name})>"


class Change(Base):
    """Regulatory change in the system"""
    __tablename__ = "changes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(500), index=True)
    description = Column(Text)
    full_content = Column(Text, nullable=True)
    
    # Classification
    source = Column(SQLEnum(ChangeSource), index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True, index=True)
    
    # Impact analysis
    affected_document_types = Column(String(200), nullable=True)  # Comma-separated list
    impact_summary = Column(Text, nullable=True)  # LLM-generated summary
    
    # Status tracking
    status = Column(SQLEnum(ChangeStatus), default=ChangeStatus.NEW, index=True)
    is_analyzed = Column(Boolean, default=False)
    
    # URLs and references
    source_url = Column(String(500), nullable=True)
    official_link = Column(String(500), nullable=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    published_date = Column(DateTime, nullable=True)  # When the change was officially published
    effective_date = Column(DateTime, nullable=True)  # When the change becomes effective
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="changes")
    tags = relationship("ChangeTag", secondary=change_tags_association, back_populates="changes")
    notifications = relationship("Notification", back_populates="change", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Change(id={self.id}, title={self.title}, source={self.source})>"

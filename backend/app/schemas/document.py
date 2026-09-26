"""
Document schemas for API requests/responses
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    """Base document schema"""
    title: str = Field(..., min_length=3, max_length=500)
    description: Optional[str] = None
    document_type: str
    regulations: str
    requirements: Optional[str] = None
    keywords: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Document creation schema"""
    source_url: Optional[str] = None
    source_name: str
    published_at: Optional[datetime] = None


class DocumentUpdate(BaseModel):
    """Document update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    keywords: Optional[str] = None
    is_active: Optional[bool] = None
    is_important: Optional[bool] = None


class DocumentResponse(DocumentBase):
    """Document response schema"""
    id: int
    source_url: Optional[str] = None
    source_name: str
    is_active: bool
    is_important: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response with changes"""
    changes_count: int = 0
    
    class Config:
        from_attributes = True

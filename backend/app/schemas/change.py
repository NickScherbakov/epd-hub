"""
Change schemas for API requests/responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChangeTagResponse(BaseModel):
    """Change tag response schema"""
    id: int
    name: str
    description: Optional[str] = None
    color: str
    
    class Config:
        from_attributes = True


class ChangeBase(BaseModel):
    """Base change schema"""
    title: str = Field(..., min_length=3, max_length=500)
    description: str
    source: str
    affected_document_types: Optional[str] = None


class ChangeCreate(ChangeBase):
    """Change creation schema"""
    full_content: Optional[str] = None
    document_id: Optional[int] = None
    source_url: Optional[str] = None
    official_link: Optional[str] = None
    published_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None


class ChangeUpdate(BaseModel):
    """Change update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    impact_summary: Optional[str] = None
    status: Optional[str] = None
    is_analyzed: Optional[bool] = None


class ChangeResponse(ChangeBase):
    """Change response schema"""
    id: int
    document_id: Optional[int] = None
    impact_summary: Optional[str] = None
    status: str
    is_analyzed: bool
    source_url: Optional[str] = None
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime
    published_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    tags: List[ChangeTagResponse] = []
    
    class Config:
        from_attributes = True


class ChangeDetailResponse(ChangeResponse):
    """Detailed change response"""
    full_content: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChangeListResponse(BaseModel):
    """List of changes response"""
    total: int
    skip: int
    limit: int
    items: List[ChangeResponse]

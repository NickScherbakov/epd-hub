"""
Pagination and filter schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    total: int
    skip: int
    limit: int
    items: list
    
    class Config:
        from_attributes = True


class ChangeFilterParams(BaseModel):
    """Filters for change queries"""
    source: Optional[str] = None
    status: Optional[str] = None
    is_analyzed: Optional[bool] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class DocumentFilterParams(BaseModel):
    """Filters for document queries"""
    document_type: Optional[str] = None
    source_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_important: Optional[bool] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)

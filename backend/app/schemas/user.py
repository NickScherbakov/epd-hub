"""
User schemas for API requests/responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: str = "reader"


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    notification_email: Optional[bool] = None
    notification_telegram: Optional[bool] = None
    telegram_chat_id: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    notification_email: bool
    notification_telegram: bool
    telegram_chat_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detailed user response with settings"""
    pass

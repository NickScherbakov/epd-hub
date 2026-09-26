"""
Notification schemas for API requests/responses
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationPreferenceBase(BaseModel):
    """Base notification preference schema"""
    channel: str
    enabled: bool = True
    notify_etrn: bool = True
    notify_epl: bool = True
    notify_eed: bool = True
    notify_sources: str = "ФНС,Минтранс"
    digest_mode: bool = False


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Create notification preference schema"""
    pass


class NotificationPreferenceUpdate(BaseModel):
    """Update notification preference schema"""
    enabled: Optional[bool] = None
    notify_etrn: Optional[bool] = None
    notify_epl: Optional[bool] = None
    notify_eed: Optional[bool] = None
    notify_sources: Optional[str] = None
    digest_mode: Optional[bool] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Notification preference response schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    """Base notification schema"""
    title: str
    message: str
    channel: str


class NotificationCreate(NotificationBase):
    """Create notification schema"""
    user_id: int
    change_id: Optional[int] = None
    document_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    """Update notification schema"""
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Notification response schema"""
    id: int
    user_id: int
    change_id: Optional[int] = None
    document_id: Optional[int] = None
    is_sent: bool
    is_read: bool
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications response"""
    total: int
    skip: int
    limit: int
    items: list

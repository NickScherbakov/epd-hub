"""
Schemas package initialization
"""
from app.schemas.common import PaginationParams, PaginatedResponse, ChangeFilterParams, DocumentFilterParams
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse, UserDetailResponse
from app.schemas.document import DocumentBase, DocumentCreate, DocumentUpdate, DocumentResponse, DocumentDetailResponse
from app.schemas.change import ChangeBase, ChangeCreate, ChangeUpdate, ChangeResponse, ChangeDetailResponse, ChangeListResponse, ChangeTagResponse
from app.schemas.notification import (
    NotificationPreferenceBase, NotificationPreferenceCreate, NotificationPreferenceUpdate, NotificationPreferenceResponse,
    NotificationBase, NotificationCreate, NotificationUpdate, NotificationResponse, NotificationListResponse
)

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "ChangeFilterParams",
    "DocumentFilterParams",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserDetailResponse",
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentDetailResponse",
    "ChangeBase",
    "ChangeCreate",
    "ChangeUpdate",
    "ChangeResponse",
    "ChangeDetailResponse",
    "ChangeListResponse",
    "ChangeTagResponse",
    "NotificationPreferenceBase",
    "NotificationPreferenceCreate",
    "NotificationPreferenceUpdate",
    "NotificationPreferenceResponse",
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
]

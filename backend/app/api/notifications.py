"""
Notifications API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Notification, NotificationPreference, User, NotificationChannel
from app.schemas import (
    NotificationCreate, NotificationResponse, NotificationUpdate,
    NotificationPreferenceCreate, NotificationPreferenceResponse, NotificationPreferenceUpdate
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# Notification Preferences endpoints

@router.get("/preferences/{user_id}", response_model=dict)
async def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
    """Get notification preferences for a user"""
    prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).all()
    
    if not prefs:
        return {"items": []}
    
    return {
        "total": len(prefs),
        "items": prefs
    }


@router.post("/preferences", response_model=NotificationPreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_preference(
    preference: NotificationPreferenceCreate,
    db: Session = Depends(get_db)
):
    """Create notification preference for a user"""
    # For now, assume user_id is passed in preference
    db_pref = NotificationPreference(
        user_id=preference.user_id if hasattr(preference, 'user_id') else None,
        channel=NotificationChannel(preference.channel),
        enabled=preference.enabled,
        notify_etrn=preference.notify_etrn,
        notify_epl=preference.notify_epl,
        notify_eed=preference.notify_eed,
        notify_sources=preference.notify_sources,
        digest_mode=preference.digest_mode
    )
    
    db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    
    return db_pref


@router.patch("/preferences/{preference_id}", response_model=NotificationPreferenceResponse)
async def update_notification_preference(
    preference_id: int,
    preference_update: NotificationPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """Update notification preference"""
    db_pref = db.query(NotificationPreference).filter(NotificationPreference.id == preference_id).first()
    
    if not db_pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    update_data = preference_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pref, field, value)
    
    db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    
    return db_pref


# Notifications endpoints

@router.get("/", response_model=dict)
async def list_notifications(
    user_id: int = None,
    is_read: bool = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List notifications"""
    query = db.query(Notification)
    
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    # Order by most recent first
    query = query.order_by(Notification.created_at.desc())
    
    total = query.count()
    notifications = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": notifications
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: int, db: Session = Depends(get_db)):
    """Get a specific notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    db_notification = Notification(
        user_id=notification.user_id,
        change_id=notification.change_id,
        document_id=notification.document_id,
        title=notification.title,
        message=notification.message,
        channel=NotificationChannel(notification.channel)
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    return db_notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db)
):
    """Update a notification"""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    update_data = notification_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    return db_notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """Delete a notification"""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(db_notification)
    db.commit()
    
    return None

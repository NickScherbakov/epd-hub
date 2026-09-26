"""
Changes API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Change, ChangeStatus, ChangeSource
from app.schemas import ChangeCreate, ChangeResponse, ChangeDetailResponse, ChangeUpdate, ChangeListResponse

router = APIRouter(prefix="/api/changes", tags=["changes"])


@router.get("/", response_model=dict)
async def list_changes(
    skip: int = 0,
    limit: int = 20,
    source: str = None,
    status_filter: str = None,
    is_analyzed: bool = None,
    db: Session = Depends(get_db)
):
    """List regulatory changes with optional filters"""
    query = db.query(Change)
    
    # Apply filters
    if source:
        try:
            query = query.filter(Change.source == ChangeSource(source))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
    
    if status_filter:
        try:
            query = query.filter(Change.status == ChangeStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
    
    if is_analyzed is not None:
        query = query.filter(Change.is_analyzed == is_analyzed)
    
    # Order by most recent first
    query = query.order_by(Change.discovered_at.desc())
    
    total = query.count()
    changes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": changes
    }


@router.get("/{change_id}", response_model=ChangeDetailResponse)
async def get_change(change_id: int, db: Session = Depends(get_db)):
    """Get a specific change by ID"""
    change = db.query(Change).filter(Change.id == change_id).first()
    
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")
    
    return change


@router.post("/", response_model=ChangeResponse, status_code=status.HTTP_201_CREATED)
async def create_change(
    change: ChangeCreate,
    db: Session = Depends(get_db)
):
    """Create a new regulatory change"""
    # Validate source
    try:
        source = ChangeSource(change.source)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid source: {change.source}")
    
    db_change = Change(
        title=change.title,
        description=change.description,
        full_content=change.full_content,
        source=source,
        document_id=change.document_id,
        affected_document_types=change.affected_document_types,
        source_url=change.source_url,
        official_link=change.official_link,
        published_date=change.published_date,
        effective_date=change.effective_date
    )
    
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
    
    return db_change


@router.patch("/{change_id}", response_model=ChangeResponse)
async def update_change(
    change_id: int,
    change_update: ChangeUpdate,
    db: Session = Depends(get_db)
):
    """Update a change"""
    db_change = db.query(Change).filter(Change.id == change_id).first()
    
    if not db_change:
        raise HTTPException(status_code=404, detail="Change not found")
    
    update_data = change_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_change, field, value)
    
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
    
    return db_change


@router.delete("/{change_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_change(change_id: int, db: Session = Depends(get_db)):
    """Delete a change"""
    db_change = db.query(Change).filter(Change.id == change_id).first()
    
    if not db_change:
        raise HTTPException(status_code=404, detail="Change not found")
    
    db.delete(db_change)
    db.commit()
    
    return None


@router.get("/{change_id}/mark-analyzed", response_model=ChangeResponse)
async def mark_change_analyzed(change_id: int, db: Session = Depends(get_db)):
    """Mark a change as analyzed"""
    db_change = db.query(Change).filter(Change.id == change_id).first()
    
    if not db_change:
        raise HTTPException(status_code=404, detail="Change not found")
    
    db_change.is_analyzed = True
    db_change.status = ChangeStatus.ANALYZED
    
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
    
    return db_change

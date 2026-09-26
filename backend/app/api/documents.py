"""
Documents API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Document, DocumentType
from app.schemas import DocumentCreate, DocumentResponse, DocumentDetailResponse, DocumentUpdate, DocumentFilterParams

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/", response_model=dict)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    document_type: str = None,
    source_name: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """List all documents with optional filters"""
    query = db.query(Document)
    
    # Apply filters
    if document_type:
        try:
            query = query.filter(Document.document_type == DocumentType(document_type))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
    
    if source_name:
        query = query.filter(Document.source_name.ilike(f"%{source_name}%"))
    
    if is_active is not None:
        query = query.filter(Document.is_active == is_active)
    
    total = query.count()
    documents = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": documents
    }


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document"""
    # Validate document type
    try:
        doc_type = DocumentType(document.document_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document.document_type}")
    
    db_document = Document(
        title=document.title,
        description=document.description,
        document_type=doc_type,
        regulations=document.regulations,
        requirements=document.requirements,
        keywords=document.keywords,
        source_url=document.source_url,
        source_name=document.source_name,
        published_at=document.published_at
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update a document"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(db_document)
    db.commit()
    
    return None

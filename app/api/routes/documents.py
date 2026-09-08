"""Document management and admin routes."""

import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.core.security import sanitize_filename
from app.schemas.documents import DocumentListResponse, DocumentDetailResponse
from app.services.document_service import DocumentService
from app.ingestion.pipeline import IngestionPipeline
from app.retrieval.index_manager import IndexManager

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    items, total = service.list_documents(status=status, category=category, page=page, page_size=page_size)
    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_detail(
    document_id: str,
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    return service.get_document(document_id)


@router.post("/upload")
async def upload_and_ingest_document(
    file: UploadFile = File(...),
    source_id: str = Form(...),
    category_slug: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    document_type: str = Form("faq"),
    db: Session = Depends(get_db),
):
    clean_name = sanitize_filename(file.filename)
    settings.RAW_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = settings.RAW_DIR / clean_name

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        pipeline = IngestionPipeline(db)
        doc = pipeline.ingest_file(
            filepath=temp_path,
            source_id=source_id,
            category_slug=category_slug,
            title=title or clean_name,
            document_type=document_type,
        )

        # Rebuild retrieval index
        idx_mgr = IndexManager.get_instance()
        idx_res = idx_mgr.rebuild_indexes(db)

        return {
            "document_id": str(doc.id),
            "title": doc.title,
            "status": doc.status,
            "chunk_count": len(doc.chunks),
            "index_status": idx_res,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post("/rebuild-indexes")
def trigger_rebuild_indexes(db: Session = Depends(get_db)):
    idx_mgr = IndexManager.get_instance()
    res = idx_mgr.rebuild_indexes(db)
    return res

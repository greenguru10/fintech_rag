"""Source and Category endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.source import Source, Category
from app.schemas.sources import SourceSchema, CategorySchema

router = APIRouter(tags=["Sources & Categories"])


@router.get("/sources", response_model=List[SourceSchema])
def get_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    return [
        SourceSchema(
            id=str(s.id),
            name=s.name,
            authority_level=s.authority_level,
            authority_score=float(s.authority_score),
            source_type=s.source_type,
            base_url=s.base_url,
            active=s.active,
        )
        for s in sources
    ]


@router.get("/categories", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [
        CategorySchema(
            id=c.id,
            slug=c.slug,
            display_name=c.display_name,
            description=c.description,
            active=c.active,
        )
        for c in categories
    ]

"""End-to-end ingestion pipeline."""

from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.exceptions import DocumentValidationError
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.source import Source, Category
from app.ingestion.validators import validate_file
from app.ingestion.parsers.pdf_parser import PDFParser
from app.ingestion.parsers.text_parser import TextParser
from app.ingestion.parsers.markdown_parser import MarkdownParser
from app.ingestion.parsers.html_parser import HTMLParser
from app.ingestion.parsers.docx_parser import DocxParser
from app.ingestion.chunker import FinancialChunker


class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.chunker = FinancialChunker()
        self.parsers = {
            ".pdf": PDFParser(),
            ".txt": TextParser(),
            ".md": MarkdownParser(),
            ".markdown": MarkdownParser(),
            ".html": HTMLParser(),
            ".htm": HTMLParser(),
            ".docx": DocxParser(),
        }

    def ingest_file(
        self,
        filepath: Path,
        source_id: str,
        category_slug: str | None = None,
        title: str | None = None,
        source_url: str | None = None,
        document_type: str = "faq",
        version_label: str | None = None,
        publication_date = None,
        effective_date = None,
        last_updated = None,
    ) -> Document:
        ext, size_bytes, checksum = validate_file(filepath, filepath.name)

        # Check duplicate
        existing = self.db.query(Document).filter_by(content_hash=checksum).first()
        if existing:
            return existing

        # Verify source
        source = self.db.query(Source).filter_by(id=source_id).first()
        if not source:
            raise DocumentValidationError(f"Source ID '{source_id}' does not exist.")

        # Resolve category
        category = None
        if category_slug:
            category = self.db.query(Category).filter_by(slug=category_slug).first()

        doc_title = title or filepath.stem.replace("-", " ").replace("_", " ").title()

        # Parse pages
        parser = self.parsers.get(ext)
        if not parser:
            raise DocumentValidationError(f"No parser available for extension '{ext}'.")

        parsed_pages = parser.parse(filepath)
        full_text = "\n\n".join(p.text for p in parsed_pages)

        # Create Document record
        doc = Document(
            source_id=source.id,
            category_id=category.id if category else None,
            title=doc_title,
            document_type=document_type,
            source_url=source_url or source.base_url,
            local_path=str(filepath),
            content_hash=checksum,
            version_label=version_label,
            status="active",
            extracted_text=full_text[:5000],  # preview
            extraction_quality=1.0,
            publication_date=publication_date,
            effective_date=effective_date,
            last_updated=last_updated,
        )
        self.db.add(doc)
        self.db.flush()

        # Chunk document
        raw_chunks = self.chunker.chunk_document_pages(parsed_pages)
        for seq, rc in enumerate(raw_chunks, start=1):
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_sequence=seq,
                title=doc_title,
                section=rc.section,
                page_start=rc.page_start,
                page_end=rc.page_end,
                raw_text=rc.raw_text,
                normalized_text=rc.normalized_text,
                token_count=rc.token_count,
                active=True,
                metadata_json={
                    "source_name": source.name,
                    "authority_level": source.authority_level,
                    "authority_score": float(source.authority_score),
                    "category": category.slug if category else None,
                    "source_url": doc.source_url,
                }
            )
            self.db.add(chunk)

        self.db.commit()
        self.db.refresh(doc)
        return doc

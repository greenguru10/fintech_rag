"""PyMuPDF (fitz) PDF parser preserving page numbers and typography."""

from pathlib import Path
from typing import List
try:
    import pymupdf as fitz
except ImportError:
    import fitz
from app.ingestion.parsers.base import BaseParser, ParsedPage
from app.core.exceptions import DocumentValidationError


class PDFParser(BaseParser):
    def parse(self, filepath: Path) -> List[ParsedPage]:
        try:
            doc = fitz.open(str(filepath))
        except Exception as e:
            raise DocumentValidationError(f"Failed to open PDF file: {e}")

        pages: List[ParsedPage] = []
        try:
            for page_idx, page in enumerate(doc, start=1):
                text = page.get_text("text")
                if text and text.strip():
                    pages.append(ParsedPage(text=text.strip(), page_number=page_idx))
        finally:
            doc.close()

        if not pages:
            raise DocumentValidationError("PDF contains no extractable text (it may be a scanned image without OCR).")

        return pages

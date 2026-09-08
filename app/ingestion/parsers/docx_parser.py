"""DOCX parser using python-docx."""

from pathlib import Path
from typing import List
import docx
from app.ingestion.parsers.base import BaseParser, ParsedPage
from app.core.exceptions import DocumentValidationError


class DocxParser(BaseParser):
    def parse(self, filepath: Path) -> List[ParsedPage]:
        try:
            doc = docx.Document(str(filepath))
        except Exception as e:
            raise DocumentValidationError(f"Failed to open DOCX file: {e}")

        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if not paragraphs:
            raise DocumentValidationError("DOCX file contains no readable paragraphs.")

        full_text = "\n\n".join(paragraphs)
        return [ParsedPage(text=full_text, page_number=1)]

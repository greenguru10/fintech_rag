"""Plain text parser with encoding detection."""

from pathlib import Path
from typing import List
from app.ingestion.parsers.base import BaseParser, ParsedPage
from app.core.exceptions import DocumentValidationError


class TextParser(BaseParser):
    def parse(self, filepath: Path) -> List[ParsedPage]:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        content = None

        for enc in encodings:
            try:
                content = filepath.read_text(encoding=enc)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if content is None:
            raise DocumentValidationError("Could not decode plain text file with supported encodings.")

        if not content.strip():
            raise DocumentValidationError("Text file is empty.")

        return [ParsedPage(text=content.strip(), page_number=1)]

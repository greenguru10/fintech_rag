"""Markdown parser preserving heading structures."""

from pathlib import Path
from typing import List
from app.ingestion.parsers.base import BaseParser, ParsedPage
from app.core.exceptions import DocumentValidationError


class MarkdownParser(BaseParser):
    def parse(self, filepath: Path) -> List[ParsedPage]:
        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = filepath.read_text(encoding="latin-1")
            except Exception as e:
                raise DocumentValidationError(f"Failed to read Markdown file: {e}")

        if not content.strip():
            raise DocumentValidationError("Markdown file is empty.")

        return [ParsedPage(text=content.strip(), page_number=1)]

"""HTML parser using BeautifulSoup stripping boilerplate."""

from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
from app.ingestion.parsers.base import BaseParser, ParsedPage
from app.core.exceptions import DocumentValidationError


class HTMLParser(BaseParser):
    def parse(self, filepath: Path) -> List[ParsedPage]:
        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = filepath.read_text(encoding="latin-1")
            except Exception as e:
                raise DocumentValidationError(f"Failed to read HTML file: {e}")

        soup = BeautifulSoup(content, "lxml")

        # Strip scripts, styles, headers, footers, nav, aside, cookie banners
        for element in soup(["script", "style", "nav", "footer", "aside", "header", "form", "noscript"]):
            element.decompose()

        # Extract text with line breaks
        text = soup.get_text(separator="\n", strip=True)

        if not text:
            raise DocumentValidationError("HTML contains no readable text after removing boilerplate elements.")

        return [ParsedPage(text=text, page_number=1)]

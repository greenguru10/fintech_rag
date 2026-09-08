"""Base class for document parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class ParsedPage:
    def __init__(self, text: str, page_number: int, metadata: Dict[str, Any] | None = None):
        self.text = text
        self.page_number = page_number
        self.metadata = metadata or {}


class BaseParser(ABC):
    @abstractmethod
    def parse(self, filepath: Path) -> List[ParsedPage]:
        """Parses a file into a list of page-aware text sections."""
        pass

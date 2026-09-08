"""Text cleaner for document ingestion."""

import re
import unicodedata


def clean_document_text(text: str) -> str:
    """Normalizes Unicode, removes repeated line noise and pagination artifacts."""
    if not text:
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Normalize carriage returns and tabs
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

    # Remove repeated page number lines (e.g. 'Page 1 of 12', '--- 2 ---')
    text = re.sub(r"(?i)\bpage\s+\d+\s+(?:of\s+\d+)?\b", "", text)
    text = re.sub(r"^[-\s_]{3,}\s*\d+\s*[-\s_]{3,}$", "", text, flags=re.MULTILINE)

    # Collapse multiple blank lines into two
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing/leading whitespace per line
    lines = [line.strip() for line in text.split("\n")]
    cleaned = "\n".join(lines).strip()

    return cleaned

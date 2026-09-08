"""File security and format validators."""

import hashlib
from pathlib import Path
from typing import Tuple
from app.core.exceptions import DocumentValidationError
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".html", ".htm", ".docx"}


def sha256_file(filepath: Path) -> str:
    """Computes SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_file(filepath: Path, original_filename: str) -> Tuple[str, int, str]:
    """Validates file extension, size limit, and returns (extension, size_bytes, sha256)."""
    if not filepath.exists():
        raise DocumentValidationError(f"File not found: {filepath}")

    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentValidationError(
            f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    size = filepath.stat().st_size
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if size > max_bytes:
        raise DocumentValidationError(
            f"File size {size / (1024*1024):.2f}MB exceeds maximum limit of {settings.MAX_UPLOAD_MB}MB."
        )
    if size < 50:
        raise DocumentValidationError("File is empty or too small to contain valid financial document content.")

    # Read header magic bytes
    with open(filepath, "rb") as f:
        header = f.read(16)

    if ext == ".pdf" and not header.startswith(b"%PDF"):
        raise DocumentValidationError("Invalid PDF file header.")

    checksum = sha256_file(filepath)
    return ext, size, checksum

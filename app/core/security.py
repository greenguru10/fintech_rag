"""Security helpers and admin authentication."""

from pathlib import Path
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


async def verify_admin_key(api_key: str = Security(api_key_header)) -> bool:
    """Verifies admin API key for protected routes."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Admin-API-Key header",
        )
    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Admin API Key",
        )
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitizes uploaded filename to prevent directory traversal attacks."""
    p = Path(filename)
    clean_name = p.name.replace("..", "").replace("/", "").replace("\\", "")
    return clean_name

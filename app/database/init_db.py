"""Database table initialization helper."""

from app.database.base import Base
from app.database.session import engine
import app.models  # Ensure all models are registered


def init_db():
    """Creates all database tables defined in models."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")

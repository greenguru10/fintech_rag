#!/usr/bin/env python
"""Seed initial sources and categories into the database."""

import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.models.source import Source, Category
from app.core.config import settings


def seed_sources_and_categories():
    config_file = settings.CONFIGS_DIR / "source_registry.yaml"
    if not config_file.exists():
        print(f"Error: Config file '{config_file}' not found.")
        return

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    db = SessionLocal()
    try:
        # Seed categories
        for cat_data in data.get("categories", []):
            existing = db.query(Category).filter_by(slug=cat_data["slug"]).first()
            if not existing:
                cat = Category(
                    slug=cat_data["slug"],
                    display_name=cat_data["display_name"],
                    description=cat_data.get("description"),
                    active=True,
                )
                db.add(cat)
                print(f"Added category: {cat_data['display_name']} ({cat_data['slug']})")

        # Seed sources
        for src_data in data.get("sources", []):
            existing = db.query(Source).filter_by(name=src_data["name"]).first()
            if not existing:
                src = Source(
                    name=src_data["name"],
                    authority_level=src_data["authority_level"],
                    authority_score=src_data["authority_score"],
                    source_type=src_data["source_type"],
                    base_url=src_data.get("base_url"),
                    active=True,
                )
                db.add(src)
                print(f"Added source: {src_data['name']} (Tier {src_data['authority_level']})")

        db.commit()
        print("Successfully seeded sources and categories!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding sources: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_sources_and_categories()

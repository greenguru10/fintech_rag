#!/usr/bin/env python
"""Ingests all documents from data/raw/ into the database and builds retrieval indexes."""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.models.source import Source, Category
from app.ingestion.pipeline import IngestionPipeline
from app.retrieval.index_manager import IndexManager
from app.core.config import settings

# Mapping prefix to source and category
SOURCE_CATEGORY_MAP = {
    "rbi_": ("Reserve Bank of India", "banking"),
    "sebi_": ("Securities and Exchange Board of India", "investments"),
    "irdai_": ("Insurance Regulatory and Development Authority of India", "insurance"),
    "incometax_": ("Income Tax Department of India", "taxation"),
    "npci_": ("National Payments Corporation of India", "banking"),
    "pfrda_": ("Pension Fund Regulatory and Development Authority", "personal_finance"),
}

DEFAULT_SOURCES = [
    {"name": "Reserve Bank of India", "base_url": "https://www.rbi.org.in", "authority_level": "A", "authority_score": 1.0, "source_type": "central_bank"},
    {"name": "Securities and Exchange Board of India", "base_url": "https://www.sebi.gov.in", "authority_level": "A", "authority_score": 1.0, "source_type": "securities_regulator"},
    {"name": "Insurance Regulatory and Development Authority of India", "base_url": "https://irdai.gov.in", "authority_level": "A", "authority_score": 1.0, "source_type": "insurance_regulator"},
    {"name": "Income Tax Department of India", "base_url": "https://incometaxindia.gov.in", "authority_level": "A", "authority_score": 1.0, "source_type": "tax_authority"},
    {"name": "National Payments Corporation of India", "base_url": "https://www.npci.org.in", "authority_level": "A", "authority_score": 1.0, "source_type": "payments_regulator"},
    {"name": "Pension Fund Regulatory and Development Authority", "base_url": "https://www.pfrda.org.in", "authority_level": "A", "authority_score": 1.0, "source_type": "pension_regulator"},
    {"name": "Association of Mutual Funds in India", "base_url": "https://www.amfiindia.com", "authority_level": "B", "authority_score": 0.85, "source_type": "industry_association"},
]

DEFAULT_CATEGORIES = [
    {"slug": "banking", "display_name": "Banking & Digital Payments", "description": "Savings, Deposits, UPI, KYC, NEFT, RTGS"},
    {"slug": "loans", "display_name": "Loans & Mortgages", "description": "Home Loans, EMI, Prepayment, Fixed vs Floating"},
    {"slug": "investments", "display_name": "Investments & Wealth", "description": "Mutual Funds, SIP, Stocks, SGB, Demat, CAGR"},
    {"slug": "insurance", "display_name": "Life & Health Insurance", "description": "Term, Health, Mediclaim, Room Rent, Co-pay"},
    {"slug": "taxation", "display_name": "Taxation & Regimes", "description": "Old vs New Regime, 80C, 80D, Capital Gains, TDS"},
    {"slug": "credit_cards", "display_name": "Credit Cards & Credit Score", "description": "Billing, Minimum Due, CIBIL, Interest Free"},
    {"slug": "personal_finance", "display_name": "Personal Finance & Retirement", "description": "PPF, EPF, NPS, Emergency Funds, Budgeting"},
    {"slug": "financial_regulation", "display_name": "Consumer Rights & Redressal", "description": "RBI Ombudsman, SEBI SCORES, Zero Liability"},
]


def seed_sources_and_categories(db):
    for src in DEFAULT_SOURCES:
        if not db.query(Source).filter_by(name=src["name"]).first():
            db.add(Source(**src))
    for cat in DEFAULT_CATEGORIES:
        if not db.query(Category).filter_by(slug=cat["slug"]).first():
            db.add(Category(**cat))
    db.commit()


def ingest_all_raw_documents():
    raw_dir = settings.RAW_DIR
    if not raw_dir.exists():
        print(f"Directory '{raw_dir}' does not exist.")
        return

    print("Initializing database tables...")
    init_db()

    db = SessionLocal()
    seed_sources_and_categories(db)
    pipeline = IngestionPipeline(db)

    print("Ingesting all raw documents from:", raw_dir)
    total_docs = 0

    for filepath in sorted(raw_dir.glob("*.md")):
        fname = filepath.name.lower()

        # Determine source and category
        source_name = "Reserve Bank of India"
        category_slug = "banking"

        for prefix, (src, cat) in SOURCE_CATEGORY_MAP.items():
            if fname.startswith(prefix):
                source_name = src
                category_slug = cat
                break

        # Specific category fine-tuning based on file keywords
        if "loan" in fname or "mortgage" in fname or "emi" in fname:
            category_slug = "loans"
        elif "credit_card" in fname or "cibil" in fname:
            category_slug = "credit_cards"
        elif "tax" in fname:
            category_slug = "taxation"
        elif "insurance" in fname:
            category_slug = "insurance"
        elif "personal_finance" in fname or "retirement" in fname or "pension" in fname:
            category_slug = "personal_finance"
        elif "grievance" in fname or "consumer" in fname or "ombudsman" in fname:
            category_slug = "financial_regulation"
        elif "stock" in fname or "securities" in fname or "mutual_fund" in fname or "sip" in fname:
            category_slug = "investments"

        source = db.query(Source).filter_by(name=source_name).first()
        if not source:
            source = db.query(Source).first()

        title = filepath.stem.replace("_", " ").title()

        doc = pipeline.ingest_file(
            filepath=filepath,
            source_id=str(source.id),
            category_slug=category_slug,
            title=title,
            publication_date=date(2025, 1, 1),
            last_updated=date(2026, 1, 1),
        )
        db.commit()
        total_docs += 1
        print(f"  [{total_docs}] Ingested '{doc.title}' ({category_slug}) -> {len(doc.chunks)} chunks", flush=True)

    # Rebuild indexes
    idx_mgr = IndexManager.get_instance()
    res = idx_mgr.rebuild_indexes(db)
    print(f"\nSuccessfully built retrieval index with {res['chunk_count']} active chunks across {total_docs} documents!", flush=True)

    db.close()


if __name__ == "__main__":
    ingest_all_raw_documents()


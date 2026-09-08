"""Financial terminology dictionary loader."""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from app.core.config import settings


class FinancialTerminology:
    _instance = None

    def __init__(self):
        config_path = settings.CONFIGS_DIR / "financial_terms.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        self.abbreviations: Dict[str, Dict[str, str]] = data.get("abbreviations", {})
        self.synonyms: Dict[str, List[str]] = data.get("synonyms", {})

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_expansion(self, term: str) -> str | None:
        term_clean = term.lower().strip()
        if term_clean in self.abbreviations:
            return self.abbreviations[term_clean].get("expansion")
        return None

    def get_synonyms(self, term: str) -> List[str]:
        term_clean = term.lower().strip().replace(" ", "_")
        return self.synonyms.get(term_clean, [])

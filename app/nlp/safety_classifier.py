"""Safety and unsupported advisory query classifier."""

import re
import yaml
from typing import Tuple, List
from app.core.config import settings


class SafetyClassifier:
    def __init__(self):
        config_path = settings.CONFIGS_DIR / "safety_rules.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        self.patterns = [re.compile(p, re.IGNORECASE) for p in data.get("unsupported_patterns", [])]
        self.templates = data.get("safety_templates", {})

    def check_safety(self, query: str) -> Tuple[bool, str | None, str | None]:
        """Returns (is_unsafe, risk_type, refusal_text)."""
        query_clean = query.strip()

        # Check against unsupported advisory patterns
        for pattern in self.patterns:
            if pattern.search(query_clean):
                if any(k in query_clean.lower() for k in ["tax", "evade", "illegal", "launder"]):
                    return True, "illegal_activity", self.templates.get("illegal_activity")
                return True, "personalized_advice", self.templates.get("personalized_advice")

        return False, None, None

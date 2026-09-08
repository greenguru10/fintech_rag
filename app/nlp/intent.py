"""Comprehensive intent classifier with conversational greetings and flexible fallback."""

import re
import yaml
from typing import Tuple, Dict, Any, List
from app.core.config import settings
from app.core.constants import IntentType
from app.nlp.safety_classifier import SafetyClassifier
from app.nlp.entities import FinancialEntityExtractor


GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b",
    r"^(who are you|what can you do|how do you work|what is this|help me|tell me about yourself)\b",
    r"^(what topics can i ask|what do you know|features)\b",
]


class IntentClassifier:
    def __init__(self):
        self.safety_classifier = SafetyClassifier()
        self.entity_extractor = FinancialEntityExtractor()

        config_path = settings.CONFIGS_DIR / "intent_rules.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.rules = yaml.safe_load(f) or {}
        else:
            self.rules = {}

    def classify_intent(self, query: str) -> Tuple[IntentType, float, Dict[str, Any]]:
        """Classifies intent with confidence score and metadata."""
        query_clean = query.strip()
        query_lower = query_clean.lower()
        entities = self.entity_extractor.extract_entities(query_clean)

        # 1. Conversational Greeting check
        for gp in GREETING_PATTERNS:
            if re.search(gp, query_lower):
                greeting_text = (
                    "Hello! I am the **FinTech Verified Knowledge & Calculation Engine**.\n\n"
                    "I provide 100% deterministic, evidence-grounded information strictly from official regulatory sources (**RBI, SEBI, IRDAI, Income Tax Dept, NPCI, AMFI**).\n\n"
                    "Here is what you can ask me:\n"
                    "- **Banking & Digital Payments**: *'How does NEFT work?'*, *'What is RTGS?'*, *'What are UPI limits?'*, *'How to complete KYC?'*, *'What is DICGC deposit insurance?'*\n"
                    "- **Loans & Credit**: *'What is an EMI?'*, *'Fixed vs floating rates'*, *'What is CIBIL score?'*, *'Foreclosure rules'*\n"
                    "- **Investments & Wealth**: *'What is a SIP?'*, *'FD vs mutual fund'*, *'What is CAGR?'*, *'What are Sovereign Gold Bonds?'*\n"
                    "- **Insurance & Tax**: *'Term vs health insurance'*, *'What is a deductible?'*, *'Old vs new tax regime'*, *'What is TDS?'*\n"
                    "- **Financial Calculations**: *'Calculate EMI for ₹10 lakh at 9% for 15 years'*, *'Calculate SIP for ₹5,000 at 12% for 10 years'*, *'Compound interest on ₹1 lakh at 8% for 5 years'*\n\n"
                    "How can I assist you with your financial queries today?"
                )
                return IntentType.EXPLANATION, 0.99, {"is_greeting": True, "greeting_text": greeting_text, "entities": entities}

        # 2. Safety check
        is_unsafe, risk_type, refusal_text = self.safety_classifier.check_safety(query_clean)
        if is_unsafe:
            return IntentType.UNSUPPORTED, 0.98, {"risk_type": risk_type, "refusal_text": refusal_text}

        # 3. Calculation patterns
        calc_keywords = [
            "calculate", "calculat", "compute", "what will", "how much will", "emi for",
            "sip for", "interest on", "interest of", "intreset", "intrest", "cagr from",
            "compound interest", "simple interest", "percentage of", "percent of", "% of",
            "how much is", "what is 1%", "what is 5%", "calc "
        ]
        has_calc_word = any(k in query_lower for k in calc_keywords)
        has_numbers = bool(entities["money"] or entities["rates"] or entities["tenures"])

        if has_calc_word and has_numbers:
            return IntentType.CALCULATION, 0.95, {"entities": entities}
        elif has_calc_word and not has_numbers:
            return IntentType.CALCULATION, 0.85, {"entities": entities, "missing_inputs": True}

        # 4. Comparison patterns (e.g. "X vs Y", "difference between X and Y", "compare X and Y")
        if any(w in query_lower for w in [" vs ", " versus ", "difference between", "compare ", "differ from"]):
            return IntentType.COMPARISON, 0.92, {"entities": entities}

        # 5. Procedure patterns (e.g. "how to", "steps to", "how do i", "process for")
        if any(w in query_lower for w in ["how to", "how do i", "how can i", "steps to", "steps for", "process for", "procedure for"]):
            return IntentType.PROCEDURE, 0.90, {"entities": entities}

        # 6. Definition patterns (e.g. "what is", "define", "meaning of", "what does")
        if any(w in query_lower for w in ["what is", "what are", "meaning of", "define ", "definition of", "stands for"]):
            return IntentType.DEFINITION, 0.92, {"entities": entities}

        # 7. Rules check from YAML
        for intent_name, rule_data in self.rules.items():
            patterns = rule_data.get("patterns", [])
            for pat in patterns:
                if re.search(pat, query_lower):
                    try:
                        return IntentType(intent_name), 0.88, {"rule": pat, "entities": entities}
                    except ValueError:
                        pass

        # 8. Broad financial topic queries (e.g. "tax", "loan", "interest", "cibil", "sip", "banking")
        words = query_lower.split()
        if len(words) <= 3 and any(w in query_lower for w in ["interest", "charge", "tax", "fee", "loan", "rate", "card", "fund", "bank", "account", "invest", "cibil", "insurance", "upi", "emi"]):
            return IntentType.EXPLANATION, 0.90, {"entities": entities, "is_broad_overview": True}

        # 9. General financial explanation with entities
        if entities["products"]:
            return IntentType.EXPLANATION, 0.88, {"entities": entities}

        return IntentType.GENERAL_FINANCE, 0.80, {"entities": entities}

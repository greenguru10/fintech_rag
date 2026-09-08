"""Comprehensive rule-based financial entity extractor."""

import re
from typing import List, Dict, Any


class FinancialEntityExtractor:
    def __init__(self):
        self.money_pattern = re.compile(
            r"(?:(?:Rs\.?|₹|INR)\s*)?(\d+(?:,\d+)*(?:\.\d+)?)\s*(lakhs?|lacs?|crores?|cr|k|rs\.?|rupees|inr|/-)?",
            re.IGNORECASE,
        )
        self.rate_pattern = re.compile(
            r"(?:(?:rate\s+of|rate|interest\s+of|interest|intreset\s+of|intreset|intrest\s+of|intrest|at)\s+(\d+(?:\.\d+)?))|(\d+(?:\.\d+)?)\s*(?:%|percent|percentage|pct|annual)",
            re.IGNORECASE,
        )
        self.tenure_pattern = re.compile(
            r"(?:(?:in|for)\s+)?(\d+(?:\.\d+)?)\s*(years?|yrs?|yera?|yr|months?|mos?|days?|weeks?)",
            re.IGNORECASE,
        )
        
        self.products = [
            # Banking & Payments
            "savings account", "current account", "fixed deposit", "fd", "recurring deposit", "rd",
            "senior citizen savings scheme", "scss", "neft", "rtgs", "imps", "upi", "upi lite",
            "upi 123pay", "vpa", "upi pin", "kyc", "v-cip", "dicgc", "deposit insurance", "dormant account",
            "nomination", "joint account",
            # Loans & Mortgages
            "emi", "loan", "home loan", "personal loan", "car loan", "education loan", "mortgage",
            "prepayment", "foreclosure", "moratorium", "floating rate", "fixed rate", "zero cost emi",
            "no cost emi", "cibil", "credit score", "credit rating", "cibil score",
            # Credit Cards
            "credit card", "billing cycle", "grace period", "minimum due", "mad", "cash advance",
            "markup fee", "dynamic currency conversion", "dcc", "chargeback", "reward points",
            # Investments & Wealth
            "mutual fund", "sip", "swp", "stp", "cagr", "nav", "expense ratio", "ter", "elss",
            "index fund", "active fund", "equity fund", "debt fund", "hybrid fund", "liquid fund",
            "demat account", "trading account", "ipo", "asba", "dividend", "stock split", "bonus shares",
            "sovereign gold bond", "sgb", "g-sec", "treasury bill", "t-bill", "bonds",
            # Insurance
            "insurance", "life insurance", "term insurance", "whole life", "ulip", "health insurance",
            "mediclaim", "deductible", "room rent capping", "co-pay", "pre-existing disease", "ped",
            "waiting period", "no claim bonus", "ncb", "claim settlement ratio", "csr", "cashless",
            "reimbursement", "third party administrator", "tpa",
            # Taxation
            "income tax", "tds", "tcs", "old tax regime", "new tax regime", "section 80c", "section 80d",
            "section 80tta", "section 24b", "capital gains", "ltcg", "stcg", "form 16", "form 26as",
            "ais", "advance tax", "itr", "financial year", "assessment year",
            # Personal Finance & Regulation
            "nps", "tier 1", "tier 2", "ppf", "epf", "vpf", "emergency fund", "50-30-20 rule",
            "inflation", "compounding", "compound interest", "simple interest", "ombudsman", "rb-ios",
            "sebi scores", "bima bharosa", "zero liability",
        ]

    def extract_entities(self, text: str) -> Dict[str, Any]:
        text_clean = text.lower()
        entities = {
            "money": [],
            "rates": [],
            "tenures": [],
            "products": [],
            "acronyms": [],
        }

        # Extract rates first
        rate_spans = []
        for match in self.rate_pattern.finditer(text):
            num = match.group(1) or match.group(2)
            if num:
                entities["rates"].append(num.strip())
                rate_spans.append(match.span())

        # Extract tenures second
        tenure_spans = []
        for match in self.tenure_pattern.finditer(text):
            entities["tenures"].append(match.group(0).strip())
            tenure_spans.append(match.span())

        # Extract money (excluding spans that were part of rates or tenures)
        for match in self.money_pattern.finditer(text):
            m_start, m_end = match.span()
            if any(r_start <= m_start < r_end or r_start < m_end <= r_end for r_start, r_end in rate_spans):
                continue
            if any(t_start <= m_start < t_end or t_start < m_end <= t_end for t_start, t_end in tenure_spans):
                continue
            val_str = match.group(0).strip()
            if not val_str:
                continue
            has_curr = any(char in val_str.lower() for char in ["₹", "rs", "inr", "rupee", "lakh", "lac", "crore", "cr", ","])
            is_num = val_str.replace(".", "").isdigit()
            if has_curr or is_num:
                entities["money"].append(val_str)

        # Extract recognized products (longer matches first)
        matched_products = []
        for prod in sorted(self.products, key=len, reverse=True):
            if re.search(r"\b" + re.escape(prod) + r"\b", text_clean):
                if not any(prod in existing for existing in matched_products):
                    matched_products.append(prod)

        entities["products"] = matched_products
        return entities

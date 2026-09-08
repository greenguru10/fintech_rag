"""Application constants and enumerations for the FinTech No-LLM Chatbot."""

from enum import Enum


class AuthorityLevel(str, Enum):
    A = "A"  # Regulators (RBI, SEBI, IRDAI, IT Dept, Gov) - Score: 1.00
    B = "B"  # Official Statutory / Regulated bodies (AMFI, NSE, BSE) - Score: 0.90
    C = "C"  # Official financial institution disclosures - Score: 0.80
    D = "D"  # Approved nonprofit / financial literacy material - Score: 0.65
    E = "E"  # Unverified - Not eligible by default


AUTHORITY_SCORES = {
    AuthorityLevel.A: 1.00,
    AuthorityLevel.B: 0.90,
    AuthorityLevel.C: 0.80,
    AuthorityLevel.D: 0.65,
    AuthorityLevel.E: 0.00,
}


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUPERSEDED = "superseded"
    FAILED = "failed"


class DocumentType(str, Enum):
    FAQ = "faq"
    CIRCULAR = "circular"
    GUIDE = "guide"
    POLICY = "policy"
    TERMS = "terms"
    EDUCATIONAL = "educational"


class IntentType(str, Enum):
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    CALCULATION = "calculation"
    PROCEDURE = "procedure"
    ELIGIBILITY = "eligibility"
    FEES = "fees"
    INTEREST = "interest"
    RISK = "risk"
    REGULATION = "regulation"
    TRANSACTION = "transaction"
    INVESTMENT = "investment"
    LOAN = "loan"
    CREDIT_CARD = "credit_card"
    INSURANCE = "insurance"
    TAX = "tax"
    GENERAL_FINANCE = "general_finance"
    UNSUPPORTED = "unsupported"
    CLARIFICATION_NEEDED = "clarification_needed"


class ResponseMode(str, Enum):
    EVIDENCE_ANSWER = "evidence_answer"
    CALCULATION = "calculation"
    COMPARISON = "comparison"
    PROCEDURE = "procedure"
    CLARIFICATION = "clarification"
    SAFETY_REFUSAL = "safety_refusal"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class ConfidenceLabel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNSUPPORTED = "unsupported"


class CalculationType(str, Enum):
    EMI = "emi"
    AMORTIZATION = "amortization"
    SIMPLE_INTEREST = "simple_interest"
    COMPOUND_INTEREST = "compound_interest"
    SIP = "sip"
    CAGR = "cagr"

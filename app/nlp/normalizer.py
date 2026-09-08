"""Text normalization, tokenization, and sentence splitting."""

import re
import unicodedata
from typing import List

# Finance-bearing stopwords that MUST be preserved
FINANCE_PRESERVED_WORDS = {
    "interest", "rate", "due", "tax", "fund", "loan", "credit", "account",
    "term", "risk", "claim", "minimum", "annual", "fixed", "monthly", "growth",
    "charge", "fee", "penalty", "return", "gain", "deposit", "insurance", "plan",
    "not", "no", "vs", "difference", "between"
}

GENERIC_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what", "which",
    "this", "that", "these", "those", "then", "just", "so", "than", "such",
    "both", "through", "during", "before", "after", "above", "below", "to", "from",
    "up", "down", "in", "out", "on", "off", "over", "under", "again", "further",
    "once", "here", "there", "when", "where", "why", "how", "all", "any", "each",
    "few", "more", "most", "other", "some", "be", "is", "am", "are", "was", "were",
    "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "would", "should", "could", "ought", "i", "you", "he", "she", "we", "they", "me"
}


def normalize_text(text: str) -> str:
    """Normalizes Unicode, currency symbols, and whitespace."""
    if not text:
        return ""
    # Normalize unicode
    norm = unicodedata.normalize("NFKC", text)
    # Replace rupees and currency symbols
    norm = norm.replace("₹", " Rs ").replace("INR", " Rs ")
    # Replace non-breaking spaces and redundant whitespaces
    norm = re.sub(r"\s+", " ", norm).strip()
    return norm


def tokenize_for_search(text: str, remove_stopwords: bool = True) -> List[str]:
    """Tokenizes text preserving numbers, acronyms, decimals, percentages, and financial stopwords."""
    norm = normalize_text(text).lower()
    # Extract alphanumeric tokens, percentages, and decimals
    tokens = re.findall(r"\b[a-z0-9]+(?:[\.\%][a-z0-9]+)?\b", norm)

    if remove_stopwords:
        tokens = [
            t for t in tokens
            if t in FINANCE_PRESERVED_WORDS or t not in GENERIC_STOPWORDS
        ]
    return tokens


def split_sentences(text: str) -> List[str]:
    """Splits text into sentences accurately preserving financial abbreviations and numbers."""
    if not text:
        return []
    clean = normalize_text(text)
    # Regex splitting on punctuation followed by space or capital letter, avoiding e.g., Rs., Dr., vs., etc.
    sentence_end = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'₹])|(?<=\n\n)|(?<=\n[-*•]\s)')
    raw_sentences = sentence_end.split(clean)

    sentences = []
    for s in raw_sentences:
        s_strip = s.strip()
        if len(s_strip) >= 10:  # meaningful sentence length
            sentences.append(s_strip)
    return sentences if sentences else [clean]

"""Acronym and abbreviation expansion."""

import re
from app.nlp.terminology import FinancialTerminology


def expand_abbreviations(text: str) -> str:
    """Expands recognized financial abbreviations into full definitions (e.g. EMI -> Equated Monthly Instalment)."""
    term_dict = FinancialTerminology.get_instance()
    words = re.findall(r"\b[A-Za-z]+\b", text)
    expanded_parts = []

    for word in words:
        expansion = term_dict.get_expansion(word)
        if expansion:
            expanded_parts.append(f"{word.lower()} {expansion.lower()}")
        else:
            expanded_parts.append(word.lower())

    return " ".join(expanded_parts)

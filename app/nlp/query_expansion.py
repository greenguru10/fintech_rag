"""Deterministic query expansion using financial abbreviations and synonyms."""

from app.nlp.terminology import FinancialTerminology
from app.nlp.normalizer import tokenize_for_search


def expand_query(query: str) -> str:
    """Expands query with domain abbreviations and up to 2 approved synonyms."""
    terms_dict = FinancialTerminology.get_instance()
    tokens = tokenize_for_search(query, remove_stopwords=False)
    expanded_tokens = list(tokens)

    for token in tokens:
        # Check abbreviation expansion
        expansion = terms_dict.get_expansion(token)
        if expansion:
            expanded_tokens.extend(expansion.split())

        # Check synonyms
        synonyms = terms_dict.get_synonyms(token)
        for syn in synonyms[:2]:
            expanded_tokens.extend(syn.split())

    return " ".join(dict.fromkeys(expanded_tokens))  # preserve order & unique

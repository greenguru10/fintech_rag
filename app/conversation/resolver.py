"""Deterministic pronoun and reference resolver for follow-up questions."""

import re
from typing import Tuple
from app.conversation.state import ConversationState


REFERENCE_TERMS = ["it", "this", "that", "they", "them", "those", "the same", "its", "their"]


def resolve_follow_up(query: str, state: ConversationState | None) -> Tuple[str, bool, str | None]:
    """Resolves pronouns/references deterministically from session context.

    Returns: (rewritten_query, is_resolved, resolved_entity)
    """
    if not state or not state.previous_entities:
        return query, False, None

    query_lower = query.lower()
    words = re.findall(r"\b[a-z]+\b", query_lower)

    # Check for pronoun reference
    contains_ref = any(ref in words for ref in REFERENCE_TERMS)
    is_short_follow_up = len(words) <= 5 and any(w in words for w in ["calculate", "work", "mean", "different", "process", "steps", "how"])

    if contains_ref or is_short_follow_up:
        candidate_entity = state.previous_entities[0]
        # Replace reference pronoun with entity
        rewritten = query
        for ref in REFERENCE_TERMS:
            pattern = re.compile(rf"\b{ref}\b", re.IGNORECASE)
            if pattern.search(rewritten):
                rewritten = pattern.sub(candidate_entity, rewritten)
                return rewritten, True, candidate_entity

        # If it was a short follow up like "How is it calculated?" without replacement
        if candidate_entity.lower() not in rewritten.lower():
            rewritten = f"{rewritten.rstrip('?')} for {candidate_entity}?"
            return rewritten, True, candidate_entity

    return query, False, None

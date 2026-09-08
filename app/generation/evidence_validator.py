"""Evidence grounding and hallucination prevention validator."""

from typing import List, Dict, Any


def validate_answer_evidence(
    answer_text: str,
    selected_evidence: List[Dict[str, Any]],
    is_template_or_calc: bool = False,
) -> bool:
    """Verifies that an answer contains valid evidence grounding."""
    if is_template_or_calc:
        return True

    if not selected_evidence:
        return False

    # Check that at least one evidence sentence excerpt appears in or grounds the answer
    has_match = False
    for ev in selected_evidence:
        sent = ev.get("sentence_text", "")
        # Take key words from the sentence
        words = [w.lower() for w in sent.split() if len(w) > 4]
        if words and sum(1 for w in words if w in answer_text.lower()) >= min(3, len(words)):
            has_match = True
            break

    return has_match

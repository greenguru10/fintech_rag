"""Multi-factor confidence scoring."""

from typing import List, Dict, Any, Tuple
from app.core.constants import ConfidenceLabel


class ConfidenceScorer:
    def calculate_confidence(
        self,
        top_chunks: List[Dict[str, Any]],
        selected_evidence: List[Dict[str, Any]],
        intent_confidence: float,
        is_calculation: bool = False,
    ) -> Tuple[float, ConfidenceLabel, Dict[str, float]]:
        if is_calculation:
            # Audited calculations with valid inputs have high confidence
            return 0.95, ConfidenceLabel.HIGH, {
                "retrieval_relevance": 1.0,
                "evidence_support": 1.0,
                "authority": 1.0,
                "intent_confidence": intent_confidence,
                "corroboration": 1.0,
                "contradiction_risk": 0.0,
            }

        if not top_chunks or not selected_evidence:
            return 0.0, ConfidenceLabel.UNSUPPORTED, {
                "retrieval_relevance": 0.0,
                "evidence_support": 0.0,
                "authority": 0.0,
                "intent_confidence": intent_confidence,
                "corroboration": 0.0,
                "contradiction_risk": 0.0,
            }

        # 1. Retrieval relevance R
        top_scores = [c.get("final_score", c.get("hybrid_score", 0.0)) for c in top_chunks[:3]]
        r_top = top_scores[0]
        r_mean = sum(top_scores) / len(top_scores)
        R = 0.70 * r_top + 0.30 * r_mean

        # 2. Evidence support E
        sent_scores = [ev["sentence_score"] for ev in selected_evidence]
        e_mean = sum(sent_scores) / len(sent_scores)
        e_count_factor = min(1.0, len(selected_evidence) / 2.0)
        E = 0.60 * e_mean + 0.40 * e_count_factor

        # 3. Authority A
        auth_scores = [float(ev.get("authority_level", "A") == "A") * 1.0 or 0.8 for ev in selected_evidence]
        A = max(auth_scores) if auth_scores else 0.8

        # 4. Intent confidence I
        I = intent_confidence

        # 5. Corroboration C
        distinct_sources = len(set(ev.get("source_name") for ev in selected_evidence))
        if distinct_sources >= 2:
            C = 1.0
        elif distinct_sources == 1:
            C = 0.5
        else:
            C = 0.0

        # 6. Contradiction risk X
        X = 0.0

        confidence = 0.32 * R + 0.18 * E + 0.16 * A + 0.14 * I + 0.12 * C + 0.08 * (1.0 - X)
        confidence = round(max(0.0, min(1.0, confidence)), 3)

        if confidence >= 0.78:
            label = ConfidenceLabel.HIGH
        elif confidence >= 0.60:
            label = ConfidenceLabel.MEDIUM
        elif confidence >= 0.40:
            label = ConfidenceLabel.LOW
        else:
            label = ConfidenceLabel.UNSUPPORTED

        factors = {
            "retrieval_relevance": round(R, 3),
            "evidence_support": round(E, 3),
            "authority": round(A, 3),
            "intent_confidence": round(I, 3),
            "corroboration": round(C, 3),
            "contradiction_risk": round(X, 3),
        }

        return confidence, label, factors

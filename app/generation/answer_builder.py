"""Rich, deterministic grounded answer composer."""

import re
from typing import List, Dict, Any, Tuple
from app.core.constants import IntentType, ResponseMode
from app.generation.templates import (
    DEFINITION_TEMPLATE,
    EXPLANATION_TEMPLATE,
    PROCEDURE_TEMPLATE,
    COMPARISON_TEMPLATE,
    INSUFFICIENT_EVIDENCE_TEMPLATE,
)
from app.nlp.terminology import FinancialTerminology


class AnswerBuilder:
    def __init__(self):
        self.terminology = FinancialTerminology.get_instance()

    def build_answer(
        self,
        intent: IntentType,
        query: str,
        selected_evidence: List[Dict[str, Any]],
        entities: Dict[str, Any],
    ) -> Tuple[str, ResponseMode]:
        if not selected_evidence:
            return INSUFFICIENT_EVIDENCE_TEMPLATE, ResponseMode.INSUFFICIENT_EVIDENCE

        # Extract primary entity or product
        products = entities.get("products", [])
        primary_product = products[0].upper() if products else ""

        # Check section title from top evidence
        top_section = selected_evidence[0].get("section") or "Financial Regulatory Overview"

        if intent == IntentType.DEFINITION:
            expansion = self.terminology.get_expansion(primary_product) if primary_product else None
            term_display = f"{primary_product} ({expansion.title()})" if expansion else (primary_product.title() if primary_product else top_section)
            def_sentence = selected_evidence[0]["sentence_text"]
            
            # If additional supporting sentences exist, add them
            extra_context = ""
            if len(selected_evidence) > 1:
                additional_points = []
                for ev in selected_evidence[1:]:
                    if ev["sentence_text"] != def_sentence:
                        additional_points.append(f"- {ev['sentence_text']}")
                if additional_points:
                    extra_context = "\n\n**Key Details:**\n" + "\n".join(additional_points)

            answer = f"**{term_display}** means:\n\n{def_sentence}{extra_context}\n\n*Educational information based on verified regulatory guidelines.*"
            return answer, ResponseMode.EVIDENCE_ANSWER

        elif intent == IntentType.PROCEDURE:
            steps = []
            for i, ev in enumerate(selected_evidence, start=1):
                steps.append(f"{i}. {ev['sentence_text']}")
            steps_list = "\n".join(steps)
            proc_title = primary_product.title() if primary_product else top_section
            answer = PROCEDURE_TEMPLATE.format(
                procedure_title=proc_title,
                steps_list=steps_list,
            )
            return answer, ResponseMode.PROCEDURE

        elif intent == IntentType.COMPARISON:
            if len(products) >= 2:
                topic_a = products[0].upper()
                topic_b = products[1].upper()
            else:
                # Try finding 'vs' or 'between' in query
                match = re.search(r"([a-zA-Z0-9_\s]+)\s+(?:vs|versus|and)\s+([a-zA-Z0-9_\s]+)", query, re.IGNORECASE)
                if match:
                    topic_a = match.group(1).strip().title()
                    topic_b = match.group(2).strip().title()
                else:
                    topic_a = primary_product.title() if primary_product else "First Option"
                    topic_b = "Second Option"

            body_a = selected_evidence[0]["sentence_text"]
            body_b = selected_evidence[1]["sentence_text"] if len(selected_evidence) > 1 else (selected_evidence[0]["sentence_text"])
            
            answer = (
                f"### Comparison: {topic_a} vs {topic_b}\n\n"
                f"| Feature / Aspect | {topic_a} | {topic_b} |\n"
                f"|---|---|---|\n"
                f"| **Key Characteristic** | {body_a} | {body_b} |\n\n"
                f"*This comparison is educational. Consult the respective official terms for full conditions.*"
            )
            return answer, ResponseMode.COMPARISON

        else:
            # Explanation / General Finance
            title = top_section if top_section != "General Section" else (primary_product.title() if primary_product else "Regulatory Guidance")
            bullet_points = []
            for ev in selected_evidence:
                bullet_points.append(f"- {ev['sentence_text']}")
            
            body_text = "\n\n".join(bullet_points)
            answer = (
                f"**{title}**\n\n"
                f"{body_text}\n\n"
                f"*Educational information based on verified regulatory guidelines.*"
            )
            return answer, ResponseMode.EVIDENCE_ANSWER

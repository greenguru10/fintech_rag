"""Chat service orchestrating end-to-end request lifecycle."""

import uuid
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

from app.core.constants import IntentType, ResponseMode, ConfidenceLabel
from app.conversation.state import ConversationState
from app.conversation.resolver import resolve_follow_up
from app.nlp.normalizer import normalize_text
from app.nlp.query_expansion import expand_query
from app.nlp.intent import IntentClassifier
from app.retrieval.retriever import HybridRetriever
from app.generation.answer_builder import AnswerBuilder
from app.generation.citations import CitationBuilder
from app.generation.confidence import ConfidenceScorer
from app.generation.templates import CALCULATION_TEXT_TEMPLATE, CLARIFICATION_TEMPLATE
from app.calculations.loan import calculate_emi
from app.calculations.investment import (
    calculate_sip,
    calculate_compound_interest,
    calculate_cagr,
    calculate_simple_interest,
    calculate_percentage,
)
from app.calculations.validators import parse_money, parse_rate, parse_tenure_months
from app.models.session import SessionModel, MessageModel
from app.models.query import QueryModel, RetrievalResultModel
from app.models.answer import AnswerModel, CitationModel
from app.models.feedback import CalculationHistoryModel
from app.schemas.chat import ChatResponse, ConfidenceSchema, SourceCitationSchema
from app.database.session import SessionLocal

logger = logging.getLogger(__name__)

# In-memory session cache for sub-millisecond session lookup
_SESSION_CACHE: Dict[str, ConversationState] = {}


def persist_chat_in_background(
    session_id: str,
    state_json: dict,
    raw_msg: str,
    rewritten_q: str,
    intent: str,
    intent_conf: float,
    resp_dict: dict,
    top_chunks: List[Dict[str, Any]],
):
    """Asynchronous background task to record conversation history without blocking HTTP response."""
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        _execute_persistence(
            db=db,
            session_id=session_id,
            state_json=state_json,
            raw_msg=raw_msg,
            rewritten_q=rewritten_q,
            intent=intent,
            intent_conf=intent_conf,
            resp_dict=resp_dict,
            top_chunks=top_chunks,
        )
    except Exception as e:
        logger.error(f"Failed to persist chat records in background: {e}", exc_info=True)
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


def _execute_persistence(
    db: Session,
    session_id: str,
    state_json: dict,
    raw_msg: str,
    rewritten_q: str,
    intent: str,
    intent_conf: float,
    resp_dict: dict,
    top_chunks: List[Dict[str, Any]],
):
    """Executes all database record insertions in a single atomic commit with zero intermediate flushes."""
    # 1. Upsert session record
    session_rec = db.query(SessionModel).filter_by(id=session_id).first()
    if not session_rec:
        session_rec = SessionModel(
            id=session_id,
            state_json=state_json,
        )
        db.add(session_rec)
    else:
        session_rec.state_json = state_json
        session_rec.updated_at = datetime.now(timezone.utc)

    # 2. Add user message
    user_msg = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="user",
        content=raw_msg,
    )
    db.add(user_msg)

    # 3. Add bot message
    bot_msg = MessageModel(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role="assistant",
        content=resp_dict["answer"],
        message_metadata={
            "intent": intent,
            "response_mode": resp_dict["response_mode"],
            "confidence_score": resp_dict["confidence"]["score"],
        },
    )
    db.add(bot_msg)

    # 4. Add query record with pre-allocated ID
    query_id = str(uuid.uuid4())
    query_rec = QueryModel(
        id=query_id,
        session_id=session_id,
        raw_query=raw_msg,
        normalized_query=rewritten_q,
        intent=intent,
        intent_confidence=intent_conf,
        category=resp_dict.get("category"),
    )
    db.add(query_rec)

    # 5. Add retrieval results
    source_chunk_ids = {s.get("chunk_id") for s in resp_dict.get("sources", []) if s.get("chunk_id")}
    for rank, chunk in enumerate(top_chunks[:10], start=1):
        rr = RetrievalResultModel(
            id=str(uuid.uuid4()),
            query_id=query_id,
            chunk_id=chunk["chunk_id"],
            rank=rank,
            bm25_score=chunk.get("bm25_score"),
            tfidf_score=chunk.get("tfidf_score"),
            metadata_score=chunk.get("metadata_score", 0.0),
            hybrid_score=chunk.get("final_score", chunk.get("hybrid_score", 0.0)),
            selected_as_evidence=(chunk["chunk_id"] in source_chunk_ids),
        )
        db.add(rr)

    # 6. Add answer record with pre-allocated ID
    ans_id = str(uuid.uuid4())
    ans_rec = AnswerModel(
        id=ans_id,
        query_id=query_id,
        response_mode=resp_dict["response_mode"],
        answer_text=resp_dict["answer"],
        confidence_score=resp_dict["confidence"]["score"],
        confidence_label=resp_dict["confidence"]["label"],
        calculation_json=resp_dict.get("calculation"),
    )
    db.add(ans_rec)

    # 7. Add citations linked to ans_id
    for idx, src in enumerate(resp_dict.get("sources", []), start=1):
        fallback_chunk = top_chunks[0]["chunk_id"] if top_chunks else str(uuid.uuid4())
        cit = CitationModel(
            id=str(uuid.uuid4()),
            answer_id=ans_id,
            chunk_id=src.get("chunk_id") or fallback_chunk,
            citation_order=idx,
            excerpt=src["excerpt"],
            sentence_index=0,
        )
        db.add(cit)

    # 8. Add calculation history if applicable
    calc_data = resp_dict.get("calculation")
    if calc_data:
        calc_hist = CalculationHistoryModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            calculation_type=calc_data.get("calculation_type", "unknown"),
            inputs_json=calc_data.get("inputs", {}),
            outputs_json=calc_data.get("result", {}),
            formula_version=calc_data.get("formula_version", "1.0.0"),
        )
        db.add(calc_hist)

    # Single atomic commit across the wire
    db.commit()


def ensure_valid_uuid(val: str | None) -> str:
    """Ensures a string is a strictly valid UUID, converting arbitrary strings deterministically."""
    if not val:
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(str(val)))
    except (ValueError, AttributeError):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(val)))


class ChatService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.intent_classifier = IntentClassifier()
        self.retriever = HybridRetriever()
        self.answer_builder = AnswerBuilder()
        self.citation_builder = CitationBuilder()
        self.confidence_scorer = ConfidenceScorer()

    def process_chat(
        self,
        message: str,
        session_id: str | None = None,
        include_debug: bool = False,
        background_tasks: Any = None,
    ) -> ChatResponse:
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        canonical_session_id = ensure_valid_uuid(session_id)

        # 1. Fast Session Management via In-Memory Cache
        state: ConversationState
        if canonical_session_id in _SESSION_CACHE:
            state = _SESSION_CACHE[canonical_session_id]
        else:
            state = ConversationState(session_id=canonical_session_id)
            _SESSION_CACHE[canonical_session_id] = state

        # 2. Resolve follow-up pronouns
        rewritten_query, is_resolved, resolved_entity = resolve_follow_up(message, state)

        # 3. Classify intent & extract entities
        intent, intent_conf, intent_meta = self.intent_classifier.classify_intent(rewritten_query)
        entities = intent_meta.get("entities", {})

        # 4. Route based on intent
        if intent_meta.get("is_greeting"):
            resp = self._build_response(
                request_id=request_id,
                session_id=canonical_session_id,
                answer_text=intent_meta.get("greeting_text"),
                intent=intent.value,
                response_mode=ResponseMode.EVIDENCE_ANSWER.value,
                confidence_score=0.99,
                confidence_label=ConfidenceLabel.HIGH.value,
                factors={"greeting": 1.0},
                citations=[],
                calculation=None,
            )
            self._dispatch_persistence(canonical_session_id, state, message, rewritten_query, intent.value, intent_conf, resp, [], background_tasks)
            return resp

        if intent == IntentType.UNSUPPORTED:
            refusal_text = intent_meta.get("refusal_text") or "I cannot provide personalized financial or investment advice."
            resp = self._build_response(
                request_id=request_id,
                session_id=canonical_session_id,
                answer_text=refusal_text,
                intent=intent.value,
                response_mode=ResponseMode.SAFETY_REFUSAL.value,
                confidence_score=0.98,
                confidence_label=ConfidenceLabel.HIGH.value,
                factors={"safety_compliance": 1.0},
                citations=[],
                calculation=None,
            )
            self._dispatch_persistence(canonical_session_id, state, message, rewritten_query, intent.value, intent_conf, resp, [], background_tasks)
            return resp

        if intent == IntentType.CLARIFICATION_NEEDED or intent_meta.get("missing_inputs"):
            products = entities.get("products", [])
            missing_topic = products[0] if products else "the specific details"
            clarification_text = CLARIFICATION_TEMPLATE.format(
                missing_field=f"{missing_topic} parameters (e.g. loan amount, interest rate, tenure)",
                example_prompt='For example: "Calculate EMI for ₹5 lakh loan at 10% for 5 years" or "What is an EMI?"',
            )
            resp = self._build_response(
                request_id=request_id,
                session_id=canonical_session_id,
                answer_text=clarification_text,
                intent=intent.value,
                response_mode=ResponseMode.CLARIFICATION.value,
                confidence_score=0.85,
                confidence_label=ConfidenceLabel.MEDIUM.value,
                factors={"clarification_required": 1.0},
                citations=[],
                calculation=None,
            )
            self._dispatch_persistence(canonical_session_id, state, message, rewritten_query, intent.value, intent_conf, resp, [], background_tasks)
            return resp

        # 5. Calculation route
        if intent == IntentType.CALCULATION and (entities.get("money") or entities.get("rates")):
            calc_resp = self._handle_calculation(rewritten_query, entities)
            if calc_resp:
                answer_text, calc_data = calc_resp
                resp = self._build_response(
                    request_id=request_id,
                    session_id=canonical_session_id,
                    answer_text=answer_text,
                    intent=intent.value,
                    response_mode=ResponseMode.CALCULATION.value,
                    confidence_score=0.95,
                    confidence_label=ConfidenceLabel.HIGH.value,
                    factors={"calculation_accuracy": 1.0},
                    citations=[],
                    calculation=calc_data,
                )
                self._dispatch_persistence(canonical_session_id, state, message, rewritten_query, intent.value, intent_conf, resp, [], background_tasks)
                return resp

        # 6. Retrieval Route (In-memory BM25 + TF-IDF + Fusion)
        normalized_q = normalize_text(rewritten_query)
        expanded_q = expand_query(rewritten_query)
        query_entities = entities.get("products", [])

        top_chunks, selected_evidence = self.retriever.retrieve(
            query=normalized_q,
            expanded_query=expanded_q,
            query_entities=query_entities,
        )

        # 7. Generate deterministic answer
        answer_text, response_mode = self.answer_builder.build_answer(
            intent=intent,
            query=rewritten_query,
            selected_evidence=selected_evidence,
            entities=entities,
        )

        # 8. Build citations
        citations = self.citation_builder.build_citations(selected_evidence)

        # 9. Calculate confidence
        conf_score, conf_label, conf_factors = self.confidence_scorer.calculate_confidence(
            top_chunks=top_chunks,
            selected_evidence=selected_evidence,
            intent_confidence=intent_conf,
            is_calculation=False,
        )

        resp = self._build_response(
            request_id=request_id,
            session_id=canonical_session_id,
            answer_text=answer_text,
            intent=intent.value,
            category=selected_evidence[0].get("category") if selected_evidence else None,
            response_mode=response_mode.value,
            confidence_score=conf_score,
            confidence_label=conf_label.value,
            factors=conf_factors,
            citations=citations,
            calculation=None,
        )

        # 10. Update session state in-memory cache
        state.previous_intent = intent.value
        state.previous_entities = query_entities or state.previous_entities
        state.previous_answer_mode = response_mode.value
        _SESSION_CACHE[canonical_session_id] = state

        self._dispatch_persistence(canonical_session_id, state, message, rewritten_query, intent.value, intent_conf, resp, top_chunks, background_tasks)
        return resp

    def _dispatch_persistence(
        self,
        session_id: str,
        state: ConversationState,
        raw_msg: str,
        rewritten_q: str,
        intent: str,
        intent_conf: float,
        resp: ChatResponse,
        top_chunks: List[Dict[str, Any]],
        background_tasks: Any = None,
    ):
        state_dict = state.model_dump(mode="json")
        resp_dict = resp.model_dump(mode="json")

        if background_tasks is not None:
            background_tasks.add_task(
                persist_chat_in_background,
                session_id=session_id,
                state_json=state_dict,
                raw_msg=raw_msg,
                rewritten_q=rewritten_q,
                intent=intent,
                intent_conf=intent_conf,
                resp_dict=resp_dict,
                top_chunks=top_chunks,
            )
        elif self.db is not None:
            try:
                _execute_persistence(
                    db=self.db,
                    session_id=session_id,
                    state_json=state_dict,
                    raw_msg=raw_msg,
                    rewritten_q=rewritten_q,
                    intent=intent,
                    intent_conf=intent_conf,
                    resp_dict=resp_dict,
                    top_chunks=top_chunks,
                )
            except Exception as e:
                logger.error(f"Failed to persist chat records: {e}", exc_info=True)
                self.db.rollback()

    def _handle_calculation(self, query: str, entities: Dict[str, Any]) -> Tuple[str, Dict[str, Any]] | None:
        q_lower = query.lower()
        money_list = entities.get("money", [])
        rates_list = entities.get("rates", [])
        tenures_list = entities.get("tenures", [])

        try:
            # 1. SIP Future Value
            if "sip" in q_lower:
                if money_list and rates_list and tenures_list:
                    p = parse_money(money_list[0], "monthly investment")
                    r = parse_rate(rates_list[0], "annual return")
                    y = Decimal(str(parse_tenure_months(tenures_list[0]) / 12))
                    res = calculate_sip(p, r, y)
                    text = CALCULATION_TEXT_TEMPLATE.format(
                        calc_name="SIP Future Value",
                        inputs_list=f"- Monthly Contribution: ₹{res['inputs']['monthly_investment']}\n- Assumed Annual Return: {res['inputs']['annual_return_pct']}%\n- Duration: {res['inputs']['years']} years",
                        result_list=f"- Total Invested: ₹{res['result']['total_invested']}\n- Estimated Future Value: ₹{res['result']['estimated_future_value']}\n- Estimated Gain: ₹{res['result']['estimated_gain']}",
                        formula=res["formula"],
                        assumptions_list="\n".join(f"- {a}" for a in res["assumptions"]),
                    )
                    return text, res

            # 2. CAGR Growth
            elif "cagr" in q_lower and len(money_list) >= 2 and tenures_list:
                bv = parse_money(money_list[0], "beginning value")
                ev = parse_money(money_list[1], "ending value")
                y = Decimal(str(parse_tenure_months(tenures_list[0]) / 12))
                res = calculate_cagr(bv, ev, y)
                text = CALCULATION_TEXT_TEMPLATE.format(
                    calc_name="Compound Annual Growth Rate (CAGR)",
                    inputs_list=f"- Beginning Value: ₹{res['inputs']['beginning_value']}\n- Ending Value: ₹{res['inputs']['ending_value']}\n- Duration: {res['inputs']['years']} years",
                    result_list=f"- CAGR: {res['result']['cagr_pct']}\n- Absolute Gain: ₹{res['result']['absolute_gain']} ({res['result']['absolute_gain_pct']})",
                    formula=res["formula"],
                    assumptions_list="\n".join(f"- {a}" for a in res["assumptions"]),
                )
                return text, res

            # 3. Compound Interest (Quarterly Compounding)
            elif ("compound interest" in q_lower or " ci " in f" {q_lower} " or "compounding" in q_lower) and money_list and rates_list and tenures_list:
                p = parse_money(money_list[0], "principal")
                r = parse_rate(rates_list[0], "annual interest rate")
                y = Decimal(str(parse_tenure_months(tenures_list[0]) / 12))
                res = calculate_compound_interest(p, r, y)
                text = CALCULATION_TEXT_TEMPLATE.format(
                    calc_name="Compound Interest",
                    inputs_list=f"- Principal: ₹{res['inputs']['principal']}\n- Annual Rate: {res['inputs']['annual_rate_pct']}%\n- Duration: {res['inputs']['years']} years",
                    result_list=f"- Total Interest Earned: ₹{res['result']['total_interest']}\n- Maturity Amount: ₹{res['result']['maturity_amount']}",
                    formula=res["formula"],
                    assumptions_list="\n".join(f"- {a}" for a in res["assumptions"]),
                )
                return text, res

            # 4. Loan EMI
            elif ("emi" in q_lower or "loan" in q_lower or "mortgage" in q_lower) and money_list and rates_list and tenures_list:
                p = parse_money(money_list[0], "principal")
                r = parse_rate(rates_list[0], "annual interest rate")
                n_months = parse_tenure_months(tenures_list[0])
                res = calculate_emi(p, r, n_months)
                text = CALCULATION_TEXT_TEMPLATE.format(
                    calc_name="Loan EMI",
                    inputs_list=f"- Principal Loan: ₹{res['inputs']['principal']}\n- Annual Interest Rate: {res['inputs']['annual_interest_rate_pct']}%\n- Tenure: {res['inputs']['tenure_months']} months ({round(n_months/12, 1)} years)",
                    result_list=f"- Monthly EMI: ₹{res['result']['monthly_emi']}\n- Total Interest: ₹{res['result']['total_interest']}\n- Total Payment: ₹{res['result']['total_payment']}",
                    formula=res["formula"],
                    assumptions_list="\n".join(f"- {a}" for a in res["assumptions"]),
                )
                return text, res

            # 5. Simple Interest or General Interest with/without Tenure
            elif any(w in q_lower for w in ["simple interest", "intreset", "interest", "intrest", " si "]) and money_list and rates_list:
                p = parse_money(money_list[0], "principal")
                r = parse_rate(rates_list[0], "interest rate")
                y = Decimal(str(parse_tenure_months(tenures_list[0]) / 12)) if tenures_list else Decimal("1")
                res = calculate_simple_interest(p, r, y)
                tenure_note = f"{y} year" if not tenures_list else f"{res['inputs']['years']} years"
                text = CALCULATION_TEXT_TEMPLATE.format(
                    calc_name="Interest Calculation",
                    inputs_list=f"- Principal Amount: ₹{res['inputs']['principal']}\n- Interest Rate: {res['inputs']['annual_rate_pct']}%\n- Time Period: {tenure_note}" + (" (Defaulted to 1 period)" if not tenures_list else ""),
                    result_list=f"- Interest Amount: ₹{res['result']['total_interest']}\n- Total Amount: ₹{res['result']['total_amount']}",
                    formula=res["formula"],
                    assumptions_list="\n".join(f"- {a}" for a in res["assumptions"]),
                )
                return text, res

            # 6. Percentage Share Calculation (e.g. "1% of 100", "calculate 10% of 50000 salary")
            elif money_list and rates_list:
                p = parse_money(money_list[0], "amount")
                r = parse_rate(rates_list[0], "percentage")
                res = calculate_percentage(p, r)
                text = CALCULATION_TEXT_TEMPLATE.format(
                    calc_name="Percentage Calculation",
                    inputs_list=f"- Base Amount: ₹{res['inputs']['amount']}\n- Percentage Rate: {res['inputs']['percentage']}%",
                    result_list=f"- Calculated Value: ₹{res['result']['calculated_value']}",
                    formula=res["formula"],
                    assumptions_list="\n".join(f"- {a}" for a in res["assumptions"]),
                )
                return text, res

            # 7. Default to EMI if 3 numeric fields exist
            elif money_list and rates_list and tenures_list:
                p = parse_money(money_list[0], "principal")
                r = parse_rate(rates_list[0], "annual interest rate")
                n_months = parse_tenure_months(tenures_list[0])
                res = calculate_emi(p, r, n_months)
                text = CALCULATION_TEXT_TEMPLATE.format(
                    calc_name="Loan EMI",
                    inputs_list=f"- Principal Loan: ₹{res['inputs']['principal']}\n- Annual Interest Rate: {res['inputs']['annual_interest_rate_pct']}%\n- Tenure: {res['inputs']['tenure_months']} months ({round(n_months/12, 1)} years)",
                    result_list=f"- Monthly EMI: ₹{res['result']['monthly_emi']}\n- Total Interest: ₹{res['result']['total_interest']}\n- Total Payment: ₹{res['result']['total_payment']}",
                    formula=res["formula"],
                    assumptions_list="\n".join(f"- {a}" for a in res["assumptions"]),
                )
                return text, res

        except Exception:
            return None

        return None

    def _build_response(
        self,
        request_id: str,
        session_id: str,
        answer_text: str,
        intent: str,
        response_mode: str,
        confidence_score: float,
        confidence_label: str,
        factors: Dict[str, float],
        citations: List[Dict[str, Any]],
        calculation: Dict[str, Any] | None,
        category: str | None = None,
    ) -> ChatResponse:
        return ChatResponse(
            request_id=request_id,
            session_id=session_id,
            answer=answer_text,
            intent=intent,
            category=category,
            response_mode=response_mode,
            confidence=ConfidenceSchema(
                score=confidence_score,
                label=confidence_label,
                factors=factors,
            ),
            sources=[
                SourceCitationSchema(
                    citation_id=c["citation_id"],
                    chunk_id=c.get("chunk_id"),
                    title=c["title"],
                    source_name=c["source_name"],
                    authority_level=c["authority_level"],
                    section=c.get("section"),
                    page_number=c.get("page_number"),
                    url=c.get("url"),
                    last_updated=c.get("last_updated"),
                    excerpt=c["excerpt"],
                )
                for c in citations
            ],
            calculation=calculation,
            follow_up=None,
            safety_notice="Educational information only. Grounded in verified regulatory guidelines.",
        )

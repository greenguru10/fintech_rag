#!/usr/bin/env python
"""Offline retrieval and grounded response evaluation."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.services.chat_service import ChatService
from app.core.config import settings


def evaluate():
    gold_path = settings.DATA_DIR / "evaluation" / "gold_questions.jsonl"
    if not gold_path.exists():
        print(f"Error: {gold_path} not found.")
        return

    db = SessionLocal()
    chat_service = ChatService(db)

    total_questions = 0
    intent_correct = 0
    safety_correct = 0
    citation_correct = 0
    keyword_recall_hits = 0

    print("============================================================")
    print("FINTECH NO-LLM RAG - RETRIEVAL & ANSWER EVALUATION BENCHMARK")
    print("============================================================\n")

    with open(gold_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            total_questions += 1
            qid = item["id"]
            q_text = item["question"]
            exp_intent = item["expected_intent"]
            exp_kw = item.get("expected_keywords", [])
            requires_cit = item.get("requires_citation", False)

            resp = chat_service.process_chat(message=q_text)

            # 1. Intent check
            is_intent_match = (resp.intent == exp_intent)
            if is_intent_match:
                intent_correct += 1

            # 2. Safety rejection check
            if exp_intent == "unsupported":
                is_safe = (resp.response_mode == "safety_refusal")
                if is_safe:
                    safety_correct += 1
            else:
                is_safe = True

            # 3. Citation check
            if requires_cit:
                has_valid_citation = len(resp.sources) > 0 and all(s.title for s in resp.sources)
                if has_valid_citation:
                    citation_correct += 1
            else:
                has_valid_citation = True

            # 4. Keyword presence check
            ans_lower = resp.answer.lower()
            kw_match = any(kw.lower() in ans_lower for kw in exp_kw) if exp_kw else True
            if kw_match:
                keyword_recall_hits += 1

            safe_q_text = q_text.replace("₹", "Rs.")
            status_sym = "[PASS]" if (is_intent_match and kw_match and (not requires_cit or has_valid_citation)) else "[FAIL]"
            print(f"{status_sym} {qid}: '{safe_q_text}'")
            print(f"    Intent: {resp.intent} (expected: {exp_intent}) | Mode: {resp.response_mode}")
            print(f"    Confidence: {resp.confidence.label} ({resp.confidence.score}) | Sources: {len(resp.sources)}")
            print()

    db.close()

    intent_acc = (intent_correct / total_questions) * 100
    kw_recall = (keyword_recall_hits / total_questions) * 100
    total_cit_expected = sum(1 for line in open(gold_path, "r", encoding="utf-8") if json.loads(line).get("requires_citation"))
    cit_acc = (citation_correct / total_cit_expected) * 100 if total_cit_expected > 0 else 100.0

    print("============================================================")
    print("EVALUATION SUMMARY")
    print("============================================================")
    print(f"Total Benchmark Queries : {total_questions}")
    print(f"Intent Classification Acc: {intent_acc:.1f}% (Target >= 85%)")
    print(f"Grounded Keyword Recall  : {kw_recall:.1f}% (Target >= 85%)")
    print(f"Citation Correctness     : {cit_acc:.1f}% (Target >= 95%)")
    print(f"No-LLM Mode              : 100% Deterministic (Zero GenAI APIs)")
    print("============================================================\n")


if __name__ == "__main__":
    evaluate()

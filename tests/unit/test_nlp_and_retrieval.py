"""Unit tests for NLP preprocessing, intent classification, and safety routing."""

from app.nlp.normalizer import normalize_text, tokenize_for_search, split_sentences
from app.nlp.abbreviations import expand_abbreviations
from app.nlp.intent import IntentClassifier
from app.nlp.safety_classifier import SafetyClassifier
from app.core.constants import IntentType


def test_normalizer():
    raw = "What is the interest on ₹5,00,000 home loan?"
    norm = normalize_text(raw)
    assert "Rs 5,00,000" in norm

    tokens = tokenize_for_search(raw)
    assert "interest" in tokens
    assert "loan" in tokens


def test_abbreviation_expansion():
    expanded = expand_abbreviations("What is EMI and SIP?")
    assert "equated monthly instalment" in expanded
    assert "systematic investment plan" in expanded


def test_sentence_splitter():
    text = "NEFT is a retail payment system. It operates 24x7x365 in half-hourly batches."
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert "NEFT" in sentences[0]


def test_intent_classification():
    clf = IntentClassifier()

    intent1, _, _ = clf.classify_intent("What is an EMI?")
    assert intent1 == IntentType.DEFINITION

    intent2, _, _ = clf.classify_intent("How does NEFT work?")
    assert intent2 == IntentType.EXPLANATION

    intent3, _, _ = clf.classify_intent("FD vs mutual fund")
    assert intent3 == IntentType.COMPARISON

    intent4, _, _ = clf.classify_intent("How to complete KYC?")
    assert intent4 == IntentType.PROCEDURE

    intent5, _, _ = clf.classify_intent("Calculate EMI for ₹5 lakh loan at 10% for 5 years")
    assert intent5 == IntentType.CALCULATION


def test_safety_refusal():
    safety = SafetyClassifier()

    is_unsafe, risk_type, _ = safety.check_safety("Which stock should I buy for 50% return next month?")
    assert is_unsafe is True
    assert risk_type == "personalized_advice"

    is_unsafe2, risk_type2, _ = safety.check_safety("How to avoid paying tax illegally?")
    assert is_unsafe2 is True
    assert risk_type2 == "illegal_activity"

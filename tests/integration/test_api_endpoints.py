"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["no_llm_mode"] == "enforced"


def test_sources_and_categories_endpoints():
    s_resp = client.get("/api/v1/sources")
    assert s_resp.status_code == 200
    assert len(s_resp.json()) >= 4

    c_resp = client.get("/api/v1/categories")
    assert c_resp.status_code == 200
    assert len(c_resp.json()) >= 6


def test_calculate_emi_api():
    resp = client.post("/api/v1/calculate/emi", json={
        "principal": "500000",
        "annual_interest_rate_pct": "10.0",
        "tenure_years": 5
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["monthly_emi"] == "10623.52"


def test_calculate_sip_api():
    resp = client.post("/api/v1/calculate/sip", json={
        "monthly_investment": "10000",
        "annual_return_pct": "12.0",
        "years": 10
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["total_invested"] == "1200000.00"


def test_chat_grounded_answer():
    resp = client.post("/api/v1/chat", json={
        "message": "What is an EMI?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "definition"
    assert "Equated Monthly Instalment" in data["answer"]
    assert len(data["sources"]) >= 1
    assert data["sources"][0]["source_name"] == "Reserve Bank of India"


def test_chat_follow_up():
    # Turn 1
    resp1 = client.post("/api/v1/chat", json={
        "message": "What is an EMI?"
    })
    assert resp1.status_code == 200
    session_id = resp1.json()["session_id"]

    # Turn 2: Follow up with reference "it"
    resp2 = client.post("/api/v1/chat", json={
        "session_id": session_id,
        "message": "How is it calculated?"
    })
    assert resp2.status_code == 200
    data = resp2.json()
    assert "EMI" in data["answer"] or "instalment" in data["answer"].lower()


def test_chat_safety_refusal():
    resp = client.post("/api/v1/chat", json={
        "message": "Which stock should I buy for a 50% return next month?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["response_mode"] == "safety_refusal"
    assert "cannot recommend specific stocks" in data["answer"]
    assert len(data["sources"]) == 0

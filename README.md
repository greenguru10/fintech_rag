# ⚡ FinTech Zero-LLM RAG & Financial Calculation Engine

[![Python 3.11](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-336791.svg?logo=postgresql)](https://supabase.com)
[![Zero-LLM Policy](https://img.shields.io/badge/Policy-100%25%20Zero--LLM%20AST%20Verified-brightgreen.svg)]()
[![Latency](https://img.shields.io/badge/Latency-Sub--50ms-success.svg)]()
[![Tests](https://img.shields.io/badge/Tests-23%2F23%20Passing-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Production%20Ready-2496ED.svg?logo=docker)](https://www.docker.com/)

A deterministic, **hallucination-free**, sub-50ms financial knowledge retrieval and calculation engine built **without generative LLM APIs**. Grounded strictly in official Indian financial regulations (**RBI, SEBI, IRDAI, NPCI, PFRDA, Income Tax Department**), featuring an authentic ChatGPT-style interface and full Supabase cloud persistence.

---

## 🌟 Key Features

- 🛡️ **Strict Zero-LLM Architecture**: 100% deterministic responses extracted directly from verified regulatory master circulars. No OpenAI, Anthropic, or external generative models.
- ⚡ **Sub-50ms Response Latency**: In-memory BM25 + TF-IDF hybrid fusion, Reciprocal Rank Fusion (RRF), and FastAPI asynchronous background database auditing.
- 🧮 **Universal Financial Calculation Engine**: High-precision `Decimal` calculations covering:
  - **Loan EMI** (Standard & 0% interest loans)
  - **SIP Future Value & Wealth Gain**
  - **Compound Interest (Quarterly Compounding)**
  - **CAGR (Compound Annual Growth Rate)**
  - **Simple Interest (with custom or defaulted tenures)**
  - **Percentage Shares & TDS calculations**
- 🎨 **ChatGPT-Inspired Dark Theme UI**:
  - Beginner-friendly interface tailored for everyday users.
  - Interactive topic pills (*Loans & EMI, SIP & Investing, Tax & Savings, Banking & UPI*).
  - Clickable citation cards linking directly to official regulatory portals.
  - One-click copy with toast notifications and feedback ratings.
- ☁️ **Supabase Cloud PostgreSQL Integration**: Full schema persistence with connection pooling, session history caching, and automatic fallback.
- 🧪 **Automated Verification Suite**: Continuous AST scanner preventing generative AI imports and full test suite with 23 passing integration/unit tests.

---

## 🏛️ System Architecture

```mermaid
graph TD
    User([User / Web Browser]) -->|POST /api/v1/chat| API[FastAPI Gateway]
    
    subgraph "Core Orchestration Engine"
        API --> Resolver[Follow-up & Pronoun Resolver]
        Resolver --> Intent[Rule-Based Intent Classifier]
        
        Intent -->|Calculation Intent| CalcEngine[Universal Calculation Engine]
        Intent -->|Regulatory Query| HybridSearch[Hybrid In-Memory Retriever]
        
        subgraph "Hybrid Retrieval Pipeline"
            HybridSearch --> BM25[BM25 Okapi]
            HybridSearch --> TFIDF[TF-IDF Vector Space]
            BM25 & TFIDF --> RRF[Score Fusion & Reranker]
            RRF --> Evidence[Evidence Sentence Extractor]
        end
        
        CalcEngine --> AnsBuilder[Deterministic Answer Builder]
        Evidence --> AnsBuilder
        AnsBuilder --> Citation[Citation & Confidence Scorer]
    end
    
    Citation -->|Instant HTTP Response (<40ms)| User
    Citation -.->|Background Task| DB[(Supabase PostgreSQL)]
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.11+
- Git
- (Optional) Docker & Docker Compose

### 1. Clone & Setup Environment

```bash
git clone https://github.com/greenguru10/fintech_rag.git
cd fintech_rag

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure your database:

```bash
cp .env.example .env
```

Example `.env`:
```env
APP_ENV=development
APP_NAME="FinTech No-LLM Knowledge Chatbot"
API_PREFIX=/api/v1

# SQLite (Local) or PostgreSQL (Supabase/Neon)
DATABASE_URL=sqlite:///data/chatbot.db
# Or remote Supabase:
# DATABASE_URL=postgresql+psycopg://postgres:[PASSWORD]@[HOST]:5432/postgres

ALLOWED_ORIGINS=*
BM25_K1=1.2
BM25_B=0.75
RETRIEVAL_TOP_K=30
FINAL_EVIDENCE_K=4
```

### 3. Ingest Regulatory Knowledge Base

```bash
# Ingest all regulatory master circulars from data/raw/
python scripts/ingest_documents.py

# Rebuild in-memory search indexes
python scripts/rebuild_indexes.py
```

### 4. Run the Application

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/chat` | Main conversational endpoint with citations & calculations |
| `POST` | `/api/v1/calculate/emi` | Loan EMI repayment calculation |
| `POST` | `/api/v1/calculate/sip` | SIP future value & wealth accumulation |
| `POST` | `/api/v1/calculate/compound-interest` | Compound interest calculation |
| `POST` | `/api/v1/calculate/cagr` | CAGR growth calculation |
| `GET` | `/api/v1/health` | Service health, database status & index chunk count |
| `GET` | `/api/v1/sources` | List all verified regulatory sources |
| `GET` | `/api/v1/categories` | List active regulatory categories |
| `GET` | `/api/v1/documents` | List active regulatory master documents |
| `POST` | `/api/v1/feedback` | Record user feedback on answers |

---

## 🐳 Docker Deployment

### Run with Docker Compose
```bash
docker-compose up --build -d
```

### Build & Run Container Manually
```bash
docker build -t fintech-rag:latest .
docker run -d -p 8000:8000 --env-file .env fintech-rag:latest
```

---

## 🧪 Testing & Code Quality

Run the test suite and strict No-LLM static verification:

```bash
# Run all unit and integration tests
pytest -v

# Run AST Zero-LLM Compliance Scanner
python scripts/verify_no_llm.py
```

---

## 📚 Grounded Regulatory Sources

1. **Reserve Bank of India (RBI)**: Master Directions on Deposits, Loans, Mortgages, Credit Cards, and Digital Lending.
2. **Securities and Exchange Board of India (SEBI)**: Mutual Funds (Categorization & Rationalization), KYC Norms.
3. **Insurance Regulatory and Development Authority of India (IRDAI)**: Health & Life Insurance Regulations.
4. **National Payments Corporation of India (NPCI)**: UPI Transaction Limits, Guidelines, and Dispute Redressal.
5. **Pension Fund Regulatory and Development Authority (PFRDA)**: National Pension Scheme (NPS) Guidelines.
6. **Income Tax Department of India**: Tax Regimes (Old vs New), Section 80C, 80D, 80TTA, and TDS Deductions.

---

## 📄 License
This project is licensed under the MIT License.

# Production Deployment Guide - FinTech AI Chatbot

This deterministic, zero-LLM FinTech AI platform is designed for **high throughput, minimal latency (<15ms), zero hallucination, and instant deployment** to any modern cloud container provider.

---

## 🚀 Option 1: Deploy on Render.com (Recommended Free/Easy)

1. Push this repository to your **GitHub**.
2. Go to **[Render.com](https://render.com/)** and click **New + > Web Service**.
3. Select your GitHub repository.
4. Configure the service settings:
   - **Environment**: `Docker` (Render will automatically detect the `Dockerfile`)
   - **Plan**: Free or Starter
   - **Health Check Path**: `/api/v1/health`
5. In the **Environment Variables** section, add:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:Vedantmallya%4047@db.vblsehbdclgoylwznmxa.supabase.co:5432/postgres
   APP_ENV=production
   ALLOWED_ORIGINS=*
   ```
6. Click **Deploy Web Service**. Your chatbot will be live with free HTTPS (e.g. `https://your-chatbot.onrender.com`).

---

## ⚡ Option 2: Deploy on Railway.app

1. Go to **[Railway.app](https://railway.app/)** and click **New Project > Deploy from GitHub Repo**.
2. Railway will automatically build the `Dockerfile`.
3. In the **Variables** tab, set:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:Vedantmallya%4047@db.vblsehbdclgoylwznmxa.supabase.co:5432/postgres
   PORT=8000
   ```
4. Click **Generate Domain** under Networking. Your chatbot is live!

---

## 🐳 Option 3: Deploy via Docker / Any VPS (AWS, DigitalOcean, Hetzner, GCP)

1. Clone the repository on your server:
   ```bash
   git clone <your-repo-url>
   cd chatbot
   ```

2. Start with Docker Compose:
   ```bash
   docker compose up -d --build
   ```

3. View live logs:
   ```bash
   docker compose logs -f
   ```

4. Check health:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

---

## 🛡️ Production Verification & Checklist

- [x] **Zero-LLM Verification**: AST scanning ensures 0 generative AI dependencies.
- [x] **Database Grounding**: Live connection to Supabase PostgreSQL with 17 regulatory documents and 69 chunks indexed.
- [x] **Financial Accuracy**: Python `Decimal` with `ROUND_HALF_UP` precision for all EMI, SIP, CI, and CAGR calculations.
- [x] **Audited Regulatory Sources**: Clickable transparent citations citing RBI, SEBI, IRDAI, NPCI, and Income Tax Department.
- [x] **Beginner-Friendly Frontend**: Modern ChatGPT dark UI with category starter prompts, live sliders, copy buttons, and responsive sidebar.

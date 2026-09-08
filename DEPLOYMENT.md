# Production Deployment Guide - FinTech AI Chatbot

This deterministic, zero-LLM FinTech AI platform is designed for **high throughput, minimal latency (<15ms), zero hallucination, and instant deployment** to any modern cloud container provider.

🌐 **Live Production Deployment**: **[https://fintech-rag2.onrender.com/](https://fintech-rag2.onrender.com/)**

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

### ⏱️ 24/7 Uptime Bot for Render (Zero Cold Starts)

Render free tier instances sleep after 15 minutes of inactivity. To keep your chatbot **awake 24/7 with zero cold starts and instant response times**:

#### Method 1: Built-in Self-Pinger (Zero Config)
When deployed on Render, the application automatically detects its `RENDER_EXTERNAL_URL` environment variable and runs an asynchronous keep-alive background worker that sends a heartbeat to `/api/v1/ping` every 9 minutes.

#### Method 2: GitHub Actions Automated Uptime Bot (Included)
This repository includes a scheduled GitHub Actions workflow in [`.github/workflows/keep_alive.yml`](file:///.github/workflows/keep_alive.yml).
1. Go to your GitHub repository **Settings > Secrets and variables > Actions**.
2. Add a new repository secret:
   - **Name**: `RENDER_APP_URL`
   - **Value**: `https://your-app-name.onrender.com`
3. GitHub Actions will automatically ping your service every 10 minutes for free!

#### Method 3: UptimeRobot (Free External Monitor)
1. Create a free account on **[UptimeRobot.com](https://uptimerobot.com/)**.
2. Click **Add New Monitor**:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `FinTech RAG Render Bot`
   - **URL**: `https://your-app-name.onrender.com/api/v1/ping`
   - **Monitoring Interval**: `5 minutes`
3. Save the monitor. Your app will remain 100% online 24/7.

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

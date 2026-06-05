# InsightForge AI — Render.com Deployment Guide

## Why Render over Vercel?

| Feature | Render (free) | Vercel (free) |
|---|---|---|
| Persistent disk | ✅ 1 GB | ❌ None |
| Function timeout | ✅ No limit (long-running) | ⚠ 10 seconds |
| FAISS on disk | ✅ Survives restarts | ❌ Resets on cold start |
| MLflow tracking | ✅ SQLite on /data | ❌ No filesystem |
| File uploads | ✅ Stored on disk | ⚠ In-memory only |

---

## Project structure

```
insightforge-render/
├── main.py              ← FastAPI entrypoint
├── app/
│   ├── agent.py         ← LangGraph ReAct agent + MLflow
│   ├── rag.py           ← Persistent FAISS on /data
│   ├── tools.py         ← search_documents + calculate
│   └── memory.py        ← MemorySaver (per-session)
├── static/
│   └── index.html       ← Full web UI
├── requirements.txt
├── render.yaml          ← Render Blueprint (auto-configures service)
└── .gitignore
```

---

## Step 1 — Push to GitHub

```bash
cd insightforge-render
git init
git add .
git commit -m "InsightForge AI - Render deployment"
```

Go to **github.com → New repository**, create `insightforge-ai`, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/insightforge-ai.git
git branch -M main
git push -u origin main
```

---

## Step 2 — Deploy on Render

### Option A — Blueprint (recommended, 1 click)
1. Go to **https://render.com/deploy**
2. Connect your GitHub account
3. Select your `insightforge-ai` repo
4. Render reads `render.yaml` and auto-configures everything
5. Click **Apply**

### Option B — Manual setup
1. Go to **https://dashboard.render.com/new/web**
2. Connect GitHub → select repo
3. Fill in:
   - **Name:** `insightforge-ai`
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Under **Advanced → Disks**, add:
   - **Mount path:** `/data`
   - **Size:** 1 GB
5. Click **Create Web Service**

---

## Step 3 — Add your OpenAI API Key

After the service is created:

1. Go to your service → **Environment** tab
2. Click **Add Environment Variable**
3. Set:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** `sk-...your key here...`
4. Click **Save Changes** → Render auto-redeploys

Your app is live at `https://insightforge-ai.onrender.com` 🎉

---

## Step 4 — Use the app

Open your Render URL and you'll see the InsightForge AI interface:

- **Upload PDFs** — stored permanently on `/data/uploads`
- **Ingest URLs** — webpage content added to knowledge base
- **Ask questions** — ReAct agent reasons over your documents
- **MLflow** — query logs stored at `/data/mlflow.db`

API endpoints:
```
GET  /health          → {"status":"ok","store_loaded":true/false}
POST /upload          → multipart PDF upload
POST /ingest          → {"sources":["https://..."]}
POST /query           → {"query":"...","thread_id":"session_1"}
```

---

## Free tier limits

| Limit | Detail |
|---|---|
| RAM | 512 MB — enough for FAISS + GPT-4o calls |
| CPU | Shared |
| Disk | 1 GB persistent |
| Sleep | Service sleeps after 15 min idle (first request takes ~30s to wake) |
| Bandwidth | 100 GB/month |

To prevent sleeping, you can use a free uptime service like **UptimeRobot** to ping `/health` every 10 minutes.

---

## Redeploy after changes

```bash
git add . && git commit -m "update" && git push
```
Render auto-deploys on every push to `main`.

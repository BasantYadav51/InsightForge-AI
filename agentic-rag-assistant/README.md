# Agentic RAG Research Assistant

An autonomous AI agent powered by LangGraph + LangChain that answers research queries by searching your documents and the web, with persistent memory, hallucination guards, and production-ready deployment.

## Features
- LangGraph ReAct agent with multi-step reasoning
- RAG pipeline: PDF/web ingestion → FAISS vector store → semantic retrieval
- Persistent conversation memory (MemorySaver)
- Hallucination detection & confidence scoring
- MLflow experiment tracking
- FastAPI REST API
- Docker + GitHub Actions CI/CD

## Stack
| Layer | Tech |
|---|---|
| Agent | LangGraph + LangChain |
| LLM | OpenAI GPT-4o |
| Vector DB | FAISS |
| Embeddings | OpenAI text-embedding-3-small |
| API | FastAPI + Pydantic |
| Tracking | MLflow |
| Deployment | Docker + GitHub Actions |

## Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/YOUR_USERNAME/agentic-rag-assistant
cd agentic-rag-assistant
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 2. Install
pip install -r requirements.txt

# 3. Run
uvicorn app.main:app --reload

# 4. Ingest a document
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"sources": ["your_doc.pdf"]}'

# 5. Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarise the key points", "thread_id": "session_1"}'
```

## Docker

```bash
docker build -t agentic-rag-assistant .
docker run -p 8000:8000 --env-file .env agentic-rag-assistant
```

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health check |
| POST | /ingest | Ingest PDFs or URLs into FAISS |
| POST | /query | Ask the agent a question |

## Author
Basant Yadav — AI/ML Engineer

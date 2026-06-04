from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import run_agent
from app.rag import build_vector_store
import mlflow

mlflow.set_experiment("agentic-rag")

app = FastAPI(title="Agentic RAG Assistant", version="1.0.0")


class QueryRequest(BaseModel):
    query: str
    thread_id: str = "default"


class IngestRequest(BaseModel):
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(req: IngestRequest):
    try:
        build_vector_store(req.sources)
        return {"message": f"Ingested {len(req.sources)} source(s) successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query(req: QueryRequest):
    try:
        result = run_agent(req.query, req.thread_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

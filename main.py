import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.agent import run_agent
from app.rag import build_vector_store, store_loaded, UPLOAD_DIR

app = FastAPI(title="InsightForge AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    thread_id: str = "default"


class IngestRequest(BaseModel):
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok", "store_loaded": store_loaded()}


@app.post("/ingest")
def ingest(req: IngestRequest):
    try:
        build_vector_store(req.sources)
        return {"message": f"Ingested {len(req.sources)} source(s) successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        dest = os.path.join(UPLOAD_DIR, file.filename)
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        build_vector_store([dest])
        return {"message": f"'{file.filename}' uploaded and ingested successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query(req: QueryRequest):
    try:
        result = run_agent(req.query, req.thread_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve UI — must be registered last
app.mount("/", StaticFiles(directory="static", html=True), name="static")

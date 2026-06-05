"""
RAG module — persistent FAISS vector store.
On Render, the persistent disk is mounted at /data.
FAISS index is saved/loaded from /data/faiss_index so it survives restarts.
"""
import os
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Use Render persistent disk if available, else local
DATA_DIR = os.environ.get("DATA_DIR", "data")
VECTOR_STORE_PATH = os.path.join(DATA_DIR, "faiss_index")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return _embeddings


def _index_exists() -> bool:
    return os.path.exists(os.path.join(VECTOR_STORE_PATH, "index.faiss"))


def build_vector_store(sources: list[str]) -> FAISS:
    """Ingest sources and persist the FAISS index to disk."""
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for src in sources:
        if src.startswith("http"):
            loader = WebBaseLoader(src)
        else:
            loader = PyPDFLoader(src)
        docs.extend(splitter.split_documents(loader.load()))

    embeddings = get_embeddings()

    if _index_exists():
        # Extend the existing index
        store = FAISS.load_local(
            VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
        )
        store.add_documents(docs)
    else:
        store = FAISS.from_documents(docs, embeddings)

    store.save_local(VECTOR_STORE_PATH)
    return store


def load_vector_store() -> FAISS:
    embeddings = get_embeddings()
    return FAISS.load_local(
        VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
    )


def retrieve(query: str, k: int = 4) -> list[str]:
    if not _index_exists():
        return []
    store = load_vector_store()
    results = store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]


def store_loaded() -> bool:
    return _index_exists()

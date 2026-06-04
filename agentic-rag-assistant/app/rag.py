from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_STORE_PATH = "faiss_index"


def build_vector_store(sources: list[str]) -> FAISS:
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for src in sources:
        if src.startswith("http"):
            loader = WebBaseLoader(src)
        else:
            loader = PyPDFLoader(src)
        docs.extend(splitter.split_documents(loader.load()))

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(VECTOR_STORE_PATH)
    return store


def load_vector_store() -> FAISS:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.load_local(
        VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
    )


def retrieve(query: str, k: int = 4) -> list[str]:
    store = load_vector_store()
    results = store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]

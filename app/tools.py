from langchain.tools import tool
from app.rag import retrieve, store_loaded


@tool
def search_documents(query: str) -> str:
    """Search the internal knowledge base for relevant information."""
    if not store_loaded():
        return "No documents have been ingested yet. Please upload a PDF or provide a URL first."
    chunks = retrieve(query)
    if not chunks:
        return "No relevant documents found for that query."
    return "\n\n---\n\n".join(chunks)


@tool
def calculate(expression: str) -> str:
    """Safely evaluate a basic math expression. E.g. '2 + 2 * 10'"""
    try:
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return "Invalid expression."
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

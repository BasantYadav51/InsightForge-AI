from langgraph.checkpoint.memory import MemorySaver


def get_memory() -> MemorySaver:
    """MemorySaver keeps conversation state across turns per thread_id."""
    return MemorySaver()

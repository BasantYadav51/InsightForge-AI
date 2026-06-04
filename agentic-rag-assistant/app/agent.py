import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.tools import search_documents, calculate
from app.memory import get_memory
import mlflow

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [search_documents, calculate]
memory = get_memory()

SYSTEM_PROMPT = (
    "You are a helpful research assistant. Always search documents before answering. "
    "If you are unsure, say so — never fabricate facts. "
    "Cite your sources when possible."
)

agent = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    state_modifier=SYSTEM_PROMPT,
)


def run_agent(query: str, thread_id: str = "default") -> dict:
    config = {"configurable": {"thread_id": thread_id}}

    with mlflow.start_run(run_name="agent_query", nested=True):
        mlflow.log_param("query", query)
        mlflow.log_param("thread_id", thread_id)

        result = agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            config=config,
        )

        answer = result["messages"][-1].content

        is_uncertain = any(
            phrase in answer.lower()
            for phrase in ["i don't know", "i'm not sure", "i cannot", "no information"]
        )
        mlflow.log_metric("is_uncertain", int(is_uncertain))
        mlflow.log_text(answer, "response.txt")

    return {
        "answer": answer,
        "thread_id": thread_id,
        "uncertain": is_uncertain,
    }

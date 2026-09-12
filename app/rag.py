from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import CHAT_MODEL, EMBEDDING_MODEL, OPENAI_API_KEY, VECTOR_DIR

SYSTEM_PROMPT = """You are a practical Singapore travel assistant.

Use the retrieved knowledge base for stable destination facts. Use MCP results for current weather or currency. Do not invent facts when the available context is insufficient. Say when you do not have enough evidence.

When citing a knowledge-base fact, include its source URL in a compact Sources section. Do not cite tool values as if they came from the KB. Clearly distinguish sourced facts from your own itinerary recommendations.

Use the conversation history to preserve traveller preferences, budget, party size and constraints across turns.
"""


class TravelRAG:
    def __init__(self):
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.store = Chroma(persist_directory=str(VECTOR_DIR), embedding_function=embeddings)
        self.llm = ChatOpenAI(model=CHAT_MODEL, api_key=OPENAI_API_KEY, temperature=0.2)

    def answer(self, question, history, tool_results):
        docs = self.store.similarity_search(question, k=4)
        context = "\n\n".join(
            f"[{doc.metadata.get('file', 'source')}]\n{doc.page_content}" for doc in docs
        )
        recent = "\n".join(f"{m['role']}: {m['content']}" for m in history[-8:])
        tools = tool_results or {}
        prompt = f"""Question:
{question}

Retrieved context:
{context}

Tool results:
{tools}

Recent conversation:
{recent}

Write a useful answer. If the KB does not support a factual claim, do not present it as sourced. If a live tool failed or was not available, be explicit about that limitation.
"""
        response = self.llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return response.content

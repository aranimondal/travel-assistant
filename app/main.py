import streamlit as st

from app.mcp_client import MCPTravelTools, detect_tool_needs
from app.rag import TravelRAG

st.set_page_config(page_title="Singapore Travel Assistant", page_icon="✈️")
st.title("Singapore Travel Assistant")
st.caption("RAG + MCP travel planning demo")

if "history" not in st.session_state:
    st.session_state.history = []

@st.cache_resource
def get_rag():
    return TravelRAG()

@st.cache_resource
def get_tools():
    return MCPTravelTools()

question = st.chat_input("Ask about Singapore travel")

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        rag = get_rag()
        tools = get_tools()
        needs = detect_tool_needs(question)
        tool_results = tools.invoke(question, needs)
        answer = rag.answer(question, st.session_state.history, tool_results)
        st.markdown(answer)
        st.session_state.history.append({"role": "assistant", "content": answer})

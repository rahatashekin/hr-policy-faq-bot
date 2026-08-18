"""
RAG Chat Interface — Agent + Memory + Streamlit UI.

Mirrors cookbook knowledge/docling/5-chat.py responsibility:
one file, one job — search + agent + chat UI.
"""

import json
import logging

import streamlit as st

from config import CHAT_MODEL, openai_client
from embed import search_pinecone

logger = logging.getLogger(__name__)


# --------------------------------------------------------------
# Tool definitions for the AI Agent
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "name": "search_knowledge_base",
        "description": (
            "Retrieve relevant information when the user asks any question "
            "about BRAC Road Safety Programme (RSP) employee policies, "
            "including HR leave rules, attendance, working hours, road safety "
            "and vehicle operations, field travel allowances (TA/DA), emergency "
            "accident response procedures, health insurance benefits, or "
            "employee code of conduct and whistleblowing."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant policy information",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]

SYSTEM_PROMPT = (
    "You are a helpful BRAC Road Safety Programme (RSP) assistant. "
    "Answer questions about employee policies using the search_knowledge_base "
    "tool. Always cite your sources. If you cannot find the answer, say so honestly."
)


def _execute_search(query: str) -> str:
    """Search Pinecone and format results with source citations."""
    results = search_pinecone(query)
    if not results:
        return "No relevant information found in the knowledge base."

    parts = []
    for r in results:
        parts.append(
            f"Source: {r['filename']} (Chunk {r['chunk_index']})\n"
            f"Content:\n{r['text']}"
        )
    return "\n\n---\n\n".join(parts)


def _call_function(name: str, args: dict) -> str:
    """Route tool calls to their corresponding functions."""
    if name == "search_knowledge_base":
        return _execute_search(**args)
    raise ValueError(f"Unknown function: {name}")


# --------------------------------------------------------------
# Agent chat — tool calling + conversational memory
# --------------------------------------------------------------


def chat(user_message: str, history: list[dict]) -> tuple[str, list[dict]]:
    """Chat with the RAG agent.

    Args:
        user_message: The user's question.
        history:      Conversation history as message dicts.

    Returns:
        Tuple of (response text, updated history).
    """
    if openai_client is None:
        raise RuntimeError("OpenAI client not initialized.")

    input_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": user_message},
    ]

    response = openai_client.responses.create(
        model=CHAT_MODEL, input=input_messages, tools=tools
    )

    tool_called = False
    for tool_call in response.output:
        if tool_call.type == "function_call":
            tool_called = True
            args = json.loads(tool_call.arguments)
            logger.info("Tool call: %s(%s)", tool_call.name, args)
            result = _call_function(tool_call.name, args)

            input_messages.append(tool_call)
            input_messages.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result),
                }
            )

    if tool_called:
        final = openai_client.responses.create(
            model=CHAT_MODEL, input=input_messages, tools=tools
        )
        answer = final.output_text
    else:
        answer = response.output_text

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": answer})
    return answer, history


# --------------------------------------------------------------
# Streamlit Chat UI
# --------------------------------------------------------------

st.set_page_config(page_title="BRAC RSP FAQ Bot", page_icon="🏢", layout="centered")

with st.sidebar:
    st.title("🏢 BRAC RSP FAQ Bot")
    st.write("AI assistant for BRAC Road Safety Programme employee policies.")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

    st.markdown("### Example Questions")
    st.markdown("- What is the leave policy for RSP employees?")
    st.markdown("- How many annual leave days are allowed?")
    st.markdown("- What is the emergency accident response procedure?")
    st.markdown("- What are the field travel allowance (TA/DA) rules?")

st.title("🏢 BRAC RSP FAQ Bot")
st.write("Ask me anything about BRAC RSP employee policies, HR rules, leave, and travel.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about BRAC RSP policies..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                response_text, st.session_state.history = chat(
                    prompt, st.session_state.history
                )
            except Exception as e:
                response_text = f"⚠️ Error: {type(e).__name__}: {e}"
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})

"""
app.py
------
Streamlit chat UI for the Conversational Knowledge Bot.

Run:
    streamlit run app.py
"""

import uuid

import streamlit as st

from llm import get_llm
from bot import build_bot, ask

st.set_page_config(page_title="Knowledge Bot", page_icon="💬", layout="centered")


def escape_dollar_signs(text: str) -> str:
    """
    Streamlit's markdown renderer treats $...$ as LaTeX math delimiters.
    Escaping '$' as '\\$' prevents dollar amounts in replies (e.g. stock
    prices from a web search) from being misrendered as math formulas.
    """
    return text.replace("$", "\\$")


st.title("💬 Conversational Knowledge Bot")
st.caption("LangGraph agent · Wikipedia + Web search tools · Persistent memory")

if "agent" not in st.session_state:
    llm = get_llm()
    st.session_state.agent = build_bot(llm)
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []  # for rendering only; the agent has its own memory

with st.sidebar:
    st.markdown(
        """
        **Try this to see memory + tools in action:**
        1. *"Who is the CEO of OpenAI?"*
        2. *"Where did he study?"*  ← follow-up, uses conversation memory
        3. *"What's the latest news about them?"*  ← triggers web search tool
        """
    )
    if st.button("🗑️ New conversation"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(escape_dollar_signs(msg["content"]))

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = ask(st.session_state.agent, st.session_state.thread_id, prompt)
        st.markdown(escape_dollar_signs(reply))
    st.session_state.messages.append({"role": "assistant", "content": reply})
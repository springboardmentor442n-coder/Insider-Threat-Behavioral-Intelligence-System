"""
app.py
------
Streamlit UI for the Company Intelligence multi-agent system.

Run:
    streamlit run app.py
"""

import streamlit as st

from llm import get_llm
from graph import build_graph

st.set_page_config(page_title="Company Intelligence Agents", page_icon="📈", layout="wide")


def escape_dollar_signs(text: str) -> str:
    """
    Streamlit's markdown renderer treats $...$ as LaTeX math delimiters.
    Since our reports contain real dollar amounts (e.g. "$225.16"), a run of
    text with two or more '$' can get misinterpreted as a math formula and
    render as garbled LaTeX instead of plain text. Escaping '$' as '\\$'
    tells the renderer to show a literal dollar sign instead.
    """
    return text.replace("$", "\\$")


st.title("📈 Company Intelligence Agentic System")
st.caption("Agent 1 (Data Collector) → Agent 2 (Analyst) — orchestrated with LangGraph")

# --- Session state setup ---
if "app_graph" not in st.session_state:
    llm = get_llm()
    st.session_state.app_graph = build_graph(llm)
    st.session_state.thread_id = "streamlit-session"
    st.session_state.turns = []  # list of {company, collector, analyst}

with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        1. **Data Collector agent** calls real tools:
           - `get_stock_performance` (yfinance)
           - `get_company_news` (DuckDuckGo)
        2. **Analyst agent** calls `calculate_volatility` and reasons over
           the Collector's facts to produce a summary, insights, and risks.
        3. A LangGraph checkpointer keeps memory across every company you
           ask about in this session, so the Analyst can compare across turns.
        """
    )
    if st.button("🗑️ Clear session memory"):
        st.session_state.turns = []
        st.session_state.thread_id = f"streamlit-session-{len(st.session_state.turns)}"
        st.rerun()

company = st.text_input("Company or ticker", placeholder="e.g. Nvidia, TSLA, Amazon")
go = st.button("🔎 Analyze", type="primary")

if go and company.strip():
    thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
    with st.spinner(f"Collector is gathering data on {company}..."):
        result = st.session_state.app_graph.invoke(
            {"company": company}, config=thread_config
        )
    st.session_state.turns.append(
        {
            "company": company,
            "collector": result["collector_report"],
            "analyst": result["analyst_report"],
        }
    )

# --- Render all turns, most recent first ---
for turn in reversed(st.session_state.turns):
    st.subheader(f"🏢 {turn['company']}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🗂️ Data Collector Report**")
        st.markdown(escape_dollar_signs(turn["collector"]))
    with col2:
        st.markdown("**🧠 Analyst Report**")
        st.markdown(escape_dollar_signs(turn["analyst"]))
    st.divider()

if not st.session_state.turns:
    st.info("👆 Enter a company above to see both agents work.")
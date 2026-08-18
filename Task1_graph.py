"""
graph.py
--------
The orchestrator: a LangGraph StateGraph that runs Collector -> Analyst in
sequence, passes structured state between them, and persists memory across
turns using a checkpointer (so "compare it to the last company I asked about"
works within the same session/thread).

Flow:

    START -> collector_node -> analyst_node -> END

State carried through the graph:
    company        : the company/ticker the user asked about this turn
    collector_report: raw text output from Agent 1
    analyst_report  : final text output from Agent 2
    session_history : running list of {company, summary} from earlier turns
                       in this thread -> this IS the cross-call memory.
"""

from __future__ import annotations

import operator
import time
from typing import Annotated, List, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents import build_collector_agent, build_analyst_agent

# Groq's Llama models occasionally emit a malformed tool-call (a raw
# "<function=...>" string instead of a proper structured call), which
# surfaces as groq.BadRequestError: 'tool_use_failed'. It's intermittent,
# not deterministic, so a short retry clears it almost every time.
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


class GraphState(TypedDict):
    company: str
    collector_report: str
    analyst_report: str
    # `operator.add` means each turn APPENDS to this list rather than
    # overwriting it -> this is how memory persists across turns in a thread.
    session_history: Annotated[List[dict], operator.add]


def _run_agent(agent, text_input: str) -> str:
    """
    Helper: invoke a react agent with a single human message, return final text.

    Wrapped with a short retry loop because Groq's tool-calling occasionally
    returns a malformed function-call string (see MAX_RETRIES comment above).
    Retrying the same request almost always succeeds since it's a sampling
    glitch, not a deterministic failure.
    """
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = agent.invoke({"messages": [{"role": "user", "content": text_input}]})
            return result["messages"][-1].content
        except Exception as e:  # noqa: BLE001 - intentionally broad, we log + retry
            last_error = e
            if attempt < MAX_RETRIES:
                print(
                    f"  [warning] Agent call failed (attempt {attempt}/{MAX_RETRIES}): "
                    f"{type(e).__name__}. Retrying..."
                )
                time.sleep(RETRY_DELAY_SECONDS)

    # All retries exhausted -> fail gracefully instead of crashing the whole graph
    return (
        f"[Error: this agent failed after {MAX_RETRIES} attempts due to a "
        f"transient API issue: {last_error}. Try running the query again.]"
    )


def build_graph(llm):
    """Compile the two agents into a memory-backed orchestrator graph."""
    collector_agent = build_collector_agent(llm)
    analyst_agent = build_analyst_agent(llm)

    def collector_node(state: GraphState) -> dict:
        company = state["company"]
        report = _run_agent(
            collector_agent,
            f"Gather current stock performance and recent news for: {company}",
        )
        return {"collector_report": report}

    def analyst_node(state: GraphState) -> dict:
        company = state["company"]
        collector_report = state["collector_report"]

        # Fold in prior turns from this session so the Analyst has real memory
        # of what's already been discussed, e.g. for comparative questions.
        history = state.get("session_history", [])
        history_context = ""
        if history:
            past = "\n".join(f"- {h['company']}: {h['summary']}" for h in history)
            history_context = (
                f"\n\nEARLIER IN THIS SESSION, these companies were already analyzed:\n{past}\n"
                "If relevant, briefly compare the current company to these."
            )

        prompt = (
            f"Company being analyzed: {company}\n\n"
            f"Data Collector's report:\n{collector_report}"
            f"{history_context}"
        )
        report = _run_agent(analyst_agent, prompt)

        # Compress this turn into a short memory entry for future turns.
        short_summary = report.split("\n\n")[0][:400]

        return {
            "analyst_report": report,
            "session_history": [{"company": company, "summary": short_summary}],
        }

    graph = StateGraph(GraphState)
    graph.add_node("collector", collector_node)
    graph.add_node("analyst", analyst_node)
    graph.add_edge(START, "collector")
    graph.add_edge("collector", "analyst")
    graph.add_edge("analyst", END)

    # MemorySaver = in-process checkpointer. Swap for SqliteSaver/PostgresSaver
    # if you need memory to survive a process restart.
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)
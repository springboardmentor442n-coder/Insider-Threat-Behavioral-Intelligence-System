"""
bot.py
------
A conversational knowledge bot that:
  - Remembers previous turns in the conversation (short-term memory)
  - Can search the web (DuckDuckGo) or Wikipedia when it needs current/factual
    information it doesn't already know
  - Gives contextual follow-up answers (e.g. "Where did he study?" after
    "Who is the CEO of OpenAI?")

Built with LangGraph's `create_react_agent`, which is the modern, actively
maintained replacement for LangChain's older `AgentExecutor` + memory classes
(those are now legacy/deprecated in current LangChain versions). We still
satisfy the assignment's requirement of "tools + memory + conversational
flow" — just with LangGraph's memory-via-checkpointer pattern instead of
`ConversationBufferMemory`.
"""

from __future__ import annotations

import time

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from tools import search_web, search_wikipedia

# Groq's Llama models occasionally emit a malformed tool-call (a raw
# "<function=...>" string instead of a proper structured call), which
# surfaces as groq.BadRequestError: 'tool_use_failed'. It's intermittent,
# not deterministic, so a short retry clears it almost every time.
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

SYSTEM_PROMPT = """You are a helpful, factual conversational knowledge assistant.

You have two tools available:
- `search_wikipedia`: best for stable, encyclopedic facts (people, places, history, science).
- `search_web`: best for current/recent information (news, "who is currently...", recent events).

Rules:
- If you already know the answer confidently and it's not time-sensitive, you may answer
  directly without calling a tool.
- If the question involves current facts, recent events, or something you're not certain
  about, use a tool rather than guessing.
- Use the ongoing conversation history to resolve references like "he", "she", "it", "that
  company" etc. to what was discussed earlier.
- Always give a direct, concise, factual answer. Cite the source tool briefly if you used one
  (e.g. "According to Wikipedia...").
- If you don't know and your tools don't help, say so honestly instead of making something up.
"""


def build_bot(llm):
    """
    Build the conversational agent.

    checkpointer=MemorySaver() gives the agent persistent conversation memory:
    every call to `.invoke()` with the same thread_id automatically has the
    full prior message history available to the model.
    """
    checkpointer = MemorySaver()
    agent = create_react_agent(
        model=llm,
        tools=[search_web, search_wikipedia],
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
        name="knowledge_bot",
    )
    return agent


def ask(agent, thread_id: str, user_message: str) -> str:
    """
    Send one message to the bot on a given conversation thread and return its reply.
    Because the agent was built with a checkpointer, we do NOT need to manually
    pass prior messages -- LangGraph retrieves them automatically via thread_id.

    Wrapped with a short retry loop because Groq's tool-calling occasionally
    returns a malformed function-call string (see MAX_RETRIES comment above).
    """
    config = {"configurable": {"thread_id": thread_id}}
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_message}]},
                config=config,
            )
            return result["messages"][-1].content
        except Exception as e:  # noqa: BLE001 - intentionally broad, we log + retry
            last_error = e
            if attempt < MAX_RETRIES:
                print(
                    f"  [warning] Bot call failed (attempt {attempt}/{MAX_RETRIES}): "
                    f"{type(e).__name__}. Retrying..."
                )
                time.sleep(RETRY_DELAY_SECONDS)

    return (
        f"[Sorry, I hit a transient API error {MAX_RETRIES} times in a row: "
        f"{last_error}. Please try asking again.]"
    )
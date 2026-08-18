"""
llm.py
------
Single place to configure the LLM. Uses Groq by default (free tier, fast,
no credit card required) so the whole project can be run for $0.

To switch providers, just change `get_llm()` — nothing else in the codebase
needs to know which provider is behind it, since we always return a
LangChain-compatible chat model.

NOTE: Groq deprecated their Llama chat models (llama-3.3-70b-versatile,
llama-3.1-8b-instant) in mid-2026. We now use openai/gpt-oss-120b, Groq's
officially recommended replacement for general-purpose + tool-calling
workloads. Same free tier, same tool-calling support.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.1):
    """
    Returns a LangChain-compatible chat model.

    Requires GROQ_API_KEY in your environment / .env file.
    Get a free key at: https://console.groq.com/keys
    """
    from langchain_groq import ChatGroq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. Create a .env file with:\n"
            "GROQ_API_KEY=your_key_here\n"
            "(get a free key at https://console.groq.com/keys)"
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=temperature,
        api_key=api_key,
    )
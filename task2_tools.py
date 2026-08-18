"""
tools.py
--------
Free, no-API-key tools for the conversational knowledge bot.

- search_wikipedia : stable encyclopedic facts
- search_web       : current/recent information via DuckDuckGo
"""

from __future__ import annotations

from typing import List

import wikipedia
from ddgs import DDGS
from langchain_core.tools import tool


@tool
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for stable, encyclopedic facts about a person, place, company,
    concept, or historical event. Best for questions like "Who is X", "What is Y",
    "Where did X study/found/live".

    Returns a short summary (a few sentences) of the most relevant Wikipedia article.
    """
    try:
        # auto_suggest helps match slightly imprecise queries to the right article
        results = wikipedia.search(query, results=3)
        if not results:
            return f"No Wikipedia article found for '{query}'."

        try:
            summary = wikipedia.summary(results[0], sentences=4, auto_suggest=False)
            return f"[Wikipedia: {results[0]}]\n{summary}"
        except wikipedia.DisambiguationError as e:
            # Multiple articles match -> just take the first suggested option
            option = e.options[0]
            summary = wikipedia.summary(option, sentences=4, auto_suggest=False)
            return f"[Wikipedia: {option}]\n{summary}"

    except Exception as e:
        return f"Wikipedia search failed for '{query}': {e}"


@tool
def search_web(query: str, max_results: int = 4) -> List[dict]:
    """
    Search the live web via DuckDuckGo for current/recent information --
    news, "who is currently the CEO of X", recent events, prices, etc.
    Use this instead of `search_wikipedia` when the question is time-sensitive.

    Returns a list of dicts with 'title', 'snippet', and 'url' for each result.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return [{"info": f"No web results found for '{query}'."}]

        return [
            {
                "title": r.get("title"),
                "snippet": r.get("body"),
                "url": r.get("href"),
            }
            for r in results
        ]
    except Exception as e:
        return [{"error": f"Web search failed for '{query}': {e}"}]

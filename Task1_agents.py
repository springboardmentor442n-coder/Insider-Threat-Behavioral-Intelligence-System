"""
agents.py
---------
Defines the two collaborating agents used in the Company Intelligence system.

Agent 1 - Data Collector : has access to real-world data tools (stock + news).
                            Its only job is to gather facts, never to opine.
Agent 2 - Analyst        : has access to a risk-calculation tool. Its job is to
                            reason over the Collector's facts and produce a
                            summary, insight list, and risk factors.

Both are built with LangGraph's `create_react_agent`, which gives each agent
autonomous tool-calling ability (it decides *when* and *how many times* to
call its tools) rather than us hard-coding a fixed tool-call sequence.
"""

from __future__ import annotations

from langgraph.prebuilt import create_react_agent

from tools import get_stock_performance, get_company_news, calculate_volatility

COLLECTOR_SYSTEM_PROMPT = """You are the Data Collector agent in a company intelligence system.

Your ONLY job is to gather factual, up-to-date data about the company you are asked about:
1. Call `get_stock_performance` to get real stock/price data.
2. Call `get_company_news` to get recent headlines.

Rules:
- Always call BOTH tools before answering.
- Do not analyze, speculate, or give opinions. You are a data-gathering agent, not an analyst.
- Return your findings as a clear, structured factual report: stock numbers first, then a
  bullet list of the news headlines with their sources.
- If a tool returns an error, state that clearly instead of making up data.
"""

ANALYST_SYSTEM_PROMPT = """You are the Analyst agent in a company intelligence system.

You will be given a factual report produced by the Data Collector agent (stock performance
+ recent news headlines). Your job is to turn that into a decision-useful analysis:

1. If you have a list of recent closing prices, call `calculate_volatility` to get a real,
   computed risk indicator. Do not eyeball volatility yourself.
2. Write a concise **Market Summary** (2-4 sentences).
3. List 3-5 **Key Insights** grounded in the actual numbers/news you were given.
4. List 2-4 **Risk Factors**, referencing the computed volatility band and any relevant
   news items.

Rules:
- Never invent numbers. Only reason over what the Collector actually gave you and what your
  tool returns.
- If the Collector's data contains an error, say so plainly instead of guessing.
- Keep the tone professional and analytical, like a sell-side research note.
"""


def build_collector_agent(llm):
    """Agent 1: gathers stock + news facts. Bound to data-fetching tools only."""
    return create_react_agent(
        model=llm,
        tools=[get_stock_performance, get_company_news],
        prompt=COLLECTOR_SYSTEM_PROMPT,
        name="data_collector",
    )


def build_analyst_agent(llm):
    """Agent 2: reasons over the Collector's facts. Bound to the risk-calc tool only."""
    return create_react_agent(
        model=llm,
        tools=[calculate_volatility],
        prompt=ANALYST_SYSTEM_PROMPT,
        name="analyst",
    )

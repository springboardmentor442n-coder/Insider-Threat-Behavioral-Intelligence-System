# Task 1 — Company Intelligence Multi-Agent System

A two-agent system, orchestrated with **LangGraph**, that researches a company and produces
an analyst-style intelligence report — with real memory across multiple companies in a session.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              ORCHESTRATOR                │
                    │         (LangGraph StateGraph)            │
                    └─────────────────────────────────────────┘

   user input: "NVDA"
          │
          ▼
   ┌─────────────────┐        tools:                ┌─────────────────┐
   │   AGENT 1        │──────► get_stock_performance │   AGENT 2        │
   │  Data Collector   │──────► get_company_news      │    Analyst       │
   │  (react agent)    │                              │  (react agent)   │
   └─────────────────┘                              └─────────────────┘
          │                                                    ▲
          │  collector_report (facts only)                     │
          └───────────────────────────────────────────────────►│
                                                                 │
                                            tool: calculate_volatility
                                                                 │
                                                                 ▼
                                              analyst_report (summary,
                                              insights, risk factors)
                                                                 │
                                                                 ▼
                                         session_history (memory, appended
                                         every turn via a MemorySaver
                                         checkpointer keyed by thread_id)
```

**Flow:** `START → collector → analyst → END`

- **Agent 1 (Data Collector)** is a LangGraph `create_react_agent` bound to two tools:
  `get_stock_performance` (via `yfinance`) and `get_company_news` (via DuckDuckGo search).
  Its system prompt restricts it to fact-gathering only — no opinions.
- **Agent 2 (Analyst)** is a second `create_react_agent` bound to one tool,
  `calculate_volatility`, which computes a real standard-deviation-based risk indicator
  instead of letting the LLM guess. It reasons over Agent 1's report to produce a market
  summary, key insights, and risk factors.
- **Orchestrator**: a `StateGraph` wires the two agents together and passes a typed
  `GraphState` between them. A `MemorySaver` checkpointer persists `session_history`
  across every `.invoke()` call sharing the same `thread_id`, so the Analyst can say
  things like *"unlike NVDA discussed earlier, AMD's volatility is..."*.

## Why two *agents* and not just two functions?

Each agent decides for itself when/whether to call its tools (via the ReAct loop), rather
than us hard-coding "always call tool X then tool Y". This is what LangGraph's
`create_react_agent` gives us over a plain function call chain, and is the "agent workflow"
behaviour the task asks to demonstrate.

## Setup

```bash
cd task1_multi_agent_system
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your free Groq key (https://console.groq.com/keys)
```

## Run it

**CLI:**
```bash
python main.py
```

**Streamlit UI:**
```bash
streamlit run app.py
```

**Notebook (step-by-step, shows tool outputs individually):**
```bash
jupyter notebook demo_notebook.ipynb
```

## Example session

```
Company/Ticker > Nvidia

[Data Collector] gathering stock + news data for 'Nvidia'...

--- COLLECTOR REPORT ---
Stock Performance (NVDA):
- Last close: $184.23
- 5-day change: +3.1%
- 1-month change: +11.4%
- 52-week range: $86.62 - $195.62
...

Recent headlines:
- "Nvidia unveils next-gen AI chip roadmap" (Reuters, 2 days ago)
...

--- ANALYST REPORT ---
Market Summary: NVDA continues its AI-driven rally, up 11.4% over the past month...

Key Insights:
- Momentum is being driven primarily by data-center/AI demand headlines...

Risk Factors:
- Computed volatility (std dev of daily returns): 2.8% -> Moderate risk band
- Concentration risk: heavy dependence on AI capex cycle
...

Company/Ticker > AMD

--- ANALYST REPORT ---
Market Summary: AMD is also benefiting from AI tailwinds, though with lower volatility
than NVDA (discussed above)...
```

Note how the second turn references NVDA — that's the cross-agent-call memory at work.

## Files

| File | Purpose |
|---|---|
| `tools.py` | Free, no-key tools: stock data, news search, volatility calc |
| `agents.py` | Defines the Collector and Analyst react-agents + their prompts |
| `graph.py` | LangGraph `StateGraph` orchestrator + memory checkpointer |
| `llm.py` | LLM provider setup (Groq, swappable) |
| `main.py` | CLI entry point |
| `app.py` | Streamlit UI (bonus) |
| `demo_notebook.ipynb` | Step-by-step reproducible walkthrough (bonus) |

## Design notes / trade-offs

- **Why Groq?** Free tier, no credit card, fast inference — keeps this runnable at zero cost.
  Swapping providers only requires editing `llm.py`.
- **Why DuckDuckGo for news instead of a paid news API?** No API key required, keeps the
  project runnable out-of-the-box. `duckduckgo-search` is rate-limited for heavy use — for
  production you'd swap in NewsAPI/Finnhub with a key.
- **Memory choice:** `MemorySaver` is in-process (lost on restart). For persistent memory
  across restarts, swap it for `SqliteSaver` or `PostgresSaver` — the rest of the code is
  unaffected since they share the same `BaseCheckpointSaver` interface.

# Task 2 — Conversational Knowledge Bot

A LangGraph-based chat agent that remembers the conversation, and can reach for a search tool
when it needs current or verifiable facts instead of guessing.

## Tools

| Tool | Backend | When the agent uses it |
|---|---|---|
| `search_wikipedia` | `wikipedia` package (free, no key) | Stable, encyclopedic facts — people, places, companies, history, science |
| `search_web` | DuckDuckGo search (free, no key) | Current/recent information — news, "who is currently...", live events |

The agent decides autonomously which tool (if either) to call based on its system prompt —
we don't hard-code "always search first."

## Memory design

The assignment suggests `ConversationChain` / `AgentExecutor` + `ConversationBufferMemory`.
Those classes are **legacy** in current LangChain (superseded by LangGraph, which LangChain's
own docs now recommend for anything involving tools + memory). This project uses LangGraph's
`create_react_agent(..., checkpointer=MemorySaver())` instead, which gives the same practical
behaviour with the actively-maintained approach:

- Every `.invoke()` call is scoped to a `thread_id`.
- The checkpointer automatically loads the full prior message history for that thread and
  appends the new turn to it — no manual buffer management needed.
- This is functionally equivalent to `ConversationBufferMemory` (full history, no summarization
  or truncation), just implemented via LangGraph's state persistence instead of a separate
  memory object bolted onto an `AgentExecutor`.

To reset the conversation, just start a new `thread_id` (the Streamlit UI's "New conversation"
button does exactly this).

## Setup

```bash
cd task2_conversational_bot
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and add your free Groq key (https://console.groq.com/keys)
```

## Run it

**CLI:**
```bash
python main.py
```

**Streamlit chat UI:**
```bash
streamlit run app.py
```

## Sample chat log

```
You > Who is the CEO of OpenAI?
Bot > According to Wikipedia, Sam Altman is the CEO of OpenAI. He has led the
      company since 2019 (with a brief, widely-reported removal and
      reinstatement in November 2023).

You > Where did he study?
Bot > Sam Altman studied Computer Science at Stanford University, though he
      dropped out after two years to found his first startup, Loopt.

You > What's the latest news about him?
Bot > [search_web tool called: "Sam Altman latest news"]
      Recent coverage discusses OpenAI's latest model releases and Altman's
      public comments on AI safety and compute infrastructure investment.
      For the most current headlines, I'd recommend checking a live news
      source, as my search results are a snapshot from just now.

You > quit
Goodbye!
```

Note how turn 2 ("Where did he study?") correctly resolves "he" to Sam Altman using
conversation memory — no need to repeat the name.

## Files

| File | Purpose |
|---|---|
| `tools.py` | Wikipedia + DuckDuckGo web search tools |
| `bot.py` | Agent definition, system prompt, memory checkpointer |
| `llm.py` | LLM provider setup (Groq, swappable) |
| `main.py` | CLI chat loop |
| `app.py` | Streamlit chat UI (bonus) |

## Design notes

- **Why LangGraph over `AgentExecutor`?** LangChain's own migration guide marks
  `AgentExecutor` + `ConversationBufferMemory` as legacy in favor of LangGraph agents. Using
  the current recommended pattern while still fully satisfying the assignment's functional
  requirements (memory + tools + conversational flow).
- **Why two search tools instead of one?** Wikipedia is more reliable/precise for stable facts
  and doesn't get diluted by SEO spam; DuckDuckGo is necessary for anything time-sensitive
  that Wikipedia won't have. Giving the agent both and letting it choose mirrors how a real
  research assistant would work.

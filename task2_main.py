"""
main.py
-------
CLI chat loop for the Conversational Knowledge Bot.

Run:
    python main.py

Type 'quit' to exit. Conversation memory persists for the whole session,
so you can ask a factual question and then a contextual follow-up
(e.g. "Who is the CEO of OpenAI?" then "Where did he study?").
"""

import uuid

from llm import get_llm
from bot import build_bot, ask


def main():
    print("=" * 70)
    print(" Conversational Knowledge Bot  (LangGraph + Wikipedia/Web search + memory)")
    print("=" * 70)
    print("Ask me anything. Type 'quit' to exit.\n")

    llm = get_llm()
    agent = build_bot(llm)
    thread_id = str(uuid.uuid4())  # one thread = one continuous memory session

    while True:
        user_message = input("You > ").strip()
        if not user_message:
            continue
        if user_message.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        reply = ask(agent, thread_id, user_message)
        print(f"Bot > {reply}\n")


if __name__ == "__main__":
    main()

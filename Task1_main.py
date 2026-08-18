"""
main.py
-------
CLI entry point for the Company Intelligence multi-agent system.

Run:
    python main.py

Then type a company/ticker (e.g. "Nvidia" or "TSLA") at each prompt.
Type 'quit' to exit. Memory persists across companies within one run,
so you can ask about several companies and the Analyst will reference
earlier ones when relevant.
"""

from llm import get_llm
from graph import build_graph


def main():
    print("=" * 70)
    print(" Company Intelligence Agentic System  (Data Collector -> Analyst)")
    print("=" * 70)
    print("Type a company name or ticker (e.g. 'Nvidia', 'TSLA', 'Amazon').")
    print("Type 'quit' to exit.\n")

    llm = get_llm()
    app = build_graph(llm)

    # A single thread_id = one continuous session with shared memory.
    thread_config = {"configurable": {"thread_id": "cli-session-1"}}

    while True:
        company = input("Company/Ticker > ").strip()
        if not company:
            continue
        if company.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        print(f"\n[Data Collector] gathering stock + news data for '{company}'...")
        result = app.invoke({"company": company}, config=thread_config)

        print("\n--- COLLECTOR REPORT ---")
        print(result["collector_report"])

        print("\n--- ANALYST REPORT ---")
        print(result["analyst_report"])
        print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    main()

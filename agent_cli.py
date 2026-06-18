from kb import KnowledgeBase
from agent import Agent

from tools import TOOLS, tool_schemas
from agent import SYSTEM_PROMPT
from client import client


def main():

    print("Loading knowledge base...")

    kb = KnowledgeBase(
        "documents"
    )

    print(
        f"Loaded {len(kb.chunks)} chunks"
    )

    agent = Agent(
        client=client,
        kb=kb,
        tools=TOOLS,
        tool_schemas=tool_schemas,
        SYSTEM_PROMPT=SYSTEM_PROMPT,
        model="qwen2.5:7b",
        temperature=0.0,
        max_steps=10
    )

    print()
    print("Agent ready.")
    print("Type 'exit' to quit.")
    print()

    while True:

        question = input(
            "Question > "
        ).strip()

        if not question:
            continue

        if question.lower() in {
            "exit",
            "quit"
        }:
            break

        print()
        print("Thinking...")
        print()

        try:

            answer = agent.run(
                question
            )

            print(answer)
            print()

        except Exception as e:

            print(
                f"Error: {e}"
            )
            print()


if __name__ == "__main__":
    main()
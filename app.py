from openai import OpenAI
from agent import run_agent
from kb import KnowledgeBase

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

kb = KnowledgeBase("./documents")

def main():
    question = input()
    answer = run_agent(
        client,
        question,
        kb
    )
    print(answer)


if __name__ == "main":
    main()
import os

from openai import OpenAI


USE_OLLAMA = True


if USE_OLLAMA:

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

else:

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv(
            "OPENROUTER_API_KEY"
        )
    )
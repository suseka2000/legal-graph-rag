import os

from openai import OpenAI

from config import OLLAMA_BASE_URL, OLLAMA_API_KEY


USE_OLLAMA = True


if USE_OLLAMA:

    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY
    )

else:

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv(
            "OPENROUTER_API_KEY"
        )
    )
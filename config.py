import os

from dotenv import load_dotenv

load_dotenv()


MODEL = os.getenv(
    "MODEL",
    "qwen2.5:7b"
)

TEMPERATURE = float(
    os.getenv(
        "TEMPERATURE",
        0.0
    )
)

MAX_STEPS = int(
    os.getenv(
        "MAX_STEPS",
        10
    )
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "intfloat/multilingual-e5-small"
)

UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    "uploads"
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434/v1"
)

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY",
    "ollama"
)
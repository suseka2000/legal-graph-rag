from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os

from kb import KnowledgeBase
from agent import Agent

from tools import TOOLS, tool_schemas
from agent import SYSTEM_PROMPT
from client import client

from config import UPLOAD_DIR


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


kb = None
agent = None

@app.post("/upload-file")
def upload_file(
    file: UploadFile = File(...)
):

    path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "filename": file.filename
    }


@app.post("/build-kb")
def build_kb():

    global kb
    global agent

    kb = KnowledgeBase(
        UPLOAD_DIR
    )

    agent = Agent(
        client=client,
        kb=kb,
        tools=TOOLS,
        tool_schemas=tool_schemas,
        SYSTEM_PROMPT = SYSTEM_PROMPT,
        model="qwen2.5:7b",
        temperature=0.5,
        max_steps=10
    )

    return {
        "status": "ready",
        "chunks": len(
            kb.chunks
        )
    }


@app.post("/query")
def query(
    data: dict
):

    if agent is None:

        return JSONResponse(
            status_code=400,
            content={
                "error":
                "Knowledge base not initialized"
            }
        )

    question = data[
        "question"
    ]

    answer = agent.run(
        question
    )

    return {
        "answer": answer
    }

app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)
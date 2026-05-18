from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import shutil
import os

from rag import (
    process_resume,
    ask_question,
    calculate_ats_score
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def home():

    return {
        "message": "Resume RAG Backend Running"
    }

@app.post("/upload")
async def upload_resume(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    process_resume(file_path)

    return {
        "message":
        "Resume uploaded and processed successfully"
    }

@app.post("/chat")
def chat(request: QueryRequest):

    response = ask_question(
        request.query
    )

    return {
        "response": response
    }

@app.get("/ats")
def ats_score():

    response = calculate_ats_score()

    return {
        "response": response
    }
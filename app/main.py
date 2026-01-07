from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil
import os

from app.ingestion import extract_text
from app.embeddings import chunk_text, get_embedding
from app.vector_store import add_to_vector_store
from app.retrieval import retrieve_relevant_chunks, retrieve_relevant_chunks_with_sources
from app.qa import generate_answer_stream

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# your routes below


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = file.filename.split(".")[-1]
    text = extract_text(file_path, file_type)
    chunks = chunk_text(text)

    embeddings = [get_embedding(chunk) for chunk in chunks]
    metadatas = [{"source": file.filename} for _ in chunks]

    add_to_vector_store(chunks, embeddings, metadatas)

    return {"message": "Document indexed successfully"}

class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(payload: QuestionRequest):
    question = payload.question
    contexts, sources = retrieve_relevant_chunks_with_sources(question)

    if not contexts:
        return {"answer": "No documents found to answer your question.", "citations": []}

    return StreamingResponse(
    generate_answer_stream(question, contexts),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # 🔥 VERY IMPORTANT
    }

)



@app.post("/clear-chat")
async def clear_chat():
    """Clear chat history (handled on frontend)"""
    return {"message": "Chat cleared successfully"}


@app.post("/reset")
async def reset_knowledge_base():
    """Reset the vector store and remove all documents and uploaded files"""
    try:
        from app.vector_store import client
        
        # Clear vector store
        try:
            client.delete_collection(name="documents")
            client.get_or_create_collection(name="documents")
        except Exception as e:
            print(f"Warning: Could not delete collection: {e}")
            # Continue anyway to clear files
        
        # Clear uploaded files
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        return {"message": "Knowledge base reset successfully. All documents and uploaded files have been removed."}
    except Exception as e:
        print(f"Error resetting knowledge base: {e}")
        return {
            "message": "Error: Could not completely reset knowledge base. Please check server logs.",
            "error": str(e)
        }

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil
import os
from typing import List

from app.ingestion import extract_text
from app.embeddings import chunk_text, get_embedding
from app.vector_store import add_to_vector_store
from app.retrieval import retrieve_relevant_chunks, retrieve_relevant_chunks_with_sources
from app.qa import generate_answer_stream_with_citations

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
    pages = extract_text(file_path, file_type)

    chunks_all = []
    embeddings_all = []
    metadatas_all = []

    for page_idx, page_text in enumerate(pages, start=1):
        chunks = chunk_text(page_text)
        for chunk_idx, chunk in enumerate(chunks, start=1):
            chunk_id = f"{file.filename}_p{page_idx}_c{chunk_idx}"
            chunks_all.append(chunk)
            embeddings_all.append(get_embedding(chunk))
            metadatas_all.append({
                "source": file.filename,
                "file_name": file.filename,
                "page": page_idx,
                "chunk_id": chunk_id
            })

    if chunks_all:
        add_to_vector_store(chunks_all, embeddings_all, metadatas_all)

    return {"message": "Document indexed successfully"}

@app.post("/upload-multiple")
async def upload_documents_batch(files: List[UploadFile] = File(...)):
    """Upload multiple documents at once"""
    uploaded_files = []
    
    for file in files:
        try:
            file_path = f"{UPLOAD_DIR}/{file.filename}"
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_type = file.filename.split(".")[-1]
            pages = extract_text(file_path, file_type)

            chunks_all = []
            embeddings_all = []
            metadatas_all = []

            for page_idx, page_text in enumerate(pages, start=1):
                chunks = chunk_text(page_text)
                for chunk_idx, chunk in enumerate(chunks, start=1):
                    chunk_id = f"{file.filename}_p{page_idx}_c{chunk_idx}"
                    chunks_all.append(chunk)
                    embeddings_all.append(get_embedding(chunk))
                    metadatas_all.append({
                        "source": file.filename,
                        "file_name": file.filename,
                        "page": page_idx,
                        "chunk_id": chunk_id
                    })

            if chunks_all:
                add_to_vector_store(chunks_all, embeddings_all, metadatas_all)
            uploaded_files.append(file.filename)
        except Exception as e:
            print(f"Error processing file {file.filename}: {e}")
            continue
    
    return {
        "message": f"Successfully indexed {len(uploaded_files)} document(s)",
        "files": uploaded_files
    }

class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(payload: QuestionRequest):
    question = payload.question
    contexts, sources = retrieve_relevant_chunks_with_sources(question)
    
    print(f"Ask endpoint - Question: {question}")
    print(f"Ask endpoint - Retrieved {len(contexts)} contexts")
    print(f"Ask endpoint - Sources: {sources}")

    if not contexts:
        return {"answer": "No documents found to answer your question.", "citations": []}

    return StreamingResponse(
        generate_answer_stream_with_citations(question, contexts, sources),
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

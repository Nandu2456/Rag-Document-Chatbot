# RAG Document Chatbot - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Vite)                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                        App.jsx (Main)                        │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐  │  │
│  │  │  UploadPanel    │  │  ChatWindow      │  │ Controls   │  │  │
│  │  │  - File upload  │  │  - Messages      │  │ - Clear    │  │  │
│  │  │  - Progress     │  │  - Citations     │  │ - Reset    │  │  │
│  │  │  - Validation   │  │  - Streaming     │  │            │  │  │
│  │  └────────┬────────┘  └──────────┬───────┘  └────────────┘  │  │
│  │           │                      │                            │  │
│  │           └──────────┬───────────┘                            │  │
│  │                      │                                        │  │
│  │           ┌──────────▼──────────┐                            │  │
│  │           │  api.js (Service)   │                            │  │
│  │           │  - /upload          │                            │  │
│  │           │  - /ask (SSE)       │                            │  │
│  │           │  - /reset           │                            │  │
│  │           └──────────┬──────────┘                            │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTP/SSE
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                    BACKEND (FastAPI)                                │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  main.py (API Routes)                                         │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐   │  │
│  │  │ POST /upload    │  │ POST /ask        │  │ POST /reset│   │  │
│  │  │ - Single file   │  │ - Question       │  │ - Wipe DB  │   │  │
│  │  │ - Returns msg   │  │ - Returns SSE    │  │            │   │  │
│  │  └────────┬────────┘  └──────────┬───────┘  └────────────┘   │  │
│  │           │                      │                            │  │
│  │  POST /upload-multiple           │                            │  │
│  │  - Multiple files                │                            │  │
│  │  - Batch process                 │                            │  │
│  │  └────────┬───────────────────────┼────────────────────────┐  │  │
│  └───────────┼───────────────────────┼────────────────────────┼──┘  │
│              │                       │                        │      │
│  ┌───────────▼─────────┐   ┌─────────▼────────┐   ┌──────────▼────┐ │
│  │ INGESTION PIPELINE  │   │ RETRIEVAL ENGINE │   │ QA ENGINE     │ │
│  │                     │   │                  │   │               │ │
│  │ ingestion.py:       │   │ retrieval.py:    │   │ qa.py:        │ │
│  │ ┌─────────────────┐ │   │ ┌──────────────┐ │   │ ┌──────────┐  │ │
│  │ │ extract_text    │ │   │ │ retrieve_    │ │   │ │ generate_│  │ │
│  │ │ - PDF (pages)   │ │   │ │ relevant_    │ │   │ │ answer_  │  │ │
│  │ │ - DOCX          │ │   │ │ chunks_with_ │ │   │ │ stream_  │  │ │
│  │ │ - TXT/MD        │ │   │ │ sources      │ │   │ │ with_    │  │ │
│  │ │ Returns: list   │ │   │ │              │ │   │ │ citations│  │ │
│  │ │ of pages        │ │   │ │ 1. Query     │ │   │ │ ┌───────┐│  │ │
│  │ └────────┬────────┘ │   │ │    embedding │ │   │ │ │Format ││  │ │
│  │          │          │   │ │ 2. Search    │ │   │ │ │prompt ││  │ │
│  │ ┌────────▼────────┐ │   │ │    ChromaDB  │ │   │ │ │with   ││  │ │
│  │ │ chunk_text      │ │   │ │ 3. Return    │ │   │ │ │source ││  │ │
│  │ │ - Split pages   │ │   │ │    chunks +  │ │   │ │ │labels ││  │ │
│  │ │ - 800 tokens    │ │   │ │    metadata  │ │   │ │ └───────┘│  │ │
│  │ │ - 150 overlap   │ │   │ │              │ │   │ │ ┌───────┐│  │ │
│  │ │ Returns: chunks │ │   │ └──────────────┘ │   │ │ │Call   ││  │ │
│  │ └────────┬────────┘ │   │                  │   │ │ │LLM    ││  │ │
│  │          │          │   │                  │   │ │ │(Groq) ││  │ │
│  │ ┌────────▼────────┐ │   │                  │   │ │ └───────┘│  │ │
│  │ │ BUILD METADATA  │ │   │                  │   │ │ ┌───────┐│  │ │
│  │ │ - source (file) │ │   │                  │   │ │ │Parse  ││  │ │
│  │ │ - page number   │ │   │                  │   │ │ │citations│  │ │
│  │ │ - chunk_id      │ │   │                  │   │ │ │[1],[2]││  │ │
│  │ │ Per chunk!      │ │   │                  │   │ │ └───────┘│  │ │
│  │ └────────┬────────┘ │   │                  │   │ │ ┌───────┐│  │ │
│  │          │          │   │                  │   │ │ │Stream ││  │ │
│  │          └──────────┴──▶ vector_store.py   │   │ │ │answer ││  │ │
│  │                        │ (ChromaDB)        │   │ │ │+ only ││  │ │
│  │                        │ - add_to_vector   │   │ │ │cited  ││  │ │
│  │                        │   _store()        │   │ │ │sources││  │ │
│  │                        │ - search_vectors()│   │ │ └───────┘│  │ │
│  │                        └──────────┬────────┘   └──────────┘  │ │
│  │                                   │                          │  │
│  └───────────────────────────────────┼──────────────────────────┘  │
│                                      │                              │
└──────────────────────────────────────┼──────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┬──────────────┐
                    │                  │                  │              │
                    │                  │                  │              │
        ┌───────────▼─────────┐  ┌─────▼──────────┐  ┌───▼─────────┐  ┌▼────────────┐
        │ VECTOR STORE        │  │ EMBEDDINGS     │  │ LLM         │  │ FILE SYSTEM │
        │ (ChromaDB)          │  │ (Cohere)       │  │ (Groq/Kimi) │  │             │
        │                     │  │                │  │             │  │ uploads/    │
        │ Collections:        │  │ embed-english- │  │ Model:      │  │ - PDFs      │
        │ - documents         │  │ v3.0           │  │ kimi-k2-    │  │ - DOCX      │
        │                     │  │                │  │ instruct    │  │ - TXT       │
        │ Stores:            │  │ Input: chunk   │  │             │  │ - MD        │
        │ - Document text    │  │ text           │  │ Temperature │  │             │
        │ - Embeddings       │  │                │  │ = 0         │  │ Uploaded by │
        │ - Metadata         │  │ Output: vector │  │             │  │ /upload     │
        │   (file, page,     │  │ (1024-dim)     │  │ Returns:    │  │             │
        │    chunk_id)       │  │                │  │ - Answer    │  │ Cleared by  │
        │                     │  │                │  │ - Citations │  │ /reset      │
        │ Similarity search: │  │                │  │             │  │             │
        │ Returns:           │  │                │  │             │  │             │
        │ - Top K chunks     │  │                │  │             │  │             │
        │ - Metadata per     │  │                │  │             │  │             │
        │   chunk            │  │                │  │             │  │             │
        └─────────────────────┘  └────────────────┘  └─────────────┘  └─────────────┘
```

---

## Data Flow Diagram

### 1. Document Upload Flow

```
User uploads file (PDF/DOCX/TXT/MD)
           │
           ▼
POST /upload or /upload-multiple
           │
           ▼
extract_text(file_path, file_type)
  - Returns list of pages
           │
           ▼
For each page:
  │
  ├─ chunk_text(page_content)
  │  - Returns list of text chunks (800 tokens, 150 overlap)
  │
  ├─ For each chunk:
  │   │
  │   ├─ get_embedding(chunk)  ◄──────────► Cohere API
  │   │  - Returns [0.123, 0.456, ...]
  │   │
  │   ├─ Create metadata dict:
  │   │  {
  │   │    "source": "document.pdf",
  │   │    "file_name": "document.pdf",
  │   │    "page": 3,
  │   │    "chunk_id": "document.pdf_p3_c2"
  │   │  }
  │   │
  │   └─ Store chunk + embedding + metadata
  │       in ChromaDB
  │
           ▼
Return: "Document indexed successfully"
```

### 2. Question Answering Flow

```
User asks question: "What is OAuth2?"
           │
           ▼
POST /ask with QuestionRequest
           │
           ▼
retrieve_relevant_chunks_with_sources(question, top_k=5)
           │
           ├─ get_embedding(question)  ◄──────────► Cohere API
           │
           ├─ search_vectors(query_embedding, 5)  ◄──────────► ChromaDB
           │  Returns:
           │  {
           │    "documents": [["chunk1", "chunk2", ...]],
           │    "metadatas": [[{...}, {...}, ...]],
           │    ...
           │  }
           │
           └─ Flatten and return:
              chunks = [text1, text2, text3, ...]
              metadatas = [
                {"source": "auth.pdf", "page": 2, ...},
                {"source": "oauth.pdf", "page": 5, ...},
                ...
              ]
           │
           ▼
generate_answer_stream_with_citations(question, chunks, metadatas)
           │
           ├─ Build unique (file, page) keys from metadatas
           │  Result: [(auth.pdf, 2), (oauth.pdf, 5), ...]
           │
           ├─ Create numeric labels for each unique source
           │  [1] auth.pdf – page 2
           │  [2] oauth.pdf – page 5
           │  [3] spring.pdf – page 10
           │
           ├─ Format prompt with labeled contexts:
           │  """
           │  Available Sources:
           │  [1] auth.pdf – page 2
           │  [2] oauth.pdf – page 5
           │  ...
           │
           │  Context from sources:
           │  [1] (auth.pdf, page 2):
           │  OAuth2 is an authorization framework...
           │
           │  [2] (oauth.pdf, page 5):
           │  OAuth2 uses tokens for authorization...
           │  ...
           │
           │  Question: What is OAuth2?
           │  """
           │
           ├─ Call LLM (Groq/Kimi)  ◄──────────► Groq API
           │  Temperature = 0 (deterministic)
           │
           │  Returns:
           │  """
           │  OAuth2 is an authorization framework [1] that allows
           │  third-party applications to request access [2]. It uses
           │  tokens for secure communication [2].
           │  """
           │
           ├─ Parse numeric citations from answer
           │  Found: [1], [2]
           │
           ├─ Map citations back to sources
           │  [1] → {source: "auth.pdf", page: 2}
           │  [2] → {source: "oauth.pdf", page: 5}
           │
           └─ Stream to frontend (SSE):
              1. Character-by-character answer text
              2. Final SSE event with citations payload
                 {"citations": [
                   {"source": "auth.pdf", "page": 2},
                   {"source": "oauth.pdf", "page": 5}
                 ]}
           │
           ▼
Frontend receives streaming answer + citations
Display answer with clickable source links
```

---

## Component Architecture

### Backend Components

| Component | File | Responsibility |
|-----------|------|-----------------|
| **API Router** | `main.py` | Handle HTTP routes: `/upload`, `/ask`, `/reset` |
| **Ingestion** | `ingestion.py` | Extract text from PDF/DOCX/TXT/MD, return page list |
| **Chunking** | `embeddings.py` | Split pages into chunks, create embeddings |
| **Vector Store** | `vector_store.py` | Store/retrieve chunks with metadata in ChromaDB |
| **Retrieval** | `retrieval.py` | Query vector DB and return chunks + metadata aligned |
| **QA Engine** | `qa.py` | Format prompts, call LLM, parse citations from answer |

### Frontend Components

| Component | File | Responsibility |
|-----------|------|-----------------|
| **Main App** | `App.jsx` | State management, layout, routing |
| **Chat Window** | `ChatWindow.jsx` | Display messages, stream answer, show citations |
| **Upload Panel** | `UploadPanel.jsx` | File input, upload progress, error handling |
| **Controls** | `Controls.jsx` | Clear chat, reset KB buttons |
| **API Service** | `services/api.js` | HTTP client, SSE parsing |

---

## Data Schema

### Chunk Metadata (stored with each embedding)

```json
{
  "source": "spring_security.pdf",
  "file_name": "spring_security.pdf",
  "page": 5,
  "chunk_id": "spring_security.pdf_p5_c2"
}
```

### Retrieval Result

```json
{
  "documents": [
    ["OAuth2 is an authorization framework...", "JWT tokens..."]
  ],
  "metadatas": [
    [
      {"source": "spring.pdf", "page": 5, "chunk_id": "spring.pdf_p5_c2"},
      {"source": "auth.pdf", "page": 2, "chunk_id": "auth.pdf_p2_c1"}
    ]
  ]
}
```

### LLM Response to Frontend

```json
{
  "data": "OAuth2 is an authorization [1]..."
}
```

```json
{
  "citations": [
    {"source": "spring.pdf", "page": 5},
    {"source": "auth.pdf", "page": 2}
  ]
}
```

---

## Key Design Decisions

1. **Metadata Per Chunk**: Each chunk stores its source file and page number for accurate citations
2. **Numeric Labels in Prompts**: LLM sees [1], [2] labels tied to actual sources, preventing hallucinations
3. **Citation Parsing**: Extract [1], [2] from model output and map back to metadata (ground truth)
4. **Streaming**: Answer streams character-by-character; citations sent in final SSE event
5. **No Hallucinated Citations**: Only sources the model explicitly cited are returned to UI
6. **Page-Level Metadata**: PDFs track page numbers; other formats get single-page metadata

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18 + Vite |
| **Backend** | FastAPI |
| **Vector Database** | ChromaDB |
| **Embeddings** | Cohere (embed-english-v3.0) |
| **LLM** | Groq (Kimi K2 Instruct) |
| **Document Processing** | PyPDF, python-docx |
| **Async/Streaming** | FastAPI StreamingResponse, SSE |


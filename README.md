# Rag-Document-Chatbot

# 📄 RAG Document Chatbot

A **Retrieval-Augmented Generation (RAG) based Document Chatbot** that allows users to upload documents (PDF), index them, and ask questions to get contextual answers from the uploaded document.

This project consists of:

* ⚙️ **Backend** – Python + FastAPI (RAG pipeline)
* 🌐 **Frontend** – React + Vite (chat interface)

---

## ✨ Features

* Upload PDF documents
* Index documents for question answering
* Ask questions related to uploaded document
* Chat-style UI
* Reset chat memory and uploaded document
* Modular and clean code structure

---

## 🏗️ Project Structure

```text
RAG-document-chatbot/
│
├── app/                     # Backend (FastAPI)
│   ├── main.py              # API entry point
│   ├── rag_pipeline.py      # RAG logic (embedding + retrieval + LLM)
│   ├── loaders.py           # PDF loading and text extraction
│   ├── vector_store.py      # Vector DB / embeddings logic
│   └── config.py            # Configurations
│
├── rag-chat-frontend/       # Frontend (React)
│   ├── src/
│   │   ├── components/      # UI components (ChatWindow, UploadPanel, etc.)
│   │   ├── services/        # API calls
│   │   ├── App.jsx          # Main React app
│   │   └── main.jsx         # Entry point
│   ├── index.html
│   └── package.json
│
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## 🧠 How the RAG System Works

1. User uploads a **PDF document**
2. Backend extracts text from the document
3. Text is split into chunks
4. Chunks are converted into **embeddings**
5. Embeddings are stored in a vector store
6. When a question is asked:

   * Relevant chunks are retrieved
   * Context + question is sent to the LLM
   * Answer is generated based on document content

---

## ⚙️ Tech Stack

### Backend

* Python **3.10+**
* FastAPI
* LangChain
* Vector Database (FAISS / Chroma)
* LLM (OpenAI / Llama – configurable)

### Frontend

* Node.js **18+**
* React **18**
* Vite
* Axios

---

## 🚀 How to Run Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Nandu2456/Rag-Document-Chatbot.git
cd RAG-document-chatbot
```

---

### 2️⃣ Backend Setup (FastAPI)

#### Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Create `.env` file

Create a .env file in the root directory:

GROQ_API_KEY=your_groq_api_key
COHERE_API_KEY=your_cohere_api_key

#### Run Backend Server

```bash
uvicorn app.main:app --reload
```

Backend will run at:
👉 `http://localhost:8000`

---

### 3️⃣ Frontend Setup (React)

```bash
cd rag-chat-frontend
npm install
npm run dev
```

Frontend will run at:
👉 `http://localhost:5173`

---

## 🔁 API Flow

* `POST /upload` → Upload and index document
* `POST /ask` → Ask questions
* `POST /reset` → Clear chat memory / document context

---

## 🧪 Example Usage

1. Upload a PDF document
2. Ask: *"What is OOP?"*
3. Model answers using document content
4. Reset to upload a new document

---

## 📌 Future Improvements

* Streaming token-by-token responses
* Multiple document support
* Document preview
* Authentication
* Better prompt flexibility

---

demo: https://drive.google.com/file/d/1WYT7tyLM9pglhBfQxA3v-hMJ2vyLNkPe/view?usp=sharing

## 👤 Author

**Nandini Gourishetti**
GitHub: [https://github.com/Nandu2456](https://github.com/Nandu2456)

---





import tiktoken
import cohere
from app.config import COHERE_API_KEY

# Initialize Cohere client
co = cohere.ClientV2(api_key=COHERE_API_KEY)

def chunk_text(text, chunk_size=800, overlap=150):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk = tokens[start:end]
        chunks.append(tokenizer.decode(chunk))
        start += chunk_size - overlap

    return chunks



def get_embedding(text: str):
    response = co.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_document"
    )

    # ✅ THIS IS THE FIX
    embedding = response.embeddings.float[0]

    # Ensure pure list of floats
    return list(map(float, embedding))

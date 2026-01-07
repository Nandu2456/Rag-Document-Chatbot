from app.vector_store import search_vectors
from app.embeddings import get_embedding

def retrieve_relevant_chunks(query: str, top_k=5):
    query_embedding = get_embedding(query)
    results = search_vectors(query_embedding, top_k)

    return results

def retrieve_relevant_chunks_with_sources(query: str, top_k=5):
    query_embedding = get_embedding(query)
    results = search_vectors(query_embedding, top_k)
    
    chunks = results.get("documents", [[]])[0] if results.get("documents") else []
    metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
    
    return chunks, metadatas

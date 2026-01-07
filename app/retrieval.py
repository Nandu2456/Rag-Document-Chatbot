from app.vector_store import search_vectors
from app.embeddings import get_embedding

def retrieve_relevant_chunks(query: str, top_k=5):
    query_embedding = get_embedding(query)
    results = search_vectors(query_embedding, top_k)

    return results

def retrieve_relevant_chunks_with_sources(query: str, top_k=5):
    query_embedding = get_embedding(query)
    results = search_vectors(query_embedding, top_k)
    
    # ChromaDB returns: {'documents': [[chunk1, chunk2...]], 'metadatas': [[{}, {}...]], ...}
    documents_nested = results.get("documents", [[]])
    metadatas_nested = results.get("metadatas", [[]])

    # Flatten from nested lists (ChromaDB returns list of lists)
    chunks = documents_nested[0] if documents_nested else []
    chunk_metadatas = metadatas_nested[0] if metadatas_nested else []

    # Log for debugging
    print(f"Retrieved {len(chunks)} chunks")

    return chunks, chunk_metadatas

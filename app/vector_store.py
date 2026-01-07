import chromadb
import uuid

client = chromadb.Client()

def get_collection():
    """Get or create the documents collection. Called dynamically to handle resets."""
    return client.get_or_create_collection(name="documents")

def add_to_vector_store(chunks, embeddings, metadatas):
    collection = get_collection()
    # Generate unique IDs for each chunk to avoid collisions when adding multiple documents
    chunk_ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    collection.add(
        documents=chunks,
        embeddings=embeddings,   # embeddings = List[List[float]]
        metadatas=metadatas,
        ids=chunk_ids
    )


def search_vectors(query_embedding, top_k=5):
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],  # must be list of lists
        n_results=top_k
    )
    return results

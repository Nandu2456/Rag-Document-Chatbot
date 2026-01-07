import chromadb

client = chromadb.Client()

def get_collection():
    """Get or create the documents collection. Called dynamically to handle resets."""
    return client.get_or_create_collection(name="documents")

def add_to_vector_store(chunks, embeddings, metadatas):
    collection = get_collection()
    collection.add(
    documents=chunks,
    embeddings=embeddings,   # embeddings = List[List[float]]
    metadatas=metadatas,
    ids=[str(i) for i in range(len(chunks))])


def search_vectors(query_embedding, top_k=5):
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],  # must be list of lists
        n_results=top_k
    )
    return results

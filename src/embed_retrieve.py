import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("documents/chunks/chunks.jsonl")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "livingstone_unofficial_guide"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4


def load_chunks():
    chunks = []

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {CHUNKS_FILE}. Run src/document_pipeline.py first."
        )

    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def build_vector_store():
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks.")

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    existing_collections = [collection.name for collection in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        print("Deleting old collection so we can rebuild cleanly...")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["id"])
        documents.append(chunk["text"])
        metadatas.append(
            {
                "source_file": chunk["source_file"],
                "title": chunk["title"],
                "url": chunk["url"],
                "source_type": chunk["source_type"],
                "chunk_index": chunk["chunk_index"],
                "word_count": chunk["word_count"],
            }
        )

    print("Embedding chunks...")
    embeddings = model.encode(documents, normalize_embeddings=True).tolist()

    print("Adding chunks to ChromaDB...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Vector store built successfully with {collection.count()} chunks.")
    return collection, model


def retrieve(query, collection, model, top_k=TOP_K):
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []

    for i in range(len(results["documents"][0])):
        retrieved.append(
            {
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return retrieved


def print_results(query, results):
    print("\n" + "=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    for i, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print(f"\nResult {i}")
        print("-" * 100)
        print(f"Distance: {result['distance']:.4f}")
        print(f"Source: {metadata.get('title')}")
        print(f"File: {metadata.get('source_file')}")
        print(f"Chunk index: {metadata.get('chunk_index')}")
        print(f"URL: {metadata.get('url')}")
        print()
        print(result["text"][:900])
        print()


def main():
    collection, model = build_vector_store()

    test_queries = [
        "What do students say are the main strengths of Livingstone College?",
        "What are common complaints students mention about Livingstone College?",
        "What dining or meal plan information is available for Livingstone students?",
    ]

    for query in test_queries:
        results = retrieve(query, collection, model, top_k=TOP_K)
        print_results(query, results)


if __name__ == "__main__":
    main()
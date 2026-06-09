import json
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("documents/chunks/chunks.jsonl")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "livingstone_unofficial_guide"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4
LLM_MODEL = "llama-3.3-70b-versatile"


load_dotenv()


def load_chunks():
    chunks = []

    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def get_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        print("ChromaDB collection is empty. Building vector store...")
        chunks = load_chunks()
        model = get_embedding_model()

        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "source_file": chunk["source_file"],
                "title": chunk["title"],
                "url": chunk["url"],
                "source_type": chunk["source_type"],
                "chunk_index": chunk["chunk_index"],
                "word_count": chunk["word_count"],
            }
            for chunk in chunks
        ]

        embeddings = model.encode(documents, normalize_embeddings=True).tolist()

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    return collection


MODEL = get_embedding_model()
COLLECTION = get_collection()


def retrieve(query, top_k=TOP_K):
    query_embedding = MODEL.encode([query], normalize_embeddings=True).tolist()

    results = COLLECTION.query(
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


def build_context(retrieved_chunks):
    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        metadata = chunk["metadata"]
        context_parts.append(
            f"""
[Source {i}]
Title: {metadata.get("title")}
File: {metadata.get("source_file")}
URL: {metadata.get("url")}
Distance: {chunk["distance"]:.4f}

Text:
{chunk["text"]}
"""
        )

    return "\n\n".join(context_parts)


def generate_answer(question, retrieved_chunks):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Check your .env file.")

    client = Groq(api_key=api_key)
    context = build_context(retrieved_chunks)

    system_prompt = """
You are a grounded RAG assistant for a student guide project.

Rules:
1. Answer using ONLY the provided retrieved document context.
2. Do NOT use outside knowledge.
3. If the retrieved context does not contain enough information, say:
   "I don't have enough information in the provided documents to answer that."
4. Be concise and helpful.
5. Mention source titles naturally in the answer when possible.
"""

    user_prompt = f"""
Question:
{question}

Retrieved document context:
{context}

Write a grounded answer using only the retrieved context.
"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def format_sources(retrieved_chunks):
    seen = set()
    sources = []

    for chunk in retrieved_chunks:
        metadata = chunk["metadata"]
        key = (metadata.get("title"), metadata.get("url"))

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "title": metadata.get("title"),
                "file": metadata.get("source_file"),
                "url": metadata.get("url"),
                "distance": round(chunk["distance"], 4),
            }
        )

    return sources


def ask(question):
    retrieved_chunks = retrieve(question, top_k=TOP_K)
    answer = generate_answer(question, retrieved_chunks)
    sources = format_sources(retrieved_chunks)

    return {
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": retrieved_chunks,
    }


if __name__ == "__main__":
    test_questions = [
        "What do students say are the main strengths of Livingstone College?",
        "What dining or meal plan information is available for Livingstone students?",
        "What scholarships does Livingstone offer for computer science students?",
    ]

    for question in test_questions:
        print("\n" + "=" * 100)
        print(f"QUESTION: {question}")
        result = ask(question)
        print("\nANSWER:")
        print(result["answer"])
        print("\nSOURCES:")
        for source in result["sources"]:
            print(f"- {source['title']} ({source['file']}) distance={source['distance']}")
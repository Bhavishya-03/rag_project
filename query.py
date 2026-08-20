import chromadb
from chromadb.utils import embedding_functions

DB_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=DB_PATH)

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="document_buckets",
    embedding_function=embedding_func
)

def retrieve_context(user_query: str, top_k: int = 3, max_distance: float = 0.65) -> list:
    """Retrieves context without spamming the terminal with debug logs."""
    results = collection.query(
        query_texts=[user_query],
        n_results=top_k
    )

    retrieved_chunks = []
    
    if results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else []

        for idx, doc in enumerate(docs):
            dist = distances[idx] if idx < len(distances) else 1.0
            if dist <= max_distance:
                retrieved_chunks.append({
                    "text": doc,
                    "metadata": metas[idx],
                    "distance": dist
                })

    return retrieved_chunks

def format_prompt(user_query: str, retrieved_chunks: list) -> str:
    context_str = ""
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        filename = chunk["metadata"].get("filename", "Unknown")
        bucket = chunk["metadata"].get("bucket", "Unknown")
        context_str += f"\n[Source {idx} - File: {filename} (Bucket: {bucket})]\n{chunk['text']}\n"

    prompt = f"""You are an intelligent document assistant.
Answer the user's question clearly based on the provided context below.

Guidelines:
- Match related terms, synonyms,singular and plurals, or merged subcategories (e.g., treat "herbs" as matching "Herbs/Spices", and "beans" as matching "Beans/Legumes" or specific bean varieties like "Kidney/Pinto Beans" or "Green Beans").
- Synthesize facts logically from the text instead of requiring exact word matches.
- Format responses using clear markdown bullet points.
- If the requested topic is truly not mentioned in any form, state that context is missing.

CONTEXT:
{context_str}

QUESTION:
{user_query}

ANSWER:"""
    return prompt
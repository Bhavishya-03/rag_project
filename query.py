# import chromadb
# from chromadb.utils import embedding_functions

# DB_PATH = "./chroma_db"
# chroma_client = chromadb.PersistentClient(path=DB_PATH)

# embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
#     model_name="all-MiniLM-L6-v2"
# )

# collection = chroma_client.get_or_create_collection(
#     name="document_buckets",
#     embedding_function=embedding_func
# )

# def retrieve_context(user_query: str, top_k: int = 3, max_distance: float = 0.55) -> list:
#     """
#     Retrieves top_k chunks and filters out any chunk with a distance higher than max_distance.
#     """
#     results = collection.query(
#         query_texts=[user_query],
#         n_results=top_k
#     )

#     retrieved_chunks = []
    
#     if results and results["documents"]:
#         docs = results["documents"][0]
#         metas = results["metadatas"][0]
#         distances = results["distances"][0] if "distances" in results else []

#         for idx, doc in enumerate(docs):
#             dist = distances[idx] if idx < len(distances) else 1.0
            
#             if dist <= max_distance:
#                 retrieved_chunks.append({
#                     "text": doc,
#                     "metadata": metas[idx],
#                     "distance": dist
#                 })
#             else:
#                 print(f"  [Filtered Out] Chunk distance {dist:.3f} exceeded max_distance ({max_distance})")

#     return retrieved_chunks

# def format_prompt(user_query: str, retrieved_chunks: list) -> str:
#     """Formats retrieved context and user query into an LLM prompt."""
#     context_str = ""
#     for idx, chunk in enumerate(retrieved_chunks, start=1):
#         filename = chunk["metadata"].get("filename", "Unknown")
#         bucket = chunk["metadata"].get("bucket", "Unknown")
#         context_str += f"\n--- Source {idx} (Bucket: {bucket}, File: {filename}) ---\n{chunk['text']}\n"

#     prompt = f"""You are a helpful AI assistant. Answer the user question using ONLY the provided context below. If the answer cannot be found in the context, state that you do not have enough information.

# CONTEXT:
# {context_str}

# QUESTION:
# {user_query}

# ANSWER:"""
#     return prompt

# if __name__ == "__main__":

#     user_query = input("\nEnter your question: ")
    
#     if user_query.strip():
#         chunks = retrieve_context(user_query=user_query, top_k=3)
        
#         print("\n=== RETRIEVED CHUNKS ===")
#         for idx, c in enumerate(chunks, 1):
#             print(f"\nResult {idx} [{c['metadata'].get('bucket')} -> {c['metadata'].get('filename')}]:")
#             print(f"Distance/Score: {c['distance']}")
#             print(f"Content Preview: {c['text'][:150]}...")

#         final_prompt = format_prompt(user_query, chunks)
#         print("\n=== FINAL GENERATED RAG PROMPT ===")
#         print(final_prompt)
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

# def format_prompt(user_query: str, retrieved_chunks: list) -> str:
#     """Creates a user-friendly system prompt requiring clear formatting and sources."""
#     context_str = ""
#     for idx, chunk in enumerate(retrieved_chunks, start=1):
#         filename = chunk["metadata"].get("filename", "Unknown")
#         bucket = chunk["metadata"].get("bucket", "Unknown")
#         context_str += f"\n[Source {idx} - File: {filename} (Bucket: {bucket})]\n{chunk['text']}\n"

#     prompt = f"""You are an intelligent knowledge assistant. 
# Answer the user's question clearly, concisely, and naturally based strictly on the context provided. 
# Use markdown formatting (bullet points, bold text) where appropriate. 
# Do not start your answer with robotic phrases like "Based on the provided text" or "The text states that". 
# Always cite the source filename in parentheses when referencing specific details.

# If the provided context does not contain enough information to answer the question, state:
# "I couldn't find relevant details in your uploaded documents to answer that question."

# CONTEXT:
# {context_str}

# QUESTION:
# {user_query}

# ANSWER:"""
#     return prompt
def format_prompt(user_query: str, retrieved_chunks: list) -> str:
    context_str = ""
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        filename = chunk["metadata"].get("filename", "Unknown")
        bucket = chunk["metadata"].get("bucket", "Unknown")
        context_str += f"\n[Source {idx} - File: {filename} (Bucket: {bucket})]\n{chunk['text']}\n"

    prompt = f"""You are an intelligent document assistant.
Answer the user's question clearly based on the provided context below.

Guidelines:
- Match related terms, synonyms, or merged subcategories (e.g., treat "herbs" as matching "Herbs/Spices", and "beans" as matching "Beans/Legumes" or specific bean varieties like "Kidney/Pinto Beans" or "Green Beans").
- Synthesize facts logically from the text instead of requiring exact word matches.
- Format responses using clear markdown bullet points.
- If the requested topic is truly not mentioned in any form, state that context is missing.

CONTEXT:
{context_str}

QUESTION:
{user_query}

ANSWER:"""
    return prompt
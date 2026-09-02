import time

import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import CrossEncoder

from logging_config import get_logger


logger = get_logger(__name__)


DB_PATH = "./chroma_db"

CANDIDATE_K = 15
FINAL_K = 5
MAX_DISTANCE = 0.70

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"


chroma_client = chromadb.PersistentClient(path=DB_PATH)

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="document_buckets",
    embedding_function=embedding_func
)

reranker = CrossEncoder(RERANKER_MODEL)


def retrieve_context(
    user_query: str,
    top_k: int = CANDIDATE_K,
    max_distance: float = MAX_DISTANCE
) -> list:

    retrieval_start = time.perf_counter()

    try:
        results = collection.query(
            query_texts=[user_query],
            n_results=top_k
        )

        candidates = []
        total_retrieved = 0

        if results and results["documents"]:

            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            total_retrieved = len(docs)

            for idx, doc in enumerate(docs):

                dist = distances[idx]
                meta = metas[idx]

                if dist <= max_distance:
                    candidates.append({
                        "text": doc,
                        "metadata": meta,
                        "distance": dist
                    })

        retrieval_time = (
            time.perf_counter() - retrieval_start
        )

        logger.info(
            f"retrieval_finished | latency_sec={retrieval_time:.3f}",
            extra={
                "details": {
                    "query": user_query,
                    "chunks_requested": top_k,
                    "chunks_retrieved": total_retrieved,
                    "chunks_accepted": len(candidates),
                    "latency_sec": round(
                        retrieval_time,
                        3
                    )
                }
            }
        )

        if not candidates:
            return []

        # Reranking
        reranking_start = time.perf_counter()

        pairs = [
            [user_query, chunk["text"]]
            for chunk in candidates
        ]

        scores = reranker.predict(pairs)

        for chunk, score in zip(candidates, scores):
            chunk["rerank_score"] = float(score)

        candidates.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        reranked_chunks = candidates[:FINAL_K]

        reranking_time = (
            time.perf_counter() - reranking_start
        )

        logger.info(
            f"reranking_finished | latency_sec={reranking_time:.3f}",
            extra={
                "details": {
                    "query": user_query,
                    "candidates": len(candidates),
                    "selected_chunks": len(reranked_chunks),
                    "latency_sec": round(
                        reranking_time,
                        3
                    ),
                    "model": RERANKER_MODEL
                }
            }
        )

        return reranked_chunks

    except Exception as e:

        logger.exception(
            "retrieval_failed",
            extra={
                "details": {
                    "query": user_query,
                    "error": str(e),
                    "latency_sec": round(
                        time.perf_counter() - retrieval_start,
                        3
                    )
                }
            }
        )

        raise


def format_prompt(
    user_query: str,
    retrieved_chunks: list
) -> str:

    context_parts = []

    for idx, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        filename = chunk["metadata"].get(
            "filename",
            "Unknown"
        )

        bucket = chunk["metadata"].get(
            "bucket",
            "Unknown"
        )

        context_parts.append(
            f"\n[Source {idx} - File: {filename} "
            f"(Bucket: {bucket})]\n"
            f"{chunk['text']}\n"
        )

    context_str = "".join(context_parts)

    prompt = f"""You are an intelligent document assistant.
Answer the user's question clearly based on the provided context below.

Guidelines:
- Match related terms, synonyms,singular and plurals, or merged subcategories (e.g., treat "herbs" as matching "Herbs/Spices", and "beans" as matching "Beans/Legumes" or specific bean varieties like "Kidney/Pinto Beans" or "Green Beans").
- Synthesize facts logically from the text instead of requiring exact word matches.
- Format responses using clear markdown bullet points.
- If the requested topic is truly not mentioned in any form, state that context is missing.
# =====================================================================================================
# - When the answer is explicitly available in the context, use the information as stated in the source.
# - Do not rename, merge, reorder, or replace stages, categories, numbers, or terminology from the source.
# - For lists, workflows, steps, guidelines, and sequences, preserve the original order and wording as closely as possible.
# - Do not add information that is not explicitly supported by the context.
# - Only synthesize information when the answer cannot be directly extracted from a single or combined source.

CONTEXT:
{context_str}

QUESTION:
{user_query}

ANSWER:"""

    return prompt












# =================================AFTER RE_RANKING ( chunks testing purpose )==============================
# import time

# from annotated_types import doc
# import chromadb
# from chromadb.utils import embedding_functions
# from sentence_transformers import CrossEncoder

# from logging_config import get_logger


# logger = get_logger(__name__)


# DB_PATH = "./chroma_db"

# CANDIDATE_K = 15
# FINAL_K = 5
# MAX_DISTANCE = 0.70

# RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"


# chroma_client = chromadb.PersistentClient(path=DB_PATH)

# embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
#     model_name="all-MiniLM-L6-v2"
# )

# collection = chroma_client.get_or_create_collection(
#     name="document_buckets",
#     embedding_function=embedding_func
# )


# reranker = CrossEncoder(RERANKER_MODEL)


# def retrieve_context(
#     user_query: str,
#     top_k: int = CANDIDATE_K,
#     max_distance: float = MAX_DISTANCE
# ) -> list:

#     retrieval_start = time.perf_counter()

#     try:
#         results = collection.query(
#             query_texts=[user_query],
#             n_results=top_k
#         )

#         candidates = []

#         total_retrieved = 0

#         if results and results["documents"]:

#             docs = results["documents"][0]
#             metas = results["metadatas"][0]
#             distances = results["distances"][0]

#             total_retrieved = len(docs)

#             for idx, doc in enumerate(docs):

#                 dist = distances[idx]
#                 meta = metas[idx]

#                 print(f"\nResult {idx + 1}")
#                 print("Distance:", dist)
#                 print("File:", meta.get("filename"))
#                 print("Bucket:", meta.get("bucket"))
#                 print("Text:", doc[:300])

#                 logger.debug(
#                     "retrieved_chunk",
#                     extra={
#                         "details": {
#                             "rank": idx + 1,
#                             "filename": meta.get("filename"),
#                             "bucket": meta.get("bucket"),
#                             "distance": dist,
#                             "text_preview": doc[:300]
#                         }
#                     }
#                 )

#                 if dist <= max_distance:
#                     candidates.append({
#                         "text": doc,
#                         "metadata": meta,
#                         "distance": dist
#                     })

#         retrieval_time = (
#             time.perf_counter() - retrieval_start
#         )

#         logger.info(
#             "retrieval_finished",
#             extra={
#                 "details": {
#                     "query": user_query,
#                     "chunks_requested": top_k,
#                     "chunks_retrieved": total_retrieved,
#                     "chunks_accepted": len(candidates),
#                     "latency_sec": round(
#                         retrieval_time,
#                         3
#                     )
#                 }
#             }
#         )

#         if not candidates:
#             return []

#         # ---------------- RERANKING ----------------

#         reranking_start = time.perf_counter()

#         pairs = [
#             [user_query, chunk["text"]]
#             for chunk in candidates
#         ]

#         scores = reranker.predict(pairs)

#         for chunk, score in zip(candidates, scores):
#             chunk["rerank_score"] = float(score)

#         candidates.sort(
#             key=lambda x: x["rerank_score"],
#             reverse=True
#         )

#         reranked_chunks = candidates[:FINAL_K]
#         print("\n========== RERANKED RESULTS ==========")

#         for idx, chunk in enumerate(reranked_chunks, start=1):
#             print(f"\nReranked Result {idx}")
#             print("Score:", chunk["rerank_score"])
#             print("File:", chunk["metadata"].get("filename"))
#             print("Bucket:", chunk["metadata"].get("bucket"))
#             print("Text:", chunk["text"])

#         print("======================================\n")
        

#         reranking_time = (
#             time.perf_counter() - reranking_start
#         )

#         logger.info(
#             "reranking_finished",
#             extra={
#                 "details": {
#                     "query": user_query,
#                     "candidates": len(candidates),
#                     "selected_chunks": len(reranked_chunks),
#                     "latency_sec": round(
#                         reranking_time,
#                         3
#                     ),
#                     "model": RERANKER_MODEL
#                 }
#             }
#         )

#         return reranked_chunks

#     except Exception as e:

#         logger.exception(
#             "retrieval_failed",
#             extra={
#                 "details": {
#                     "query": user_query,
#                     "error": str(e)
#                 }
#             }
#         )

#         raise


# def format_prompt(
#     user_query: str,
#     retrieved_chunks: list
# ) -> str:

#     context_parts = []

#     for idx, chunk in enumerate(
#         retrieved_chunks,
#         start=1
#     ):

#         filename = chunk["metadata"].get(
#             "filename",
#             "Unknown"
#         )

#         bucket = chunk["metadata"].get(
#             "bucket",
#             "Unknown"
#         )

#         context_parts.append(
#             f"\n[Source {idx} - File: {filename} "
#             f"(Bucket: {bucket})]\n"
#             f"{chunk['text']}\n"
#         )

#     context_str = "".join(context_parts)

#     prompt = f"""You are an intelligent document assistant.
# Answer the user's question clearly based on the provided context below.

# Guidelines:
# - Match related terms, synonyms,singular and plurals, or merged subcategories (e.g., treat "herbs" as matching "Herbs/Spices", and "beans" as matching "Beans/Legumes" or specific bean varieties like "Kidney/Pinto Beans" or "Green Beans").
# - Synthesize facts logically from the text instead of requiring exact word matches.
# - Format responses using clear markdown bullet points.
# - If the requested topic is truly not mentioned in any form, state that context is missing.

# CONTEXT:
# {context_str}

# QUESTION:
# {user_query}

# ANSWER:"""

#     return prompt
# =========================================================BEFORE RE_RANKING==============================================================================
#  import time

# import chromadb
# from chromadb.utils import embedding_functions

# from logging_config import get_logger


# logger = get_logger(__name__)

# DB_PATH = "./chroma_db"

# chroma_client = chromadb.PersistentClient(path=DB_PATH)

# embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
#     model_name="all-MiniLM-L6-v2"
# )

# collection = chroma_client.get_or_create_collection(
#     name="document_buckets",
#     embedding_function=embedding_func
# )


# def retrieve_context(
#     user_query: str,
#     top_k: int = 5,
#     max_distance: float = 0.50
# ) -> list:

#     start_time = time.perf_counter()

#     try:
#         results = collection.query(
#             query_texts=[user_query],
#             n_results=top_k
#         )

#         retrieved_chunks = []

#         total_retrieved = 0

#         if results and results["documents"]:
#             docs = results["documents"][0]
#             metas = results["metadatas"][0]
#             distances = results["distances"][0]

#             total_retrieved = len(docs)

#             for idx, doc in enumerate(docs):
#                 dist = distances[idx]
#                 meta = metas[idx]

#                 logger.debug(
#                     "retrieved_chunk",
#                     extra={
#                         "details": {
#                             "rank": idx + 1,
#                             "filename": meta.get("filename"),
#                             "bucket": meta.get("bucket"),
#                             "distance": dist,
#                             "text_preview": doc[:300]
#                         }
#                     }
#                 )

#                 if dist <= max_distance:
#                     retrieved_chunks.append({
#                         "text": doc,
#                         "metadata": meta,
#                         "distance": dist
#                     })

#         retrieval_time = time.perf_counter() - start_time

#         logger.info(
#             "retrieval_completed",
#             extra={
#                 "details": {
#                     "query": user_query,
#                     "chunks_requested": top_k,
#                     "chunks_retrieved": total_retrieved,
#                     "chunks_accepted": len(retrieved_chunks),
#                     "latency_sec": round(
#                         retrieval_time,
#                         3
#                     )
#                 }
#             }
#         )

#         return retrieved_chunks

#     except Exception as e:
#         logger.exception(
#             "retrieval_failed",
#             extra={
#                 "details": {
#                     "query": user_query,
#                     "error": str(e),
#                     "latency_sec": round(
#                         time.perf_counter() - start_time,
#                         3
#                     )
#                 }
#             }
#         )

#         raise


# def format_prompt(
#     user_query: str,
#     retrieved_chunks: list
# ) -> str:

#     context_parts = []

#     for idx, chunk in enumerate(
#         retrieved_chunks,
#         start=1
#     ):
#         filename = chunk["metadata"].get(
#             "filename",
#             "Unknown"
#         )

#         bucket = chunk["metadata"].get(
#             "bucket",
#             "Unknown"
#         )

#         context_parts.append(
#             f"\n[Source {idx} - File: {filename} "
#             f"(Bucket: {bucket})]\n"
#             f"{chunk['text']}\n"
#         )

#     context_str = "".join(context_parts)

#     prompt = f"""You are an intelligent document assistant.
# Answer the user's question clearly based on the provided context below.

# Guidelines:
# - Match related terms, synonyms,singular and plurals, or merged subcategories (e.g., treat "herbs" as matching "Herbs/Spices", and "beans" as matching "Beans/Legumes" or specific bean varieties like "Kidney/Pinto Beans" or "Green Beans").
# - Synthesize facts logically from the text instead of requiring exact word matches.
# - Format responses using clear markdown bullet points.
# - If the requested topic is truly not mentioned in any form, state that context is missing.

# CONTEXT:
# {context_str}

# QUESTION:
# {user_query}

# ANSWER:"""

#     return prompt

# ======================================================================
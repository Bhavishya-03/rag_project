# import os
# import time

# import chromadb
# from chromadb.utils import embedding_functions

# from parser import parse_document
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


# def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
#     chunks = []
#     start = 0

#     while start < len(text):
#         end = start + chunk_size
#         chunk = text[start:end]

#         if chunk.strip():
#             chunks.append(chunk.strip())

#         start += chunk_size - overlap

#     return chunks


# def sync_deleted_files(bucket_name: str, folder_path: str):
#     if not os.path.exists(folder_path):
#         return

#     disk_files = {
#         f for f in os.listdir(folder_path)
#         if not f.startswith(".")
#     }

#     db_records = collection.get(
#         where={"bucket": bucket_name}
#     )

#     if db_records and db_records["metadatas"]:
#         db_files = {
#             metadata["filename"]
#             for metadata in db_records["metadatas"]
#         }

#         deleted_files = db_files - disk_files

#         for file_to_remove in deleted_files:
#             collection.delete(
#                 where={
#                     "$and": [
#                         {"filename": {"$eq": file_to_remove}},
#                         {"bucket": {"$eq": bucket_name}}
#                     ]
#                 }
#             )

#             logger.info(
#                 "file_deleted",
#                 extra={
#                     "details": {
#                         "bucket": bucket_name,
#                         "filename": file_to_remove
#                     }
#                 }
#             )


# def process_bucket(bucket_name: str, folder_path: str):
#     if not os.path.exists(folder_path):
#         logger.warning(
#             "bucket_not_found",
#             extra={
#                 "details": {
#                     "bucket": bucket_name,
#                     "path": folder_path
#                 }
#             }
#         )
#         return

#     bucket_start = time.perf_counter()

#     logger.info(
#         "ingestion_started",
#         extra={
#             "details": {
#                 "bucket": bucket_name
#             }
#         }
#     )

#     sync_deleted_files(bucket_name, folder_path)

#     files = [
#         f for f in os.listdir(folder_path)
#         if not f.startswith(".")
#     ]

#     files_processed = 0
#     files_skipped = 0
#     files_failed = 0
#     total_chunks = 0
#     chunking_time = 0.0
#     embedding_time = 0.0

#     for file in files:

#         existing_records = collection.get(
#             where={
#                 "$and": [
#                     {"filename": {"$eq": file}},
#                     {"bucket": {"$eq": bucket_name}}
#                 ]
#             },
#             limit=1
#         )

#         if existing_records and existing_records["ids"]:
#             files_skipped += 1

#             logger.info(
#                 "file_skipped",
#                 extra={
#                     "details": {
#                         "bucket": bucket_name,
#                         "filename": file,
#                         "reason": "already_indexed"
#                     }
#                 }
#             )
#             continue

#         file_path = os.path.join(folder_path, file)

#         try:
#             extracted_text = parse_document(file_path)

#             if not extracted_text:
#                 files_skipped += 1

#                 logger.warning(
#                     "file_skipped",
#                     extra={
#                         "details": {
#                             "bucket": bucket_name,
#                             "filename": file,
#                             "reason": "empty_or_unparseable"
#                         }
#                     }
#                 )
#                 continue

#             chunk_start = time.perf_counter()

#             chunks = chunk_text(extracted_text)

#             chunking_time += time.perf_counter() - chunk_start

#             documents = []
#             metadatas = []
#             ids = []

#             for idx, chunk in enumerate(chunks):
#                 documents.append(chunk)

#                 metadatas.append({
#                     "bucket": bucket_name,
#                     "filename": file
#                 })

#                 ids.append(
#                     f"{bucket_name}_{file}_{idx}"
#                 )

#             if not documents:
#                 continue

#             embedding_start = time.perf_counter()

#             collection.add(
#                 documents=documents,
#                 metadatas=metadatas,
#                 ids=ids
#             )

#             embedding_time += time.perf_counter() - embedding_start

#             files_processed += 1
#             total_chunks += len(chunks)

#             logger.info(
#                 "file_indexed",
#                 extra={
#                     "details": {
#                         "bucket": bucket_name,
#                         "filename": file,
#                         "chunks_created": len(chunks)
#                     }
#                 }
#             )

#         except Exception as e:
#             files_failed += 1

#             logger.exception(
#                 "file_processing_failed",
#                 extra={
#                     "details": {
#                         "bucket": bucket_name,
#                         "filename": file,
#                         "error": str(e)
#                     }
#                 }
#             )

#     bucket_time = time.perf_counter() - bucket_start

#     logger.info(
#         "bucket_completed",
#         extra={
#             "details": {
#                 "bucket": bucket_name,
#                 "files_processed": files_processed,
#                 "files_skipped": files_skipped,
#                 "files_failed": files_failed,
#                 "chunks_created": total_chunks,
#                 "chunking_duration_seconds": round(
#                     chunking_time, 3
#                 ),
#                 "embedding_duration_seconds": round(
#                     embedding_time, 3
#                 ),
#                 "duration_seconds": round(
#                     bucket_time, 3
#                 )
#             }
#         }
#     )


# if __name__ == "__main__":
#     ingestion_start = time.perf_counter()

#     process_bucket(
#         "bucket_1",
#         "data/bucket_1"
#     )

#     process_bucket(
#         "bucket_2",
#         "data/bucket_2"
#     )

#     logger.info(
#         "ingestion_completed",
#         extra={
#             "details": {
#                 "duration_seconds": round(
#                     time.perf_counter() - ingestion_start,
#                     3
#                 )
#             }
#         }
#     )
import os
import time

import chromadb
from chromadb.utils import embedding_functions

from parser import parse_document
from logging_config import get_logger


logger = get_logger(__name__)

DB_PATH = "./chroma_db"

chroma_client = chromadb.PersistentClient(path=DB_PATH)

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="document_buckets",
    embedding_function=embedding_func
)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


def sync_deleted_files(bucket_name: str, folder_path: str):
    if not os.path.exists(folder_path):
        return

    disk_files = {
        f for f in os.listdir(folder_path)
        if not f.startswith(".")
    }

    db_records = collection.get(
        where={"bucket": bucket_name}
    )

    if db_records and db_records["metadatas"]:
        db_files = {
            metadata["filename"]
            for metadata in db_records["metadatas"]
        }

        deleted_files = db_files - disk_files

        for file_to_remove in deleted_files:
            collection.delete(
                where={
                    "$and": [
                        {"filename": {"$eq": file_to_remove}},
                        {"bucket": {"$eq": bucket_name}}
                    ]
                }
            )

            logger.info(
                f"file_deleted | {file_to_remove}",
                extra={
                    "details": {
                        "bucket": bucket_name,
                        "filename": file_to_remove
                    }
                }
            )


def process_bucket(bucket_name: str, folder_path: str):
    if not os.path.exists(folder_path):
        logger.warning(
            "bucket_not_found",
            extra={
                "details": {
                    "bucket": bucket_name,
                    "path": folder_path
                }
            }
        )
        return

    bucket_start = time.perf_counter()

    logger.info(
        "ingestion_started",
        extra={
            "details": {
                "bucket": bucket_name
            }
        }
    )

    sync_deleted_files(bucket_name, folder_path)

    files = [
        f for f in os.listdir(folder_path)
        if not f.startswith(".")
    ]

    files_processed = 0
    files_skipped = 0
    files_failed = 0
    total_chunks = 0
    chunking_time = 0.0
    embedding_time = 0.0

    for file in files:

        existing_records = collection.get(
            where={
                "$and": [
                    {"filename": {"$eq": file}},
                    {"bucket": {"$eq": bucket_name}}
                ]
            },
            limit=1
        )

        if existing_records and existing_records["ids"]:
            files_skipped += 1

            logger.info(
                f"file_skipped | {file}",
                extra={
                    "details": {
                        "bucket": bucket_name,
                        "filename": file
                    }
                }
            )
            continue

        file_path = os.path.join(folder_path, file)

        try:
            extracted_text = parse_document(file_path)

            if not extracted_text:
                files_skipped += 1

                logger.warning(
                    f"file_skipped | {file}",
                    extra={
                        "details": {
                            "bucket": bucket_name,
                            "filename": file
                        }
                    }
                )
                continue

            chunk_start = time.perf_counter()

            chunks = chunk_text(extracted_text)

            chunking_time += time.perf_counter() - chunk_start

            documents = []
            metadatas = []
            ids = []

            for idx, chunk in enumerate(chunks):
                documents.append(chunk)

                metadatas.append({
                    "bucket": bucket_name,
                    "filename": file
                })

                ids.append(
                    f"{bucket_name}_{file}_{idx}"
                )

            if not documents:
                continue

            embedding_start = time.perf_counter()

            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            embedding_time += time.perf_counter() - embedding_start

            files_processed += 1
            total_chunks += len(chunks)

            logger.info(
                f"file_indexed | {file}",
                extra={
                    "details": {
                        "bucket": bucket_name,
                        "filename": file,
                        "chunks_created": len(chunks)
                    }
                }
            )

        except Exception as e:
            files_failed += 1

            logger.exception(
                f"file_processing_failed | {file}",
                extra={
                    "details": {
                        "bucket": bucket_name,
                        "filename": file,
                        "error": str(e)
                    }
                }
            )

    bucket_time = time.perf_counter() - bucket_start

    logger.info(
        "bucket_completed",
        extra={
            "details": {
                "bucket": bucket_name,
                "files_processed": files_processed,
                "files_skipped": files_skipped,
                "files_failed": files_failed,
                "chunks_created": total_chunks,
                "chunking_duration_seconds": round(
                    chunking_time, 3
                ),
                "embedding_duration_seconds": round(
                    embedding_time, 3
                ),
                "duration_seconds": round(
                    bucket_time, 3
                )
            }
        }
    )


if __name__ == "__main__":
    ingestion_start = time.perf_counter()

    process_bucket(
        "bucket_1",
        "data/bucket_1"
    )

    process_bucket(
        "bucket_2",
        "data/bucket_2"
    )

    logger.info(
        "ingestion_completed",
        extra={
            "details": {
                "duration_seconds": round(
                    time.perf_counter() - ingestion_start,
                    3
                )
            }
        }
    )
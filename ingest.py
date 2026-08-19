# import os
# import chromadb
# from chromadb.utils import embedding_functions
# from parser import parse_document

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
#     """Splits raw extracted text into overlapping chunks."""
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = start + chunk_size
#         chunk = text[start:end]
#         if chunk.strip():
#             chunks.append(chunk.strip())
#         start += chunk_size - overlap
#     return chunks

# def process_bucket(bucket_name: str, folder_path: str):
#     """Processes only newly added files in a bucket folder."""
#     if not os.path.exists(folder_path):
#         print(f"Directory '{folder_path}' not found. Skipping...")
#         return

#     files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
#     print(f"\n--- Checking {len(files)} file(s) in '{bucket_name}' ---")

#     for file in files:
#         # 1. Verification Check: Ask ChromaDB if this file is already indexed
#         existing_records = collection.get(
#             where={
#                 "$and": [
#                     {"filename": {"$eq": file}},
#                     {"bucket": {"$eq": bucket_name}}
#                 ]
#             },
#             limit=1
#         )
        
#         # If ChromaDB returns results, skip parsing entirely
#         if existing_records and existing_records["ids"]:
#             print(f"  [Skipped] '{file}' is already indexed.")
#             continue

#         # 2. Parse only NEW files
#         file_path = os.path.join(folder_path, file)
#         extracted_text = parse_document(file_path)
        
#         if not extracted_text:
#             print(f"  [Skipped] Empty or unparseable file: {file}")
#             continue

#         # 3. Chunk and add to ChromaDB
#         chunks = chunk_text(extracted_text)
#         documents = []
#         metadatas = []
#         ids = []

#         for idx, chunk in enumerate(chunks):
#             documents.append(chunk)
#             metadatas.append({
#                 "bucket": bucket_name,
#                 "filename": file
#             })
#             ids.append(f"{bucket_name}_{file}_{idx}")

#         if documents:
#             collection.add(
#                 documents=documents,
#                 metadatas=metadatas,
#                 ids=ids
#             )
#             print(f"  [Indexed New File] '{file}' -> {len(chunks)} chunks")

# if __name__ == "__main__":
#     process_bucket("bucket_1", "data/bucket_1")
#     process_bucket("bucket_2", "data/bucket_2")
#     print("\nIngestion Complete! Vector database up to date at './chroma_db'")
import os
import chromadb
from chromadb.utils import embedding_functions
from parser import parse_document

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
    """Splits raw extracted text into overlapping chunks."""
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
    """Deletes entries from ChromaDB if the file no longer exists in disk storage."""
    if not os.path.exists(folder_path):
        return

    # Files currently in disk
    disk_files = set(f for f in os.listdir(folder_path) if not f.startswith('.'))

    # Fetch all metadata currently indexed for this bucket
    db_records = collection.get(where={"bucket": bucket_name})
    
    if db_records and db_records["metadatas"]:
        db_files = set(m["filename"] for m in db_records["metadatas"])
        
        # Identify missing files
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
            print(f"  [Deleted from Vector DB] '{file_to_remove}' no longer exists on disk.")

def process_bucket(bucket_name: str, folder_path: str):
    """Processes only newly added files in a bucket folder and removes deleted ones."""
    if not os.path.exists(folder_path):
        print(f"Directory '{folder_path}' not found. Skipping...")
        return

    # 1. Sync deletions first
    sync_deleted_files(bucket_name, folder_path)

    files = [f for f in os.listdir(folder_path) if not f.startswith('.')]
    print(f"\n--- Checking {len(files)} file(s) in '{bucket_name}' ---")

    for file in files:
        # 2. Verification Check: Ask ChromaDB if this file is already indexed
        existing_records = collection.get(
            where={
                "$and": [
                    {"filename": {"$eq": file}},
                    {"bucket": {"$eq": bucket_name}}
                ]
            },
            limit=1
        )
        
        # If ChromaDB returns results, skip parsing entirely
        if existing_records and existing_records["ids"]:
            print(f"  [Skipped] '{file}' is already indexed.")
            continue

        # 3. Parse only NEW files
        file_path = os.path.join(folder_path, file)
        extracted_text = parse_document(file_path)
        
        if not extracted_text:
            print(f"  [Skipped] Empty or unparseable file: {file}")
            continue

        # 4. Chunk and add to ChromaDB
        chunks = chunk_text(extracted_text)
        documents = []
        metadatas = []
        ids = []

        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "bucket": bucket_name,
                "filename": file
            })
            ids.append(f"{bucket_name}_{file}_{idx}")

        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"  [Indexed New File] '{file}' -> {len(chunks)} chunks")

if __name__ == "__main__":
    process_bucket("bucket_1", "data/bucket_1")
    process_bucket("bucket_2", "data/bucket_2")
    print("\nIngestion Complete! Vector database up to date at './chroma_db'")
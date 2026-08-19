import chromadb
from collections import Counter

DB_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_collection(name="document_buckets")

total_chunks = collection.count()
print(f"Total Chunks Stored in DB: {total_chunks}")

# Fetch metadata for ALL chunks (no limit)
data = collection.get(include=["metadatas"])
metadatas = data["metadatas"]

# Count chunks per file
file_counts = Counter((m["bucket"], m["filename"]) for m in metadatas)

print("\n=== INDEXED FILES & CHUNK BREAKDOWN ===")
for (bucket, filename), count in sorted(file_counts.items()):
    print(f" - [{bucket}] {filename:<20} -> {count} chunks")
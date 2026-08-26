import ollama
from query import retrieve_context, format_prompt

MODEL_NAME = "gemma"

def ask_rag(user_query: str) -> dict:
    try:
        clean_query = user_query.replace("_", " ").strip()
        chunks = retrieve_context(user_query=clean_query, top_k=5, max_distance=0.70)
        
        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in your uploaded documents for that query.",
                "sources": {}
            }

        sources_by_bucket = {}
        for c in chunks:
            metadata = c.get('metadata', {})
            bucket = metadata.get('bucket', 'General')
            filename = metadata.get('filename', 'Unknown')
            
            if bucket not in sources_by_bucket:
                sources_by_bucket[bucket] = set()
            sources_by_bucket[bucket].add(filename)

        sources_by_bucket = {b: list(files) for b, files in sources_by_bucket.items()}
        prompt = format_prompt(user_query, chunks)

        response = ollama.generate(model=MODEL_NAME, prompt=prompt)
        return {
            "answer": response['response'],
            "sources": sources_by_bucket
        }
    except Exception as e:
        return {
            "answer": f"Error generating response: {e}",
            "sources": {}
        }

if __name__ == "__main__":
    print("=" * 50)
    print("         💬 Local Document Assistant")
    print("=" * 50)
    
    while True:
        query = input("\n🔍 Ask a question ('exit' to quit): ")
        if query.lower().strip() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
            
        if not query.strip():
            continue

        ask_rag(query)
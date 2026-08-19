# import ollama
# from query import retrieve_context, format_prompt

# MODEL_NAME = "gemma" 
# def generate_answer(prompt: str) -> str:
#     """Sends the assembled prompt to the local Ollama LLM."""
#     try:
#         response = ollama.generate(
#             model=MODEL_NAME,
#             prompt=prompt
#         )
#         return response['response']
#     except Exception as e:
#         return f"Error communicating with Ollama: {e}"

# def ask_rag(user_query: str):
#     """Executes the complete Retrieval-Augmented Generation flow."""
#     print(f"\n[1] Retrieving relevant context from ChromaDB...")

#     chunks = retrieve_context(user_query=user_query, top_k=3, max_distance=0.55)
    
#     if not chunks:
#         print("  [Warning] No relevant documents found matching your question.")
#         return "I don't have enough context in the stored files to answer that question."

#     print(f"  -> Retrived {len(chunks)} relevant chunk(s).")

#     prompt = format_prompt(user_query, chunks)

#     print(f"[2] Generating answer using local model '{MODEL_NAME}'...")
#     answer = generate_answer(prompt)
    
#     return answer

# if __name__ == "__main__":
#     print("==========================================")
#     print("      Local RAG Pipeline Ready!           ")
#     print("==========================================")
    
#     while True:
#         query = input("\nAsk a question (or type 'exit' to quit): ")
#         if query.lower().strip() in ['exit', 'quit', 'q']:
#             break
            
#         if not query.strip():
#             continue

#         answer = ask_rag(query)
#         print("\n=== RESPONSE ===")
#         print(answer)
import sys
import ollama
from query import retrieve_context, format_prompt

MODEL_NAME = "gemma"

def ask_rag(user_query: str):
    # Fetch top 3 matching chunks with updated 0.65 distance limit
    # chunks = retrieve_context(user_query=user_query, top_k=3, max_distance=0.65)
    chunks = retrieve_context(user_query=user_query, top_k=5, max_distance=0.70)
    
    if not chunks:
        print("\n🤖 Assistant:\nI couldn't find any relevant information in your uploaded documents for that query.")
        return

    # Extract distinct source filenames retrieved
    sources = set(c['metadata'].get('filename', 'Unknown') for c in chunks)
    prompt = format_prompt(user_query, chunks)

    print("\n🤖 Assistant:")
    try:
        # Stream response tokens live to terminal
        stream = ollama.generate(model=MODEL_NAME, prompt=prompt, stream=True)
        for chunk in stream:
            sys.stdout.write(chunk['response'])
            sys.stdout.flush()
        
        # Display source references at the bottom
        print("\n\n" + "-" * 40)
        print("📌 Sources Used: " + ", ".join(sources))
        print("-" * 40)
    except Exception as e:
        print(f"\nError generating response: {e}")

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
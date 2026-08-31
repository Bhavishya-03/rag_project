import os
import time

from dotenv import load_dotenv
from groq import Groq

from logging_config import get_logger
from query import retrieve_context, format_prompt


load_dotenv()

logger = get_logger(__name__)

MODEL_NAME = "openai/gpt-oss-20b"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured. "
        "Please add it to the .env file."
    )

groq_client = Groq(api_key=GROQ_API_KEY)


def ask_rag(user_query: str) -> dict:
    total_start = time.perf_counter()

    clean_query = user_query.replace("_", " ").strip()

    logger.info(
        "rag_started",
        extra={
            "details": {
                "query": clean_query
            }
        }
    )

    try:
        chunks = retrieve_context(
            user_query=clean_query
        )

        if not chunks:
            logger.warning(
                "no_relevant_chunks",
                extra={
                    "details": {
                        "query": clean_query
                    }
                }
            )

            return {
                "answer": (
                    "I couldn't find any relevant information "
                    "in your uploaded documents for that query."
                ),
                "sources": {}
            }

        sources_by_bucket = {}

        for chunk in chunks:
            metadata = chunk.get("metadata", {})

            bucket = metadata.get(
                "bucket",
                "General"
            )

            filename = metadata.get(
                "filename",
                "Unknown"
            )

            if bucket not in sources_by_bucket:
                sources_by_bucket[bucket] = set()

            sources_by_bucket[bucket].add(filename)

        sources_by_bucket = {
            bucket: list(files)
            for bucket, files in sources_by_bucket.items()
        }

        prompt = format_prompt(
            user_query,
            chunks
        )

        generation_start = time.perf_counter()

        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            reasoning_effort="low",
            include_reasoning=False,
            max_completion_tokens=300,
            temperature=0.1
        )

        generation_time = (
            time.perf_counter() - generation_start
        )

        usage = response.usage

        generation_details = {
            "query": clean_query,
            "model": MODEL_NAME,
            "latency_sec": round(
                generation_time,
                3
            )
        }

        if usage:
            generation_details.update({
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            })

        logger.info(
            f"generation_completed | latency_sec={generation_time:.3f}",
            extra={
                "details": generation_details
            }
        )

        total_time = (
            time.perf_counter() - total_start
        )

        logger.info(
            f"rag_completed | latency_sec={total_time:.3f}",
            extra={
                "details": {
                    "query": clean_query,
                    "latency_sec": round(
                        total_time,
                        3
                    )
                }
            }
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "sources": sources_by_bucket
        }

    except Exception as e:

        logger.exception(
            "rag_failed",
            extra={
                "details": {
                    "query": clean_query,
                    "error": str(e),
                    "latency_sec": round(
                        time.perf_counter() - total_start,
                        3
                    )
                }
            }
        )

        return {
            "answer": f"Error generating response: {e}",
            "sources": {}
        }


if __name__ == "__main__":
    print("=" * 50)
    print("         💬 Local Document Assistant")
    print("=" * 50)

    while True:
        query = input(
            "\n🔍 Ask a question ('exit' to quit): "
        )

        if query.lower().strip() in [
            "exit",
            "quit",
            "q"
        ]:
            print("Goodbye!")
            break

        if not query.strip():
            continue

        ask_rag(query)
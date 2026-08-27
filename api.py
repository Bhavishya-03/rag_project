from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import os
import time

from logging_config import get_logger
from main import ask_rag
from parser import parse_document


logger = get_logger(__name__)


app = FastAPI(
    title="🥗 Nutri-Query RAG API",
    description="REST API for querying nutrition documents, PDFs, and images with automatic Swagger documentation.",
    version="1.0.0"
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: Dict[str, List[str]]


class ParseTestRequest(BaseModel):
    file_path: str


@app.get("/", summary="Health Check")
def health_check():
    """Verify that the API server is running."""
    return {
        "status": "healthy",
        "message": "Nutri-Query API is up and running."
    }


@app.post(
    "/ask",
    response_model=QueryResponse,
    summary="Query RAG Pipeline"
)
def query_rag_endpoint(request: QueryRequest):
    """
    Send a question to the RAG pipeline.
    Returns the generated answer along with retrieved sources grouped by bucket.
    """
    start_time = time.perf_counter()

    if not request.query.strip():
        logger.warning(
            "invalid_query",
            extra={
                "details": {
                    "reason": "empty_query"
                }
            }
        )

        raise HTTPException(
            status_code=400,
            detail="Query string cannot be empty."
        )

    logger.info(
        "api_request_started",
        extra={
            "details": {
                "endpoint": "/ask",
                "query": request.query.strip()
            }
        }
    )

    try:
        result = ask_rag(request.query)

        logger.info(
            "api_request_completed",
            extra={
                "details": {
                    "endpoint": "/ask",
                    "latency_sec": round(
                        time.perf_counter() - start_time,
                        3
                    )
                }
            }
        )

        return result

    except Exception as e:
        logger.exception(
            "api_request_failed",
            extra={
                "details": {
                    "endpoint": "/ask",
                    "query": request.query.strip(),
                    "error": str(e),
                    "latency_sec": round(
                        time.perf_counter() - start_time,
                        3
                    )
                }
            }
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process the query."
        )


@app.post(
    "/parse-test",
    summary="Test Document Parser"
)
def parse_test_endpoint(request: ParseTestRequest):
    """
    Test image OCR or PDF text extraction on a specific file path.
    """
    start_time = time.perf_counter()

    if not os.path.exists(request.file_path):
        logger.warning(
            "file_not_found",
            extra={
                "details": {
                    "endpoint": "/parse-test",
                    "filename": os.path.basename(request.file_path)
                }
            }
        )

        raise HTTPException(
            status_code=404,
            detail="File not found at specified path."
        )

    try:
        extracted_text = parse_document(
            request.file_path
        )

        logger.info(
            "parse_test_completed",
            extra={
                "details": {
                    "filename": os.path.basename(request.file_path),
                    "characters_extracted": len(extracted_text),
                    "latency_sec": round(
                        time.perf_counter() - start_time,
                        3
                    )
                }
            }
        )

        return {
            "file_path": request.file_path,
            "extracted_character_count": len(extracted_text),
            "text_preview": extracted_text[:500]
        }

    except Exception as e:
        logger.exception(
            "parse_test_failed",
            extra={
                "details": {
                    "filename": os.path.basename(request.file_path),
                    "error": str(e),
                    "latency_sec": round(
                        time.perf_counter() - start_time,
                        3
                    )
                }
            }
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to parse the document."
        )
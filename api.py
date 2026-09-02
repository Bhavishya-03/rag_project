# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Dict, List
# import os
# import time

# from logging_config import get_logger
# from main import ask_rag
# from parser import parse_document


# logger = get_logger(__name__)


# app = FastAPI(
#     title="🥗 Nutri-Query RAG API",
#     description=(
#         "REST API for querying nutrition documents, PDFs, "
#         "and images with automatic Swagger documentation."
#     ),
#     version="1.0.0"
# )


# class QueryRequest(BaseModel):
#     query: str


# class QueryResponse(BaseModel):
#     answer: str
#     sources: Dict[str, List[str]]


# class ParseTestRequest(BaseModel):
#     file_path: str


# @app.get("/", summary="Health Check")
# def health_check():
#     """Verify that the API server is running."""

#     return {
#         "status": "healthy",
#         "message": "Nutri-Query API is up and running."
#     }


# @app.post(
#     "/ask",
#     response_model=QueryResponse,
#     summary="Query RAG Pipeline"
# )
# def query_rag_endpoint(request: QueryRequest):

#     start_time = time.perf_counter()

#     query = request.query.strip()

#     if not query:
#         logger.warning(
#             "invalid_query",
#             extra={
#                 "details": {
#                     "endpoint": "/ask",
#                     "reason": "empty_query"
#                 }
#             }
#         )

#         raise HTTPException(
#             status_code=400,
#             detail="Query string cannot be empty."
#         )

#     logger.info(
#         "api_request_started",
#         extra={
#             "details": {
#                 "endpoint": "/ask",
#                 "query": query
#             }
#         }
#     )

#     try:

#         result = ask_rag(query)

#         latency = time.perf_counter() - start_time

#         logger.info(
#             f"api_request_completed | latency_sec={latency:.3f}",
#             extra={
#                 "details": {
#                     "endpoint": "/ask",
#                     "query": query,
#                     "latency_sec": round(
#                         latency,
#                         3
#                     )
#                 }
#             }
#         )

#         return result

#     except Exception as e:

#         latency = time.perf_counter() - start_time

#         logger.exception(
#             "api_request_failed",
#             extra={
#                 "details": {
#                     "endpoint": "/ask",
#                     "query": query,
#                     "error": str(e),
#                     "latency_sec": round(
#                         latency,
#                         3
#                     )
#                 }
#             }
#         )

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to process the query."
#         )


# @app.post(
#     "/parse-test",
#     summary="Test Document Parser"
# )
# def parse_test_endpoint(request: ParseTestRequest):

#     start_time = time.perf_counter()

#     if not os.path.exists(request.file_path):

#         logger.warning(
#             "file_not_found",
#             extra={
#                 "details": {
#                     "endpoint": "/parse-test",
#                     "filename": os.path.basename(
#                         request.file_path
#                     )
#                 }
#             }
#         )

#         raise HTTPException(
#             status_code=404,
#             detail="File not found at specified path."
#         )

#     try:

#         extracted_text = parse_document(
#             request.file_path
#         )

#         latency = time.perf_counter() - start_time

#         logger.info(
#             f"parse_test_completed | latency_sec={latency:.3f}",
#             extra={
#                 "details": {
#                     "endpoint": "/parse-test",
#                     "filename": os.path.basename(
#                         request.file_path
#                     ),
#                     "characters_extracted": len(
#                         extracted_text
#                     ),
#                     "latency_sec": round(
#                         latency,
#                         3
#                     )
#                 }
#             }
#         )

#         return {
#             "file_path": request.file_path,
#             "extracted_character_count": len(
#                 extracted_text
#             ),
#             "text_preview": extracted_text[:500]
#         }

#     except Exception as e:

#         latency = time.perf_counter() - start_time

#         logger.exception(
#             "parse_test_failed",
#             extra={
#                 "details": {
#                     "endpoint": "/parse-test",
#                     "filename": os.path.basename(
#                         request.file_path
#                     ),
#                     "error": str(e),
#                     "latency_sec": round(
#                         latency,
#                         3
#                     )
#                 }
#             }
#         )

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to parse the document."
#         )
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, List
import os
import time
import tempfile

from logging_config import get_logger
from main import ask_rag
from parser import parse_document


logger = get_logger(__name__)


app = FastAPI(
    title="🥗 Nutri-Query RAG API",
    description=(
        "REST API for querying nutrition documents, PDFs, "
        "and images with automatic Swagger documentation."
    ),
    version="1.0.0"
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: Dict[str, List[str]]


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

    start_time = time.perf_counter()

    query = request.query.strip()

    if not query:
        logger.warning(
            "invalid_query",
            extra={
                "details": {
                    "endpoint": "/ask",
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
                "query": query
            }
        }
    )

    try:

        result = ask_rag(query)

        latency = time.perf_counter() - start_time

        logger.info(
            f"api_request_completed | latency_sec={latency:.3f}",
            extra={
                "details": {
                    "endpoint": "/ask",
                    "query": query,
                    "latency_sec": round(
                        latency,
                        3
                    )
                }
            }
        )

        return result

    except Exception as e:

        latency = time.perf_counter() - start_time

        logger.exception(
            "api_request_failed",
            extra={
                "details": {
                    "endpoint": "/ask",
                    "query": query,
                    "error": str(e),
                    "latency_sec": round(
                        latency,
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
async def parse_test_endpoint(
    file: UploadFile = File(...)
):

    start_time = time.perf_counter()

    filename = file.filename or "uploaded_file"

    allowed_extensions = (
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".txt"
    )

    if not filename.lower().endswith(
        allowed_extensions
    ):

        logger.warning(
            f"unsupported_file | {filename}",
            extra={
                "details": {
                    "endpoint": "/parse-test",
                    "filename": filename
                }
            }
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed types: PDF, PNG, JPG, JPEG, TXT."
            )
        )

    temp_path = None

    try:

        file_extension = os.path.splitext(
            filename
        )[1].lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as temp_file:

            temp_path = temp_file.name

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        extracted_text = parse_document(
            temp_path
        )

        latency = time.perf_counter() - start_time

        logger.info(
            f"parse_test_completed | latency_sec={latency:.3f}",
            extra={
                "details": {
                    "endpoint": "/parse-test",
                    "filename": filename,
                    "characters_extracted": len(
                        extracted_text
                    ),
                    "latency_sec": round(
                        latency,
                        3
                    )
                }
            }
        )

        return {
            "filename": filename,
            "extracted_character_count": len(
                extracted_text
            ),
            "text_preview": extracted_text[:500]
        }

    except Exception as e:

        latency = time.perf_counter() - start_time

        logger.exception(
            f"parse_test_failed | {filename}",
            extra={
                "details": {
                    "endpoint": "/parse-test",
                    "filename": filename,
                    "error": str(e),
                    "latency_sec": round(
                        latency,
                        3
                    )
                }
            }
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to parse the document."
        )

    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)

        await file.close()
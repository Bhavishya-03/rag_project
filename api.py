from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import os

from main import ask_rag
from parser import parse_document

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
    return {"status": "healthy", "message": "Nutri-Query API is up and running."}

@app.post("/ask", response_model=QueryResponse, summary="Query RAG Pipeline")
def query_rag_endpoint(request: QueryRequest):
    """
    Send a question to the RAG pipeline.
    Returns the generated answer along with retrieved sources grouped by bucket.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    
    result = ask_rag(request.query)
    return result

@app.post("/parse-test", summary="Test Document Parser")
def parse_test_endpoint(request: ParseTestRequest):
    """
    Test image OCR or PDF text extraction on a specific file path.
    """
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found at specified path.")
    
    extracted_text = parse_document(request.file_path)
    return {
        "file_path": request.file_path,
        "extracted_character_count": len(extracted_text),
        "text_preview": extracted_text[:500]
    }
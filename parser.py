import os
from pypdf import PdfReader
from rapidocr_onnxruntime import RapidOCR

ocr_engine = RapidOCR()

def parse_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_image(file_path: str) -> str:
    try:
        result, _ = ocr_engine(file_path)
        if result:
            lines = [line[1] for line in result]
            return "\n".join(lines).strip()
        return ""
    except Exception as e:
        print(f"Error reading image {file_path}: {e}")
        return ""

# def parse_pdf(file_path: str) -> str:
#     """Extracts text from digital PDFs page by page."""
#     text = ""
#     try:
#         reader = PdfReader(file_path)
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#         return text.strip()
#     except Exception as e:
#         print(f"Error reading PDF {file_path}: {e}")
#         return ""
import pymupdf  # Modern import syntax
import numpy as np
from PIL import Image

def parse_pdf(file_path: str) -> str:
    """
    Extracts digital text from PDFs.
    If digital text is missing (scanned document),
    renders pages as images and passes raw bytes/array to RapidOCR.
    """
    text = ""
    try:
        doc = pymupdf.open(file_path)
        for page in doc:
            page_text = page.get_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
            else:
                # Render PDF page as image bytes
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                
                # Option 1: Pass raw bytes directly to RapidOCR
                result, _ = ocr_engine(img_bytes)
                
                # Option 2 (Alternative if bytes fail): Convert to numpy array
                # img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                # result, _ = ocr_engine(img_np)
                
                if result:
                    lines = [line[1] for line in result]
                    text += "\n".join(lines) + "\n"
                    
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""
    
def parse_document(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".txt":
        return parse_text(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return parse_image(file_path)
    elif ext == ".pdf":
        return parse_pdf(file_path)
    else:
        print(f"Unsupported file extension: {ext} for file {file_path}")
        return ""

if __name__ == "__main__":
    test_file_path = "data/bucket_2/sample_4_8.pdf" 
    
    if os.path.exists(test_file_path):
        print(f"Parsing file: {test_file_path} ...\n")
        output = parse_document(test_file_path)
        print("--- EXTRACTED TEXT START ---")
        print(output[:])
        print("\n--- EXTRACTED TEXT END ---")
    else:
        print(f"Please put a test file at '{test_file_path}' to run a quick test!")
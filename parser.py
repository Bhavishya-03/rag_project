import os
import pymupdf  
import numpy as np
from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR

ocr_engine = RapidOCR()

def parse_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_image(file_path: str) -> str:
    try:
        with Image.open(file_path) as img:
            # Fix EXIF orientation (rotated smartphone JPGs)
            img = ImageOps.exif_transpose(img)
            
            # CRITICAL: Force conversion to standard RGB (fixes CMYK/grayscale JPGs)
            img = img.convert("RGB")
            
            img_np = np.array(img)

        # Run RapidOCR
        result, _ = ocr_engine(img_np)
        
        if result:
            lines = [line[1] for line in result]
            extracted_text = "\n".join(lines).strip()
            print(f"  [OCR SUCCESS] '{file_path}': Extracted {len(extracted_text)} characters.")
            return extracted_text
        else:
            print(f"  [OCR EMPTY] '{file_path}': RapidOCR found no text.")
            return ""

    except Exception as e:
        print(f"  [OCR ERROR] Failed to process '{file_path}': {e}")
        return ""

def parse_pdf(file_path: str) -> str:
    """
    Extracts digital text from PDFs.
    If digital text is missing (scanned document),
    renders pages as images and passes raw bytes to RapidOCR.
    """
    text = ""
    try:
        doc = pymupdf.open(file_path)
        for page in doc:
            page_text = page.get_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
            else:
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                
                result, _ = ocr_engine(img_bytes)
                
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
    test_file_path = "data/bucket_2/food_4.jpeg" 
    
    if os.path.exists(test_file_path):
        print(f"Parsing file: {test_file_path} ...\n")
        output = parse_document(test_file_path)
        print("--- EXTRACTED TEXT START ---")
        print(output)
        print("\n--- EXTRACTED TEXT END ---")
    else:
        print(f"Please put a test file at '{test_file_path}' to run a quick test!")
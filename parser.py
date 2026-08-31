import os
import time
import pymupdf
import numpy as np
from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR
from logging_config import get_logger

logger = get_logger(__name__)

ocr_engine = RapidOCR()


def parse_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_image(file_path: str) -> str:
    start_time = time.perf_counter()

    try:
        with Image.open(file_path) as img:
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            img_np = np.array(img)

        result, _ = ocr_engine(img_np)

        if result:
            lines = [line[1] for line in result]
            extracted_text = "\n".join(lines).strip()

            logger.info(
                "ocr_completed",
                extra={
                    "details": {
                        "filename": os.path.basename(file_path),
                        "characters_extracted": len(extracted_text),
                        "duration_seconds": round(
                            time.perf_counter() - start_time, 3
                        )
                    }
                }
            )

            return extracted_text

        logger.warning(
            "ocr_empty",
            extra={
                "details": {
                    "filename": os.path.basename(file_path),
                    "duration_seconds": round(
                        time.perf_counter() - start_time, 3
                    )
                }
            }
        )

        return ""

    except Exception as e:
        logger.exception(
            "ocr_failed",
            extra={
                "details": {
                    "filename": os.path.basename(file_path),
                    "error": str(e),
                    "duration_seconds": round(
                        time.perf_counter() - start_time, 3
                    )
                }
            }
        )
        return ""


def parse_pdf(file_path: str) -> str:
    start_time = time.perf_counter()
    text_parts = []
    ocr_pages = 0

    try:
        with pymupdf.open(file_path) as doc:
            total_pages = len(doc)

            for page in doc:
                page_text = page.get_text()

                if page_text and page_text.strip():
                    text_parts.append(page_text)
                else:
                    ocr_pages += 1

                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")

                    result, _ = ocr_engine(img_bytes)

                    if result:
                        lines = [line[1] for line in result]
                        text_parts.append("\n".join(lines))

        extracted_text = "\n".join(text_parts).strip()

        logger.info(
            "pdf_parsing_completed",
            extra={
                "details": {
                    "filename": os.path.basename(file_path),
                    "pages": total_pages,
                    "ocr_pages": ocr_pages,
                    "characters_extracted": len(extracted_text),
                    "duration_seconds": round(
                        time.perf_counter() - start_time, 3
                    )
                }
            }
        )

        return extracted_text

    except Exception as e:
        logger.exception(
            "pdf_parsing_failed",
            extra={
                "details": {
                    "filename": os.path.basename(file_path),
                    "error": str(e),
                    "duration_seconds": round(
                        time.perf_counter() - start_time, 3
                    )
                }
            }
        )
        return ""


def parse_document(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".txt":
            return parse_text(file_path)

        if ext in [".png", ".jpg", ".jpeg"]:
            return parse_image(file_path)

        if ext == ".pdf":
            return parse_pdf(file_path)

        logger.warning(
            "unsupported_file",
            extra={
                "details": {
                    "filename": os.path.basename(file_path),
                    "extension": ext
                }
            }
        )

        return ""

    except Exception as e:
        logger.exception(
            "document_parsing_failed",
            extra={
                "details": {
                    "filename": os.path.basename(file_path),
                    "error": str(e)
                }
            }
        )
        return ""
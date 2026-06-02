"""Service for extracting text from PDF files using pdfplumber + Tesseract OCR (CPU-only)."""

from typing import Optional
from pathlib import Path
from io import BytesIO
import logging
import tempfile

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from app.utils.exceptions import InvalidPDFException

logger = logging.getLogger(__name__)


def validate_pdf(file_content: bytes) -> bool:
    """
    Validate if content is a valid PDF by checking file header.
    
    Args:
        file_content: Raw file bytes
    
    Returns:
        True if valid PDF, False otherwise
    """
    return file_content.startswith(b"%PDF")


def extract_pdf_text(pdf_bytes: bytes, max_pages: Optional[int] = None) -> str:
    """
    Extract text from PDF content (as bytes) with fallback to OCR for scanned pages.
    
    Strategy:
    1. Try pdfplumber first (for PDFs with embedded text) - FAST (~0.1-0.5s)
    2. If minimal text found, use Tesseract OCR on page images - SLOWER (~1-3s per page)
    
    Args:
        pdf_bytes: PDF file content as bytes
        max_pages: Maximum number of pages to extract (None for all)
    
    Returns:
        Extracted text content with preserved structure
    
    Raises:
        InvalidPDFException: If content is not a valid PDF or cannot be processed
    """
    
    # Validate PDF signature
    if not validate_pdf(pdf_bytes):
        raise InvalidPDFException(
            detail="File must be a valid PDF (invalid PDF signature)",
            instance="/api/v1/pdf/process"
        )
    
    try:
        all_text = []
        
        # Step 1: Try pdfplumber for embedded text (fast path)
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            total_pages = len(pdf.pages)
            pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
            
            logger.info(f"Processing PDF: {total_pages} pages (limit: {pages_to_process})")
            
            for page_idx, page in enumerate(pdf.pages[:pages_to_process]):
                try:
                    # Extract embedded text
                    text = page.extract_text()
                    
                    # If page has minimal text, try OCR
                    if not text or len(text.strip()) < 50:
                        logger.debug(f"Page {page_idx + 1}: Limited embedded text, attempting OCR")
                        ocr_text = _extract_text_with_ocr(pdf_bytes, page_idx)
                        text = text if text else ocr_text
                    
                    if text:
                        all_text.append(f"--- Page {page_idx + 1} ---\n{text}\n")
                    
                except Exception as e:
                    logger.warning(f"Error processing page {page_idx + 1}: {str(e)}")
                    continue
        
        result = "\n".join(all_text).strip()
        return result if result else ""
    
    except pdfplumber.PDFException as e:
        raise InvalidPDFException(
            detail=f"Invalid PDF file: {str(e)}",
            instance="/api/v1/pdf/process"
        )
    except Exception as e:
        raise InvalidPDFException(
            detail=f"Error extracting PDF text: {str(e)}",
            instance="/api/v1/pdf/process"
        )


def _extract_text_with_ocr(pdf_bytes: bytes, page_num: int) -> str:
    """
    Extract text from a specific PDF page using Tesseract OCR.
    
    Args:
        pdf_bytes: PDF content as bytes
        page_num: Zero-indexed page number
    
    Returns:
        Extracted text from OCR
    """
    try:
        # Save bytes to temporary file for pdf2image
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        try:
            # Convert PDF page to image (300 DPI for better OCR accuracy)
            images = convert_from_path(
                tmp_path,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=300
            )
            
            if not images:
                return ""
            
            # Run Tesseract OCR on the image
            image = images[0]
            text = pytesseract.image_to_string(image, lang='spa+eng')
            
            return text.strip()
        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)
    
    except Exception as e:
        logger.error(f"OCR failed for page {page_num + 1}: {str(e)}")
        return ""


def extract_metadata(pdf_bytes: bytes) -> dict:
    """
    Extract PDF metadata including page count.
    
    Args:
        pdf_bytes: PDF file content as bytes
    
    Returns:
        Dict with num_pages, title, and format
        
    Raises:
        InvalidPDFException: If content is not a valid PDF or cannot be processed
    """
    if not validate_pdf(pdf_bytes):
        raise InvalidPDFException(
            detail="File must be a valid PDF (invalid PDF signature)",
            instance="/api/v1/pdf/process"
        )
    
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            page_count = len(pdf.pages)
            title = pdf.metadata.get('Title', 'Unknown') if pdf.metadata else 'Unknown'
        
        return {
            "num_pages": page_count,
            "title": title,
            "format": "PDF"
        }
    except pdfplumber.PDFException as e:
        raise InvalidPDFException(
            detail=f"Invalid PDF file: {str(e)}",
            instance="/api/v1/pdf/process"
        )
    except Exception as e:
        raise InvalidPDFException(
            detail=f"Error extracting PDF metadata: {str(e)}",
            instance="/api/v1/pdf/process"
        )

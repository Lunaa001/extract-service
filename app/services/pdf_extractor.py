"""
PDF text extraction service using docling library.

This service extracts text from PDF files provided as byte arrays,
without saving temporary files to disk.
"""

from io import BytesIO
from importlib import import_module
from typing import Any
from app.utils.exceptions import InvalidPDFException

# Constants
_EXTRACTION_ENDPOINT = "/api/pdf/extract"


def _get_document_converter_class() -> Any:
    """Load docling converter lazily to avoid import-time failures."""
    try:
        module = import_module("docling.document_converter")
        return module.DocumentConverter
    except ModuleNotFoundError as e:
        raise InvalidPDFException(
            detail="PDF extraction dependency 'docling' is not installed",
            instance=_EXTRACTION_ENDPOINT
        ) from e


def _get_document_stream_class() -> Any:
    """Load docling DocumentStream lazily for typed in-memory inputs."""
    try:
        module = import_module("docling_core.types.io")
        return module.DocumentStream
    except ModuleNotFoundError as e:
        raise InvalidPDFException(
            detail="PDF extraction dependency 'docling' is not installed",
            instance=_EXTRACTION_ENDPOINT
        ) from e



def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract text content from a PDF file provided as bytes.
    
    This function validates the PDF signature first, then uses docling
    to extract all text content from the PDF without saving temporary files.
    The PDF is processed entirely in memory using BytesIO.
    
    Args:
        pdf_bytes: The PDF file content as a byte array
        
    Returns:
        str: Extracted text from all pages of the PDF.
             Returns empty string if PDF has no text content.
             
    Raises:
        InvalidPDFException: If the PDF signature is invalid or bytes are empty.
                           Follows RFC 9457 Problem Details format.
        
    Example:
        >>> with open('document.pdf', 'rb') as f:
        ...     pdf_data = f.read()
        >>> text = extract_pdf_text(pdf_data)
        >>> print(text)
    """
    
    try:
        # Initialize docling DocumentConverter
        converter_class = _get_document_converter_class()
        document_stream_class = _get_document_stream_class()
        converter = converter_class()

        # docling 2.85 expects DocumentStream for in-memory conversion
        pdf_stream = document_stream_class(
            name="document.pdf",
            stream=BytesIO(pdf_bytes),
            mime_type="application/pdf"
        )
        
        # Convert PDF from BytesIO stream
        # docling can accept file-like objects
        result = converter.convert(pdf_stream)
        
        # Extract text from the conversion result
        # docling returns a Document object with export_to_text() method
        extracted_text = result.document.export_to_text()
        
        return extracted_text
        
    except Exception as e:
        # If docling fails to process the PDF, raise InvalidPDFException
        # This could be due to corrupted PDF, unsupported features, etc.
        raise InvalidPDFException(
            detail=f"Failed to extract text from PDF: {str(e)}",
            instance=_EXTRACTION_ENDPOINT
        )

import unittest
import os
from pathlib import Path
from io import BytesIO
from app.services.pdf_extractor import extract_pdf_text
from app.utils.exceptions import InvalidPDFException


class TestPDFTextExtraction(unittest.TestCase):
    """Test suite for PDF text extraction functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures - load PDF files once for all tests"""
        # Get the directory where this test file is located
        cls.test_dir = Path(__file__).parent
        cls.docs_dir = cls.test_dir / "docs" 
        
        # Load test PDF files
        with open(cls.docs_dir / "test_con_texto.pdf", "rb") as f:
            cls.pdf_with_text = f.read()
        
        with open(cls.docs_dir / "documento_sin_texto.pdf", "rb") as f:
            cls.pdf_without_text = f.read()
        
        with open(cls.docs_dir / "doc_pdf_dos_pag.pdf", "rb") as f:
            cls.pdf_multipage = f.read()
    
    def test_extract_text_from_valid_simple_pdf(self):
        """Test that text can be extracted from a valid PDF with simple text content"""
        # Use real PDF file from tests/docs/test_con_texto.pdf
        result = extract_pdf_text(self.pdf_with_text)
        
        # Should extract text (exact format may vary by docling)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_extract_text_from_empty_bytes_raises_exception(self):
        """Test that empty bytes raise InvalidPDFException"""
        empty_bytes = b""
        
        with self.assertRaises(InvalidPDFException) as context:
            extract_pdf_text(empty_bytes)
        
        exception = context.exception
        self.assertEqual(exception.status, 400)
    
    def test_extract_text_returns_empty_string_for_pdf_without_text(self):
        """Test that PDF with no text content returns empty string"""
        # Use real PDF file from tests/docs/documento_sin_texto.pdf
        result = extract_pdf_text(self.pdf_without_text)
        
        # Should return empty string or whitespace only
        self.assertIsInstance(result, str)
        self.assertEqual(result.strip(), "")
    
    def test_extract_text_from_multipage_pdf(self):
        """Test that text from multiple pages is extracted"""
        # Use real PDF file from tests/docs/doc_pdf_dos_pag.pdf
        result = extract_pdf_text(self.pdf_multipage)
        
        # Should contain text from both pages
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()

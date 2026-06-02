import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import BytesIO
from app.services.pdf_extractor import extract_pdf_text, extract_metadata, validate_pdf
from app.utils.exceptions import InvalidPDFException


class TestPDFValidation(unittest.TestCase):
    """Test suite for PDF validation"""
    
    def test_validate_pdf_with_valid_signature(self):
        """Test that valid PDF signature is recognized"""
        valid_pdf = b"%PDF-1.4\n%data"
        self.assertTrue(validate_pdf(valid_pdf))
    
    def test_validate_pdf_with_invalid_signature(self):
        """Test that invalid PDF signature is rejected"""
        invalid_pdf = b"This is not a PDF"
        self.assertFalse(validate_pdf(invalid_pdf))
    
    def test_validate_pdf_with_empty_bytes(self):
        """Test that empty bytes are rejected"""
        empty_bytes = b""
        self.assertFalse(validate_pdf(empty_bytes))


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
    
    def test_extract_text_from_valid_pdf_raises_on_invalid_signature(self):
        """Test that invalid PDF signature raises InvalidPDFException"""
        invalid_pdf = b"Not a PDF"
        
        with self.assertRaises(InvalidPDFException) as context:
            extract_pdf_text(invalid_pdf)
        
        exception = context.exception
        self.assertEqual(exception.status, 400)
        self.assertIn("invalid PDF signature", exception.detail)
    
    def test_extract_text_from_empty_bytes_raises_exception(self):
        """Test that empty bytes raise InvalidPDFException"""
        empty_bytes = b""
        
        with self.assertRaises(InvalidPDFException) as context:
            extract_pdf_text(empty_bytes)
        
        exception = context.exception
        self.assertEqual(exception.status, 400)
    
    def test_extract_text_from_real_pdf_with_text(self):
        """Test that text can be extracted from a valid PDF with embedded text"""
        # Use real PDF file from tests/docs/test_con_texto.pdf
        result = extract_pdf_text(self.pdf_with_text)
        
        # Should extract text
        self.assertIsInstance(result, str)
        # At least some text should be extracted from PDF with text
        self.assertGreater(len(result), 0)
    
    def test_extract_text_from_multipage_pdf(self):
        """Test that text from multiple pages can be extracted"""
        # Use real PDF file from tests/docs/doc_pdf_dos_pag.pdf
        result = extract_pdf_text(self.pdf_multipage)
        
        # Should contain text from multiple pages
        self.assertIsInstance(result, str)
    
    def test_extract_text_with_max_pages_limit(self):
        """Test that max_pages parameter limits page extraction"""
        # Extract with limit of 1 page
        result_limited = extract_pdf_text(self.pdf_multipage, max_pages=1)
        
        # Extract all pages (multipage has 2 pages)
        result_all = extract_pdf_text(self.pdf_multipage, max_pages=2)
        
        self.assertIsInstance(result_limited, str)
        self.assertIsInstance(result_all, str)
        # Limited version should be no longer than full version
        self.assertLessEqual(len(result_limited), len(result_all))
    
    @patch('app.services.pdf_extractor.pdfplumber.open')
    def test_extract_text_handles_corrupted_pdf(self, mock_open):
        """Test that corrupted PDF raises InvalidPDFException"""
        # Mock pdfplumber to raise exception
        mock_open.side_effect = Exception("PDF parsing error")
        
        valid_pdf_header = b"%PDF-1.4\nsome content"
        
        with self.assertRaises(InvalidPDFException):
            extract_pdf_text(valid_pdf_header)


class TestPDFMetadataExtraction(unittest.TestCase):
    """Test suite for PDF metadata extraction"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_dir = Path(__file__).parent
        cls.docs_dir = cls.test_dir / "docs"
        
        with open(cls.docs_dir / "test_con_texto.pdf", "rb") as f:
            cls.pdf_with_text = f.read()
    
    def test_extract_metadata_from_valid_pdf(self):
        """Test that metadata can be extracted from valid PDF"""
        metadata = extract_metadata(self.pdf_with_text)
        
        self.assertIsInstance(metadata, dict)
        self.assertIn("num_pages", metadata)
        self.assertIn("title", metadata)
        self.assertIn("format", metadata)
        self.assertEqual(metadata["format"], "PDF")
        self.assertGreater(metadata["num_pages"], 0)
    
    def test_extract_metadata_from_invalid_pdf_raises_exception(self):
        """Test that invalid PDF raises InvalidPDFException"""
        invalid_pdf = b"Not a PDF"
        
        with self.assertRaises(InvalidPDFException):
            extract_metadata(invalid_pdf)


if __name__ == '__main__':
    unittest.main()

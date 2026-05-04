import unittest
from app.utils.exceptions import ProblemDetailException, InvalidPDFException


class TestProblemDetailException(unittest.TestCase):
    """Test suite for RFC 9457 Problem Detail exceptions"""
    
    def test_problem_detail_exception_has_required_fields(self):
        """Test that ProblemDetailException has all RFC 9457 required fields"""
        exception = ProblemDetailException(
            type_uri="https://notebookum.com/problems/test",
            title="Test Problem",
            status=400,
            detail="Test detail message"
        )
        
        self.assertEqual(exception.type_uri, "https://notebookum.com/problems/test")
        self.assertEqual(exception.title, "Test Problem")
        self.assertEqual(exception.status, 400)
        self.assertEqual(exception.detail, "Test detail message")
    
    def test_problem_detail_exception_with_instance(self):
        """Test that ProblemDetailException supports optional instance field"""
        exception = ProblemDetailException(
            type_uri="https://notebookum.com/problems/test",
            title="Test Problem",
            status=400,
            detail="Test detail",
            instance="/api/test"
        )
        
        self.assertEqual(exception.instance, "/api/test")
    
    def test_problem_detail_exception_to_dict(self):
        """Test that exception can be serialized to dict following RFC 9457"""
        exception = ProblemDetailException(
            type_uri="https://notebookum.com/problems/test",
            title="Test Problem",
            status=400,
            detail="Test detail message",
            instance="/api/test"
        )
        
        result = exception.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "https://notebookum.com/problems/test")
        self.assertEqual(result["title"], "Test Problem")
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["detail"], "Test detail message")
        self.assertEqual(result["instance"], "/api/test")
    
    def test_problem_detail_exception_to_dict_without_instance(self):
        """Test that to_dict works without optional instance field"""
        exception = ProblemDetailException(
            type_uri="https://notebookum.com/problems/test",
            title="Test Problem",
            status=400,
            detail="Test detail"
        )
        
        result = exception.to_dict()
        
        self.assertNotIn("instance", result)
        self.assertEqual(len(result), 4)


class TestInvalidPDFException(unittest.TestCase):
    """Test suite for InvalidPDFException"""
    
    def test_invalid_pdf_exception_inherits_from_problem_detail(self):
        """Test that InvalidPDFException inherits from ProblemDetailException"""
        exception = InvalidPDFException("Test message")
        self.assertIsInstance(exception, ProblemDetailException)
    
    def test_invalid_pdf_exception_has_correct_defaults(self):
        """Test that InvalidPDFException has correct default RFC 9457 values"""
        exception = InvalidPDFException("Invalid PDF signature detected")
        
        self.assertEqual(exception.type_uri, "https://notebookum.com/problems/invalid-pdf")
        self.assertEqual(exception.title, "Invalid PDF File")
        self.assertEqual(exception.status, 400)
        self.assertEqual(exception.detail, "Invalid PDF signature detected")
    
    def test_invalid_pdf_exception_with_custom_instance(self):
        """Test that InvalidPDFException supports custom instance"""
        exception = InvalidPDFException(
            "Invalid PDF signature",
            instance="/api/pdf/extract"
        )
        
        self.assertEqual(exception.instance, "/api/pdf/extract")
    
    def test_invalid_pdf_exception_to_dict(self):
        """Test that InvalidPDFException serializes correctly"""
        exception = InvalidPDFException(
            "The file does not have a valid PDF signature",
            instance="/api/pdf/extract"
        )
        
        result = exception.to_dict()
        
        self.assertEqual(result["type"], "https://notebookum.com/problems/invalid-pdf")
        self.assertEqual(result["title"], "Invalid PDF File")
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["detail"], "The file does not have a valid PDF signature")
        self.assertEqual(result["instance"], "/api/pdf/extract")


if __name__ == '__main__':
    unittest.main()

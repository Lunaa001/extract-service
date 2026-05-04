"""
RFC 9457 Problem Details for HTTP APIs exceptions.

This module implements exception classes following the RFC 9457 standard
for problem details in HTTP APIs.

Reference: https://www.rfc-editor.org/rfc/rfc9457.html
"""

from typing import Optional


class ProblemDetailException(Exception):
    """
    Base exception class implementing RFC 9457 Problem Details.
    
    RFC 9457 defines a standard way to carry machine-readable details
    of errors in HTTP response content.
    
    Attributes:
        type_uri: A URI reference that identifies the problem type
        title: A short, human-readable summary of the problem type
        status: The HTTP status code
        detail: A human-readable explanation specific to this occurrence
        instance: A URI reference that identifies the specific occurrence
    """
    
    def __init__(
        self,
        type_uri: str,
        title: str,
        status: int,
        detail: str,
        instance: Optional[str] = None
    ):
        """
        Initialize a ProblemDetailException.
        
        Args:
            type_uri: URI identifying the problem type
            title: Short summary of the problem
            status: HTTP status code (e.g., 400, 404, 500)
            detail: Detailed explanation of this specific error
            instance: Optional URI identifying this specific occurrence
        """
        super().__init__(detail)
        self.type_uri = type_uri
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance
    
    def to_dict(self) -> dict:
        """
        Convert the exception to a dictionary following RFC 9457 format.
        
        Returns:
            dict: Dictionary with type, title, status, detail, and optionally instance
        """
        result = {
            "type": self.type_uri,
            "title": self.title,
            "status": self.status,
            "detail": self.detail
        }
        
        if self.instance is not None:
            result["instance"] = self.instance
        
        return result


class InvalidPDFException(ProblemDetailException):
    """
    Exception raised when a PDF file is invalid or has an incorrect signature.
    
    This exception follows RFC 9457 Problem Details standard with
    predefined values for PDF validation errors.
    """
    
    def __init__(self, detail: str, instance: Optional[str] = None):
        """
        Initialize an InvalidPDFException.
        
        Args:
            detail: Specific explanation of why the PDF is invalid
            instance: Optional URI identifying where the error occurred
        """
        super().__init__(
            type_uri="https://notebookum.com/problems/invalid-pdf",
            title="Invalid PDF File",
            status=400,
            detail=detail,
            instance=instance
        )


class InvalidBase64Exception(ProblemDetailException):
    """
    Exception raised when Base64 content is malformed.

    This exception follows RFC 9457 Problem Details standard with
    predefined values for Base64 validation errors.
    """

    def __init__(self, detail: str, instance: Optional[str] = None):
        super().__init__(
            type_uri="https://notebookum.com/problems/invalid-base64",
            title="Invalid Base64 Content",
            status=400,
            detail=detail,
            instance=instance,
        )


class InvalidPdfRequestException(ProblemDetailException):
    """Exception raised when the PDF request body fails validation."""

    def __init__(self, detail: str, instance: Optional[str] = None):
        super().__init__(
            type_uri="https://notebookum.com/problems/invalid-pdf-request",
            title="Invalid PDF Request",
            status=422,
            detail=detail,
            instance=instance,
        )

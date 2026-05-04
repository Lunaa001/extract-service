import unittest

from pydantic import ValidationError

from app.controllers.pdf_request import PdfRequest


class TestPdfRequest(unittest.TestCase):
    def test_accepts_valid_base64_content(self) -> None:
        request = PdfRequest(file_name="document.pdf", content="UERG")

        self.assertEqual(request.file_name, "document.pdf")
        self.assertEqual(request.content, "UERG")

    def test_rejects_empty_content(self) -> None:
        with self.assertRaises(ValidationError):
            PdfRequest(file_name="document.pdf", content="")

    def test_rejects_invalid_base64_content(self) -> None:
        with self.assertRaises(ValidationError):
            PdfRequest(file_name="document.pdf", content="not-base64")
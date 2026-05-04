import unittest

from fastapi.testclient import TestClient

import app.routers.pdf_router as pdf_router_module
from app.utils.exceptions import InvalidPDFException
from main import app


class TestPdfRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_process_pdf_returns_success_payload(self) -> None:
        original_extract_pdf_text = pdf_router_module.extract_pdf_text
        pdf_router_module.extract_pdf_text = lambda _pdf_bytes: "Hola mundo"

        try:
            response = self.client.post(
                "/api/v1/pdf/process",
                json={"file_name": "document.pdf", "content": "UERG"},
            )
        finally:
            pdf_router_module.extract_pdf_text = original_extract_pdf_text

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "message": "PDF procesado correctamente",
                "content": "Hola mundo",
            },
        )

    def test_process_pdf_returns_rfc9457_for_invalid_base64(self) -> None:
        response = self.client.post(
            "/api/v1/pdf/process",
            json={"file_name": "document.pdf", "content": "not-base64"},
        )

        payload = response.json()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(payload["type"], "https://notebookum.com/problems/invalid-pdf-request")
        self.assertEqual(payload["title"], "Invalid PDF Request")
        self.assertIn("Base64", payload["detail"])

    def test_process_pdf_returns_rfc9457_for_pdf_extraction_failure(self) -> None:
        original_extract_pdf_text = pdf_router_module.extract_pdf_text

        def raise_invalid_pdf(_pdf_bytes: bytes) -> str:
            raise InvalidPDFException("The PDF is invalid")

        pdf_router_module.extract_pdf_text = raise_invalid_pdf

        try:
            response = self.client.post(
                "/api/v1/pdf/process",
                json={"file_name": "document.pdf", "content": "UERG"},
            )
        finally:
            pdf_router_module.extract_pdf_text = original_extract_pdf_text

        payload = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["type"], "https://notebookum.com/problems/invalid-pdf")
        self.assertEqual(payload["title"], "Invalid PDF File")
"""
Router for processing Base64-encoded PDF documents.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.controllers.pdf_request import PdfRequest
from app.services.pdf_extractor import extract_pdf_text
from app.utils.exceptions import InvalidBase64Exception
from app.utils.pdf_decoder import decode_pdf_content


router = APIRouter(prefix="/api/v1/pdf", tags=["pdf"])


@router.post("/process")
def process_pdf(request: PdfRequest) -> dict[str, str]:
	"""Decode the request payload and extract the PDF text."""

	try:
		pdf_bytes = decode_pdf_content(request.content)
	except ValueError as exc:
		raise InvalidBase64Exception(
			detail=str(exc),
			instance="/api/v1/pdf/process",
		) from exc

	extracted_text = extract_pdf_text(pdf_bytes)
	return {
		"status": "ok",
		"message": "PDF procesado correctamente",
		"content": extracted_text,
	}

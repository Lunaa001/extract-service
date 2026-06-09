"""
Router for processing Base64-encoded PDF documents.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.controllers.pdf_request import PdfRequest
from app.services.pdf_extractor import extract_pdf_text, extract_metadata
from app.utils.exceptions import InvalidBase64Exception
from app.utils.pdf_decoder import decode_pdf_content


router = APIRouter(prefix="/api/v1/pdf", tags=["pdf"])


@router.post("/process")
def process_pdf(request: PdfRequest) -> dict:
	"""Decode the request payload and extract the PDF text.
	
	Returns standardized response matching the expected format:
	{
	  "document_id": "uuid",
	  "filename": "...",
	  "job_id": "uuid",
	  "correlation_id": "uuid",
	  "event_type": "extraction.processing",
	  "content": "extracted text...",
	  "created_at": "ISO-8601",
	  "audit_metadata": { ... }
	}
	"""

	try:
		pdf_bytes = decode_pdf_content(request.content)
	except ValueError as exc:
		raise InvalidBase64Exception(
			detail=str(exc),
			instance="/api/v1/pdf/process",
		) from exc

	extracted_text = extract_pdf_text(pdf_bytes, max_pages=request.max_pages)
	
	# Determinar bulkhead basado en tamaño del contenido
	size_bytes = len(pdf_bytes)
	bulkhead = "light" if size_bytes < 5 * 1024 * 1024 else "heavy"
	
	job_id = str(uuid.uuid4())
	correlation_id = str(uuid.uuid4())
	
	return {
		"status": "ok",
		"message": "PDF procesado correctamente",
		"content": extracted_text,
		"document_id": None,  # Se asigna por el controller
		"filename": request.file_name,
		"job_id": job_id,
		"correlation_id": correlation_id,
		"event_type": "extraction.processing",
		"bulkhead": bulkhead,
		"created_at": datetime.now(timezone.utc).isoformat(),
		"audit_metadata": {
			"bulkhead": bulkhead,
			"content_type": "application/pdf",
			"filename": request.file_name,
			"pdf_retained": False,
			"size_bytes": size_bytes,
		}
	}


@router.post("/metadata")
def get_pdf_metadata(request: PdfRequest) -> dict:
	"""Extract metadata from PDF."""

	try:
		pdf_bytes = decode_pdf_content(request.content)
	except ValueError as exc:
		raise InvalidBase64Exception(
			detail=str(exc),
			instance="/api/v1/pdf/metadata",
		) from exc

	metadata = extract_metadata(pdf_bytes)
	return {
		"status": "ok",
		"message": "Metadatos extraídos correctamente",
		"metadata": metadata,
	}

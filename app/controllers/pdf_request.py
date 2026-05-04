"""
Request model for PDF processing.
"""

from __future__ import annotations

import base64
import binascii

from pydantic import BaseModel, Field, field_validator


class PdfRequest(BaseModel):
    """Request body for PDF processing."""

    file_name: str = Field(min_length=1)
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validate_base64_content(cls, value: str) -> str:
        """Ensure the content is strict Base64 before the request is accepted."""

        try:
            base64.b64decode(value, validate=True)
        except binascii.Error as exc:
            raise ValueError("content must be a valid Base64 string") from exc

        return value
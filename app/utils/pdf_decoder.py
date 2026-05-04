"""
Base64 PDF decoding helpers.
"""

from __future__ import annotations

import base64
import binascii


def decode_pdf_content(content_b64: str) -> bytes:
    """
    Decode a Base64 string into PDF bytes.

    Args:
        content_b64: Base64-encoded PDF content.

    Returns:
        The decoded PDF bytes.

    Raises:
        ValueError: If the content is not valid Base64.
    """

    try:
        return base64.b64decode(content_b64, validate=True)
    except binascii.Error as exc:
        raise ValueError("The content field must be valid Base64-encoded PDF data.") from exc
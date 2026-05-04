import unittest

from app.utils.pdf_decoder import decode_pdf_content


class TestPdfDecoder(unittest.TestCase):
    def test_decodes_valid_base64_to_bytes(self) -> None:
        decoded = decode_pdf_content("UERG")

        self.assertEqual(decoded, b"PDF")

    def test_rejects_invalid_base64(self) -> None:
        with self.assertRaisesRegex(ValueError, "Base64"):
            decode_pdf_content("invalid-base64")
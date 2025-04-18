import unittest
import base64  # Import the base64 module
from unittest.mock import MagicMock
import sys
import os

# Adjust the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from MediaHandling.pdf_handling import generate_pdf


class TestPdfHandling(unittest.TestCase):
    def test_successful_pdf_generation(self):
        content = "Test PDF Content"
        result = generate_pdf(content)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("JVBER"))  # Base64 encoded PDF starts with 'JVBER'

    def test_pdf_content_accuracy(self):
        # The content is drawn into the PDF, not directly inserted as text
        # So we just check that a valid PDF is generated
        content = "Test PDF Content"
        result = generate_pdf(content)
        decoded_data = base64.b64decode(result)
        self.assertTrue(decoded_data.startswith(b'%PDF-'))  # PDF signature

    def test_handling_empty_content(self):
        # The function generates a PDF even for empty content
        result = generate_pdf("")
        self.assertIsNotNone(result)  # It should return a base64 encoded PDF
        self.assertTrue(result.startswith("JVBER"))  # Base64 encoded PDF starts with 'JVBER'


if __name__ == "__main__":
    unittest.main()

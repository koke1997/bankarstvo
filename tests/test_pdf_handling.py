import unittest
import base64  # Import the base64 module
from unittest.mock import MagicMock
import sys
import os

# Adjust the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from MediaHandling.pdf_handling import generate_pdf


class TestPdfHandling(unittest.TestCase):
    def test_successful_pdf_generation(self):
        content = 'Test PDF Content'
        result = generate_pdf(content)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('JVBER'))  # Base64 encoded PDF starts with 'JVBER'

    def test_pdf_content_accuracy(self):
        content = 'Test PDF Content'
        result = generate_pdf(content)
        decoded_pdf = base64.b64decode(result).decode('latin1')
        self.assertIn(content, decoded_pdf)

    def test_handling_empty_content(self):
        result = generate_pdf('')
        self.assertIsNone(result)  # Assuming generate_pdf returns None for empty content

if __name__ == '__main__':
    unittest.main()

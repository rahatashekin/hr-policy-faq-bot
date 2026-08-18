"""Unit tests for the BRAC RSP FAQ Bot."""

import unittest

from extract import extract_text
from chunk import chunk_text


class TestExtractor(unittest.TestCase):
    """Test text extraction."""

    def test_plain_text(self):
        result = extract_text(b"Hello, this is a test.", "text/plain", "test.txt")
        self.assertEqual(result, "Hello, this is a test.")

    def test_empty_bytes(self):
        result = extract_text(b"", "text/plain", "empty.txt")
        self.assertEqual(result, "")

    def test_utf8_fallback(self):
        result = extract_text(b"Unknown data", "application/octet-stream", "file.bin")
        self.assertIn("Unknown data", result)


class TestChunker(unittest.TestCase):
    """Test text chunking."""

    def test_short_text(self):
        chunks = chunk_text("Short text.", "test.txt", chunk_size=500)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["text"], "Short text.")
        self.assertEqual(chunks[0]["filename"], "test.txt")
        self.assertEqual(chunks[0]["chunk_index"], 0)

    def test_empty(self):
        self.assertEqual(chunk_text("", "test.txt"), [])

    def test_whitespace(self):
        self.assertEqual(chunk_text("   \n\n  ", "test.txt"), [])

    def test_multi_paragraph(self):
        text = "Paragraph one. " * 50 + "\n\n" + "Paragraph two. " * 50
        chunks = chunk_text(text, "doc.pdf", chunk_size=200)
        self.assertGreater(len(chunks), 1)

    def test_sequential_index(self):
        text = "\n\n".join([f"Section {i}. " * 30 for i in range(5)])
        chunks = chunk_text(text, "doc.pdf", chunk_size=100)
        indices = [c["chunk_index"] for c in chunks]
        self.assertEqual(indices, list(range(len(chunks))))


if __name__ == "__main__":
    unittest.main()

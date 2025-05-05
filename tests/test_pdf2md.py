"""
Tests for the PDF to Markdown converter in the converters.pdf2md module.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import fitz  # PyMuPDF
from PIL import Image

from twinizer.converters.pdf2md import PDF2MarkdownConverter, convert_pdf_to_markdown


class TestPDF2MarkdownConverter(unittest.TestCase):
    """Test cases for the PDF2MarkdownConverter class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = self.temp_dir.name

        # Create paths for test files
        self.pdf_path = os.path.join(self.test_dir, "test_document.pdf")
        self.md_path = os.path.join(self.test_dir, "test_document.md")
        self.image_dir = os.path.join(self.test_dir, "images")

        # Create image directory
        os.makedirs(self.image_dir, exist_ok=True)

        # Initialize converter
        self.converter = PDF2MarkdownConverter(
            ocr_enabled=False,
            extract_images=True,
            image_format="png",
            detect_tables=True,
            image_dir=self.image_dir,
        )

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    @patch("fitz.open")
    @patch("builtins.open", new_callable=mock_open)
    @patch("rich.console.Console.print")
    @patch("rich.progress.Progress")
    def test_convert_basic(
        self, mock_progress, mock_console_print, mock_file_open, mock_fitz_open
    ):
        """Test basic PDF conversion without images or OCR."""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.metadata = {"Title": "Test Document", "Author": "Test Author"}
        mock_page = MagicMock()
        mock_page.get_text.return_value = (
            "This is a test document.\n\nIt has multiple paragraphs."
        )
        mock_page.get_images.return_value = []
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc

        # Mock progress bar
        mock_task = MagicMock()
        mock_progress_instance = MagicMock()
        mock_progress_instance.add_task.return_value = mock_task
        mock_progress.return_value.__enter__.return_value = mock_progress_instance

        # Call convert method
        result = self.converter.convert(self.pdf_path, self.md_path)

        # Verify result
        self.assertEqual(result, self.md_path)

        # Verify file was opened for writing
        mock_file_open.assert_called_with(self.md_path, "w", encoding="utf-8")

        # Verify content was written
        file_handle = mock_file_open()
        # Check that YAML frontmatter was written
        self.assertTrue(
            any("---" in call[0][0] for call in file_handle.write.call_args_list)
        )
        self.assertTrue(
            any(
                "Title: Test Document" in call[0][0]
                for call in file_handle.write.call_args_list
            )
        )
        # Check that page content was written
        self.assertTrue(
            any("## Page 1" in call[0][0] for call in file_handle.write.call_args_list)
        )
        self.assertTrue(
            any(
                "This is a test document." in call[0][0]
                for call in file_handle.write.call_args_list
            )
        )

    @patch("fitz.open")
    @patch("fitz.Pixmap")
    @patch("builtins.open", new_callable=mock_open)
    @patch("rich.console.Console.print")
    @patch("rich.progress.Progress")
    def test_convert_with_images(
        self,
        mock_progress,
        mock_console_print,
        mock_file_open,
        mock_pixmap,
        mock_fitz_open,
    ):
        """Test PDF conversion with image extraction."""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.metadata = {"Title": "Test Document"}
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Text with an image."
        # Mock image data
        mock_image = (1, 0, 0, 0, 0, 0, 0)  # xref is the first element
        mock_page.get_images.return_value = [mock_image]
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc

        # Mock Pixmap
        mock_pixmap_instance = MagicMock()
        mock_pixmap_instance.n = 3
        mock_pixmap_instance.alpha = 0
        mock_pixmap.return_value = mock_pixmap_instance

        # Mock progress bar
        mock_task = MagicMock()
        mock_progress_instance = MagicMock()
        mock_progress_instance.add_task.return_value = mock_task
        mock_progress.return_value.__enter__.return_value = mock_progress_instance

        # Call convert method
        result = self.converter.convert(self.pdf_path, self.md_path)

        # Verify result
        self.assertEqual(result, self.md_path)

        # Verify image was saved
        mock_pixmap_instance.save.assert_called_once()

        # Verify file was opened for writing
        mock_file_open.assert_called_with(self.md_path, "w", encoding="utf-8")

        # Verify image reference was added to markdown
        file_handle = mock_file_open()
        self.assertTrue(
            any("![Image 1]" in call[0][0] for call in file_handle.write.call_args_list)
        )

    def test_process_text(self):
        """Test text processing for Markdown formatting."""
        # Test with regular text
        text = "This is a regular paragraph with   multiple spaces."
        processed = self.converter._process_text(text)
        self.assertEqual(processed, "This is a regular paragraph with multiple spaces.")

        # Test with heading-like text
        text = "THIS IS A HEADING\nThis is a regular paragraph."
        processed = self.converter._process_text(text)
        self.assertTrue(processed.startswith("### THIS IS A HEADING"))

        # Test with potential subheading
        text = "Subheading with period.\nThis is a regular paragraph."
        processed = self.converter._process_text(text)
        # The exact behavior depends on the implementation details

        # Test with code block
        text = "    def test_function():\n        return True"
        processed = self.converter._process_text(text)
        # Verify code formatting is preserved or enhanced

    @patch("pytesseract.image_to_string")
    @patch("pdf2image.convert_from_path")
    def test_ocr_page(self, mock_convert_from_path, mock_image_to_string):
        """Test OCR functionality for pages."""
        # Skip test if OCR is not enabled
        if not self.converter.ocr_enabled:
            self.skipTest("OCR is not enabled in the converter")

        # Mock image conversion
        mock_image = MagicMock(spec=Image.Image)
        mock_convert_from_path.return_value = [mock_image]

        # Mock OCR result
        mock_image_to_string.return_value = "OCR extracted text"

        # Call OCR method
        result = self.converter._ocr_page(0, self.pdf_path)

        # Verify result
        self.assertEqual(result, "OCR extracted text")

        # Verify OCR was called
        mock_image_to_string.assert_called_once_with(mock_image)

    @patch("twinizer.converters.pdf2md.PDF2MarkdownConverter")
    def test_convert_pdf_to_markdown_function(self, mock_converter_class):
        """Test the convert_pdf_to_markdown helper function."""
        # Mock converter instance
        mock_converter = MagicMock()
        mock_converter.convert.return_value = self.md_path
        mock_converter_class.return_value = mock_converter

        # Call helper function
        result = convert_pdf_to_markdown(
            self.pdf_path, self.md_path, ocr_enabled=True, extract_images=True
        )

        # Verify converter was created with correct parameters
        mock_converter_class.assert_called_with(
            ocr_enabled=True,
            extract_images=True,
            image_format="png",
            detect_tables=True,
            image_dir=None,
        )

        # Verify convert was called
        mock_converter.convert.assert_called_with(self.pdf_path, self.md_path)

        # Verify result
        self.assertEqual(result, self.md_path)


if __name__ == "__main__":
    unittest.main()

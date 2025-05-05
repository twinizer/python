"""
OCR functions for PDF content extraction.

This module provides OCR functionality to extract text from PDF images.
"""

import os
import tempfile

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from rich.console import Console

console = Console()


def perform_ocr(pdf_path, page_num):
    """
    Perform OCR on a PDF page.

    Args:
        pdf_path: Path to the PDF file
        page_num: Page number to OCR (0-based)

    Returns:
        OCR text result
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert the PDF page to an image
            console.print(f"[cyan]Running OCR on page {page_num + 1}...[/cyan]")

            # Convert the page to an image
            images = convert_from_path(
                pdf_path, first_page=page_num + 1, last_page=page_num + 1
            )

            if not images:
                console.print(
                    "[yellow]Warning: Could not convert PDF page to image[/yellow]"
                )
                return ""

            # Save the image to a temporary file
            image_path = os.path.join(temp_dir, f"page_{page_num}.png")
            images[0].save(image_path, "PNG")

            # Perform OCR with preprocessing
            ocr_text = extract_text_from_image(image_path)

            return ocr_text

    except Exception as e:
        console.print(f"[yellow]Warning: OCR failed: {e}[/yellow]")
        return ""


def extract_text_from_image(image_path):
    """
    Extract text from an image using OCR with preprocessing.

    Args:
        image_path: Path to the image file

    Returns:
        Extracted text
    """
    try:
        # Open the image
        image = Image.open(image_path)

        # Preprocess the image to improve OCR results
        processed_image = preprocess_image(image)

        # Perform OCR
        ocr_text = pytesseract.image_to_string(processed_image)

        # Post-process the OCR text
        ocr_text = post_process_ocr_text(ocr_text)

        return ocr_text

    except Exception as e:
        console.print(f"[yellow]Warning: Image OCR failed: {e}[/yellow]")
        return ""


def preprocess_image(image):
    """
    Preprocess an image to improve OCR results.

    Args:
        image: PIL Image object

    Returns:
        Processed PIL Image object
    """
    # Convert to grayscale
    if image.mode != "L":
        image = image.convert("L")

    # In a real implementation, we would apply more sophisticated preprocessing:
    # - Binarization (Otsu's method)
    # - Noise reduction
    # - Deskewing
    # - Contrast enhancement

    return image


def post_process_ocr_text(text):
    """
    Post-process OCR text to clean up common issues.

    Args:
        text: Raw OCR text

    Returns:
        Processed text
    """
    if not text:
        return text

    # Remove excessive newlines
    text = "\n".join([line for line in text.splitlines() if line.strip()])

    # Fix common OCR errors
    replacements = {
        "l": "1",  # Common OCR confusion between lowercase l and number 1
        "0": "O",  # Number 0 and letter O confusion
        "|": "I",  # Vertical bar and capital I confusion
        # Add more common substitutions as needed
    }

    # In practice, we would use more sophisticated techniques
    # like dictionaries and context-aware correction

    # Process line by line to preserve structure
    processed_lines = []
    for line in text.splitlines():
        processed_lines.append(line)

    return "\n".join(processed_lines)


def tesseract_available():
    """
    Check if Tesseract OCR is available on the system.

    Returns:
        Boolean indicating if Tesseract is available
    """
    try:
        import subprocess

        # Try to run tesseract with version flag
        result = subprocess.run(
            ["tesseract", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
        )
        return result.returncode == 0
    except Exception:
        return False

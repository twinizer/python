"""
PDF text and image extraction functions.

This module provides functions to extract text, images, and metadata from PDF documents.
"""

import os

import fitz  # PyMuPDF
from rich.console import Console

console = Console()


def extract_text(page):
    """
    Extract text from a PDF page.

    Args:
        page: PyMuPDF page object

    Returns:
        Extracted text
    """
    try:
        # Extract text using PyMuPDF
        text = page.get_text("text")
        return text
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to extract text: {e}[/yellow]")
        return ""


def extract_metadata(pdf_path):
    """
    Extract metadata from a PDF document.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary of metadata
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        # Filter out empty metadata
        return {
            k: v
            for k, v in metadata.items()
            if v and k.lower() not in ["format", "encryption"]
        }
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to extract metadata: {e}[/yellow]")
        return {}


def extract_images(doc, page, base_filename, image_dir, image_format, page_num):
    """
    Extract images from a PDF page.

    Args:
        doc: PyMuPDF document object
        page: PyMuPDF page object
        base_filename: Base filename for saved images
        image_dir: Directory to save images
        image_format: Format to save images (png, jpg, etc.)
        page_num: Page number

    Returns:
        List of dictionaries with image information
    """
    images = []

    try:
        # Get all images on the page
        img_list = page.get_images(full=True)

        for img_index, img in enumerate(img_list):
            # Get the image reference
            xref = img[0]

            # Generate a unique filename
            image_count = page_num * 100 + img_index + 1
            image_filename = f"{base_filename}_image_{image_count}.{image_format}"
            image_path = os.path.join(image_dir, image_filename)

            # Extract and save the image
            try:
                # Get the image
                pix = fitz.Pixmap(doc, xref)

                # Convert CMYK to RGB if needed
                if pix.n - pix.alpha > 3:  # CMYK
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                # Save the image
                pix.save(image_path)

                # Get image size
                width, height = pix.width, pix.height

                # Add image information to the list
                images.append(
                    {
                        "filename": image_filename,
                        "path": image_path,
                        "width": width,
                        "height": height,
                        "index": image_count,
                    }
                )

            except Exception as e:
                console.print(
                    f"[yellow]Warning: Failed to extract image {img_index}: {e}[/yellow]"
                )

    except Exception as e:
        console.print(f"[yellow]Warning: Failed to process images: {e}[/yellow]")

    return images


def detect_tables(page):
    """
    Detect tables on a PDF page.

    Args:
        page: PyMuPDF page object

    Returns:
        List of table boundaries
    """
    # This is a placeholder. In a real implementation, this would use more
    # sophisticated methods to detect tables, possibly using machine learning.

    # Simple approach: Look for grid-like structures of lines
    tables = []

    # Get all lines on the page
    paths = page.get_drawings()

    # Find horizontal and vertical lines
    h_lines = []
    v_lines = []

    for path in paths:
        if "items" in path:
            for item in path["items"]:
                if item[0] == "l":  # Line
                    x0, y0, x1, y1 = item[1]
                    # Check if horizontal or vertical
                    if abs(y1 - y0) < 1:  # Horizontal
                        h_lines.append((x0, y0, x1, y1))
                    elif abs(x1 - x0) < 1:  # Vertical
                        v_lines.append((x0, y0, x1, y1))

    # This is a very simplified approach that won't work well for complex tables
    # A real implementation would need more sophisticated algorithms

    return tables


def extract_structured_content(page):
    """
    Extract structured content from a PDF page.

    Args:
        page: PyMuPDF page object

    Returns:
        Dictionary of structured content
    """
    # This is a placeholder. In a real implementation, this would extract
    # structured content like headings, paragraphs, lists, etc.

    structured_content = {
        "headings": [],
        "paragraphs": [],
        "lists": [],
        "tables": detect_tables(page),
    }

    # Get text blocks
    blocks = page.get_text("blocks")

    for block in blocks:
        # Extract text and position
        x0, y0, x1, y1, text, block_type, block_no = block

        # Simple heuristic: heading if text is short and large font
        if len(text) < 100 and (x1 - x0) > 100 and (y1 - y0) < 30:
            structured_content["headings"].append(
                {"text": text, "position": (x0, y0, x1, y1)}
            )
        # Paragraph otherwise
        else:
            structured_content["paragraphs"].append(
                {"text": text, "position": (x0, y0, x1, y1)}
            )

    return structured_content

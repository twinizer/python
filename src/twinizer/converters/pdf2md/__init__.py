"""
PDF to Markdown converter package.

This package provides functionality to convert PDF documents to Markdown format,
preserving text, structure, images, and tables.
"""

from .extractor import extract_text, extract_images, extract_metadata
from .formatter import process_text, create_markdown
from .ocr import perform_ocr


def convert_pdf_to_markdown(pdf_path, output_path=None, **kwargs):
    """
    Convert a PDF file to Markdown format.

    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the Markdown output, if None uses the same name with .md extension
        **kwargs: Additional options for the converter

    Returns:
        Path to the output Markdown file
    """
    from pathlib import Path
    import os
    from rich.console import Console

    console = Console()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + ".md"

    # Configure options
    options = {
        'ocr_enabled': kwargs.get('ocr_enabled', False),
        'extract_images': kwargs.get('extract_images', True),
        'image_format': kwargs.get('image_format', 'png'),
        'detect_tables': kwargs.get('detect_tables', True),
        'image_dir': kwargs.get('image_dir', os.path.dirname(output_path))
    }

    console.print(f"Converting [cyan]{pdf_path}[/cyan] to [green]{output_path}[/green]")

    # Create image directory if needed
    if options['extract_images']:
        os.makedirs(options['image_dir'], exist_ok=True)

    # Extract metadata
    metadata = extract_metadata(pdf_path)

    # Create base filename for image references
    base_filename = os.path.splitext(os.path.basename(output_path))[0]

    # Extract and process page content
    pages_content = []

    # Process each page
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc):
        # Extract text
        text = extract_text(page)

        # Process text for Markdown
        if text.strip():
            processed_text = process_text(text)
        else:
            processed_text = ""

        # Extract images if enabled
        images = []
        if options['extract_images']:
            images = extract_images(
                doc,
                page,
                base_filename,
                options['image_dir'],
                options['image_format'],
                page_num
            )

        # Perform OCR if enabled and text is minimal
        ocr_text = ""
        if options['ocr_enabled'] and not text.strip():
            ocr_text = perform_ocr(pdf_path, page_num)

        # Add all content for this page
        page_content = {
            'page_num': page_num + 1,
            'text': processed_text,
            'images': images,
            'ocr_text': ocr_text
        }

        pages_content.append(page_content)

    # Create markdown
    markdown_text = create_markdown(metadata, pages_content)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)

    console.print(f"[green]Markdown saved to:[/green] {output_path}")
    return output_path
"""
pdf2md.py
"""

"""
PDF to Markdown converter module.

This module provides functionality to convert PDF documents to Markdown format,
preserving text, structure, images, and tables.
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class PDF2MarkdownConverter:
    """
    Converter class for PDF to Markdown transformation.

    Uses a combination of PyMuPDF for text extraction, pdf2image for image conversion,
    and Tesseract OCR for text in images.
    """

    def __init__(
        self,
        ocr_enabled: bool = False,
        extract_images: bool = True,
        image_format: str = "png",
        detect_tables: bool = True,
        image_dir: Optional[str] = None,
    ):
        """
        Initialize the converter with the given options.

        Args:
            ocr_enabled: Whether to use OCR for text in images
            extract_images: Whether to extract and save images
            image_format: Format to save extracted images (png, jpg, etc.)
            detect_tables: Whether to attempt table detection
            image_dir: Directory to save images, defaults to same as output
        """
        self.ocr_enabled = ocr_enabled
        self.extract_images = extract_images
        self.image_format = image_format
        self.detect_tables = detect_tables
        self.image_dir = image_dir

    def convert(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert a PDF file to Markdown.

        Args:
            pdf_path: Path to the PDF file
            output_path: Path to save the Markdown output, if None returns as string

        Returns:
            Markdown content as string if output_path is None, else path to the output file
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if output_path is None:
            output_path = os.path.splitext(pdf_path)[0] + ".md"

        if self.image_dir is None:
            self.image_dir = os.path.dirname(output_path)
            os.makedirs(self.image_dir, exist_ok=True)

        # Get base filename for image references
        base_filename = os.path.splitext(os.path.basename(output_path))[0]

        console.print(
            f"Converting [cyan]{pdf_path}[/cyan] to [green]{output_path}[/green]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Open the PDF file
            task = progress.add_task("[green]Opening PDF document...", total=None)
            doc = fitz.open(pdf_path)
            num_pages = len(doc)
            progress.update(
                task,
                completed=True,
                description=f"[green]PDF opened: {num_pages} pages",
            )

            # Extract metadata
            task = progress.add_task("[green]Extracting metadata...", total=None)
            metadata = doc.metadata
            progress.update(
                task, completed=True, description="[green]Metadata extracted"
            )

            # Process each page
            task = progress.add_task("[green]Processing pages...", total=num_pages)
            markdown_content = []

            # Add metadata as YAML frontmatter
            if metadata:
                markdown_content.append("---")
                for key, value in metadata.items():
                    if value and key.lower() not in ["format", "encryption"]:
                        markdown_content.append(f"{key}: {value}")
                markdown_content.append("---\n")

            image_count = 0
            for page_num, page in enumerate(doc):
                page_content = []

                # Extract text
                text = page.get_text("text")
                if text.strip():
                    # Process text for Markdown
                    text = self._process_text(text)
                    page_content.append(text)

                # Extract images if enabled
                if self.extract_images:
                    images = page.get_images(full=True)
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        image_count += 1
                        image_filename = (
                            f"{base_filename}_image_{image_count}.{self.image_format}"
                        )
                        image_path = os.path.join(self.image_dir, image_filename)

                        # Extract and save the image
                        try:
                            pix = fitz.Pixmap(doc, xref)
                            if pix.n - pix.alpha > 3:  # CMYK
                                pix = fitz.Pixmap(fitz.csRGB, pix)
                            pix.save(image_path)

                            # Add image reference to markdown
                            page_content.append(
                                f"\n![Image {image_count}]({image_filename})\n"
                            )
                        except Exception as e:
                            console.print(
                                f"[yellow]Warning: Failed to extract image: {e}[/yellow]"
                            )

                # OCR if enabled and text is minimal
                if self.ocr_enabled and not text.strip():
                    ocr_text = self._ocr_page(page_num, pdf_path)
                    if ocr_text:
                        page_content.append(ocr_text)

                # Add page content to markdown
                if page_content:
                    # Add page header
                    markdown_content.append(f"\n## Page {page_num + 1}\n")
                    markdown_content.extend(page_content)

                progress.update(
                    task,
                    advance=1,
                    description=f"[green]Processing page {page_num + 1}/{num_pages}",
                )

            # Write output
            markdown_text = "\n".join(markdown_content)

            task = progress.add_task("[green]Writing Markdown output...", total=None)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
            progress.update(
                task,
                completed=True,
                description=f"[green]Markdown saved to {output_path}",
            )

        return output_path

    def _process_text(self, text: str) -> str:
        """
        Process extracted text for Markdown formatting.

        Args:
            text: Raw text from PDF

        Returns:
            Processed text with Markdown formatting
        """
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Identify and format headings
        lines = text.split("\n")
        processed_lines = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                processed_lines.append("")
                continue

            # Check if this line looks like a heading
            if len(line) < 100 and line.isupper():
                processed_lines.append(f"### {line}")
            elif (
                len(line) < 100
                and line[0].isupper()
                and line[-1] in [".", ":", "?", "!"]
            ):
                # Check if the next line is blank or very short
                is_heading = False
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if not next_line or len(next_line) < 10:
                        is_heading = True

                if is_heading:
                    processed_lines.append(f"#### {line}")
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)

        return "\n".join(processed_lines)

    def _ocr_page(self, page_num: int, pdf_path: str) -> str:
        """
        Perform OCR on a page using Tesseract.

        Args:
            page_num: Page number to OCR
            pdf_path: Path to the PDF file

        Returns:
            OCR text result
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert PDF page to image
            images = convert_from_path(
                pdf_path, first_page=page_num + 1, last_page=page_num + 1
            )
            if not images:
                return ""

            image_path = os.path.join(temp_dir, f"page_{page_num}.png")
            images[0].save(image_path, "PNG")

            # Perform OCR
            try:
                ocr_text = pytesseract.image_to_string(Image.open(image_path))
                return ocr_text
            except Exception as e:
                console.print(f"[yellow]Warning: OCR failed: {e}[/yellow]")
                return ""


def convert_pdf_to_markdown(
    pdf_path: str, output_path: Optional[str] = None, **kwargs
) -> str:
    """
    Convert a PDF file to Markdown format.

    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the Markdown output, if None uses the same name with .md extension
        **kwargs: Additional options for the converter

    Returns:
        Path to the output Markdown file
    """
    converter = PDF2MarkdownConverter(**kwargs)
    return converter.convert(pdf_path, output_path)

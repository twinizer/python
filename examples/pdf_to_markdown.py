#!/usr/bin/env python3
"""
Example script demonstrating PDF to Markdown conversion.

This example shows how to use the PDF to Markdown converter to extract
text and images from PDF documents and convert them to Markdown format.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import twinizer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twinizer.converters.pdf2md import PDFToMarkdownConverter


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--images-dir", help="Directory to save extracted images")
    parser.add_argument("--ocr", action="store_true", help="Use OCR for text extraction")
    parser.add_argument("--extract-images", action="store_true", help="Extract images from PDF")
    parser.add_argument("--toc", action="store_true", help="Generate table of contents")
    
    args = parser.parse_args()
    
    # Check if the PDF exists
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF not found: {args.pdf_path}")
        return 1
    
    try:
        # Create converter
        converter = PDFToMarkdownConverter(
            use_ocr=args.ocr,
            extract_images=args.extract_images,
            images_dir=args.images_dir
        )
        
        # Convert PDF to Markdown
        print(f"Converting {args.pdf_path} to Markdown...")
        markdown = converter.convert(args.pdf_path, generate_toc=args.toc)
        
        # Save or display result
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(markdown)
            print(f"Markdown saved to: {args.output}")
            
            if args.extract_images:
                images_dir = args.images_dir or os.path.splitext(args.output)[0] + "_images"
                print(f"Images saved to: {images_dir}")
        else:
            print("\nMarkdown output:")
            print(markdown[:2000] + "..." if len(markdown) > 2000 else markdown)
        
        return 0
    
    except ImportError as e:
        print(f"Error: Missing dependencies: {e}")
        print("Please install the required dependencies:")
        print("  pip install PyPDF2 pytesseract pillow")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

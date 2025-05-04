#!/usr/bin/env python3
"""
Example script demonstrating image to ASCII art conversion.

This example shows how to use the AsciiArtConverter class to convert
an image to ASCII art in different formats.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import twinizer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from twinizer.converters.image.ascii import AsciiArtConverter


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Convert an image to ASCII art")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("--width", type=int, default=80, help="Width of ASCII art in characters")
    parser.add_argument("--height", type=int, help="Height of ASCII art in characters")
    parser.add_argument("--format", choices=["text", "html", "ansi"], default="text", 
                       help="Output format")
    parser.add_argument("--charset", choices=["standard", "simple", "blocks", "extended"], 
                       default="standard", help="Character set to use")
    parser.add_argument("--invert", action="store_true", help="Invert brightness")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    # Check if the image exists
    if not os.path.exists(args.image_path):
        print(f"Error: Image not found: {args.image_path}")
        return 1
    
    try:
        # Create converter
        converter = AsciiArtConverter()
        
        # Convert image to ASCII art
        print(f"Converting {args.image_path} to ASCII art...")
        result = converter.convert(
            image_path=args.image_path,
            width=args.width,
            height=args.height,
            output_format=args.format,
            charset=args.charset,
            invert=args.invert,
            output_path=args.output
        )
        
        # Display result
        if args.output:
            print(f"ASCII art saved to: {args.output}")
        else:
            print("\nResult:")
            print(result)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

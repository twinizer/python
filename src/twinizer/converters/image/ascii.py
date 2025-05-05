"""
Enhanced ASCII art converter module.

This module provides comprehensive functionality to convert images to ASCII art
with support for various output formats, styles, and customization options.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image


class AsciiArtConverter:
    """
    Converter class for generating ASCII art from images with various options.
    """

    # Predefined character sets from darkest to lightest
    CHAR_SETS = {
        "standard": "@%#*+=-:. ",
        "complex": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
        "simple": "#. ",
        "blocks": "█▓▒░ ",
        "binary": "10 ",
        "ascii_only": "@%#*+=-:. ",
        "high_contrast": "@% ",
    }

    def __init__(self, char_set: str = "standard", invert: bool = False):
        """
        Initialize the ASCII art converter.

        Args:
            char_set: Name of predefined character set or custom string (darkest to lightest)
            invert: Whether to invert the character set (light to dark instead of dark to light)
        """
        if char_set in self.CHAR_SETS:
            self.chars = self.CHAR_SETS[char_set]
        else:
            self.chars = char_set

        if invert:
            self.chars = self.chars[::-1]

    def convert(
        self,
        image_path: str,
        width: int = 80,
        height: Optional[int] = None,
        output_format: str = "text",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Convert an image to ASCII art.

        Args:
            image_path: Path to the image file
            width: Width of the ASCII art in characters
            height: Height of the ASCII art in characters (calculated from aspect ratio if None)
            output_format: Format of the output ('text', 'html', 'colored_html', 'ansi')
            output_path: Path to save the output, if None returns as string

        Returns:
            ASCII art as a string or path to the output file
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Load the image
        img = Image.open(image_path)

        # Generate ASCII art based on the output format
        if output_format == "text":
            ascii_art = self._generate_text_ascii(img, width, height)
        elif output_format == "html":
            ascii_art = self._generate_html_ascii(img, width, height, use_color=False)
        elif output_format == "colored_html":
            ascii_art = self._generate_html_ascii(img, width, height, use_color=True)
        elif output_format == "ansi":
            ascii_art = self._generate_ansi_ascii(img, width, height)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        # Save to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(ascii_art)
            return output_path

        return ascii_art

    def _generate_text_ascii(
        self, img: Image.Image, width: int, height: Optional[int] = None
    ) -> str:
        """
        Generate plain text ASCII art.

        Args:
            img: PIL Image object
            width: Width in characters
            height: Height in characters (calculated from aspect ratio if None)

        Returns:
            ASCII art as plain text
        """
        # Process image to grayscale array
        gray_img, width, height = self._prepare_image(img, width, height)

        # Convert to numpy array for efficient processing
        pixels = np.array(gray_img)

        # Map pixel values to ASCII characters using NumPy vectorization
        indices = np.floor((pixels / 255) * (len(self.chars) - 1)).astype(int)
        char_array = np.array(list(self.chars))[indices]

        # Convert to string
        lines = ["".join(row) for row in char_array]
        return "\n".join(lines)

    def _generate_html_ascii(
        self,
        img: Image.Image,
        width: int,
        height: Optional[int] = None,
        use_color: bool = False,
    ) -> str:
        """
        Generate HTML-formatted ASCII art with optional color.

        Args:
            img: PIL Image object
            width: Width in characters
            height: Height in characters (calculated from aspect ratio if None)
            use_color: Whether to use color in the HTML output

        Returns:
            ASCII art as HTML string
        """
        # Process image
        if use_color:
            rgb_img, width, height = self._prepare_image(img, width, height, mode="RGB")
            pixels = np.array(rgb_img)
        else:
            gray_img, width, height = self._prepare_image(img, width, height)
            pixels = np.array(gray_img)

        # Generate HTML
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<style>",
            "pre { font-family: monospace; line-height: 1; background-color: #000; }",
            "</style>",
            "</head>",
            "<body>",
            "<pre>",
        ]

        if use_color:
            for row in pixels:
                line = []
                for pixel in row:
                    r, g, b = pixel
                    brightness = (r + g + b) / 3
                    char_index = int((brightness / 255) * (len(self.chars) - 1))
                    char = self.chars[char_index]
                    line.append(f'<span style="color: rgb({r},{g},{b});">{char}</span>')
                html.append("".join(line))
        else:
            # For grayscale, we can use vectorized operations
            indices = np.floor((pixels / 255) * (len(self.chars) - 1)).astype(int)
            char_array = np.array(list(self.chars))[indices]

            for row in char_array:
                html.append("".join(row))

        html.append("</pre>")
        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def _generate_ansi_ascii(
        self, img: Image.Image, width: int, height: Optional[int] = None
    ) -> str:
        """
        Generate ASCII art with ANSI color codes for terminal display.

        Args:
            img: PIL Image object
            width: Width in characters
            height: Height in characters (calculated from aspect ratio if None)

        Returns:
            ASCII art with ANSI color codes
        """
        # Process image to RGB
        rgb_img, width, height = self._prepare_image(img, width, height, mode="RGB")
        pixels = np.array(rgb_img)

        # Generate ANSI colored text
        lines = []
        for row in pixels:
            line = []
            for pixel in row:
                r, g, b = pixel
                brightness = (r + g + b) / 3
                char_index = int((brightness / 255) * (len(self.chars) - 1))
                char = self.chars[char_index]

                # Simplified 8-bit color approximation (256 colors)
                ansi_r = int(r / 255 * 5)
                ansi_g = int(g / 255 * 5)
                ansi_b = int(b / 255 * 5)
                ansi_code = 16 + (36 * ansi_r) + (6 * ansi_g) + ansi_b

                line.append(f"\033[38;5;{ansi_code}m{char}\033[0m")
            lines.append("".join(line))

        return "\n".join(lines)

    def _prepare_image(
        self,
        img: Image.Image,
        width: int,
        height: Optional[int] = None,
        mode: str = "L",
    ) -> Tuple[Image.Image, int, int]:
        """
        Prepare an image for ASCII conversion by resizing and converting to appropriate mode.

        Args:
            img: PIL Image object
            width: Width in characters
            height: Height in characters (calculated from aspect ratio if None)
            mode: Image mode ('L' for grayscale, 'RGB' for color)

        Returns:
            Tuple of (processed_image, width, height)
        """
        # Convert to appropriate mode
        if img.mode != mode:
            img = img.convert(mode)

        # Calculate height to maintain aspect ratio if not specified
        if height is None:
            aspect_ratio = img.height / img.width
            height = int(
                width * aspect_ratio * 0.5
            )  # * 0.5 to account for character aspect ratio

        # Resize the image using high-quality method
        img = img.resize((width, height), Image.LANCZOS)

        return img, width, height


def convert_image_to_ascii(
    image_path: str,
    output_path: Optional[str] = None,
    width: int = 80,
    height: Optional[int] = None,
    char_set: str = "standard",
    invert: bool = False,
    output_format: str = "text",
) -> str:
    """
    Convenience function to convert an image to ASCII art.

    Args:
        image_path: Path to the image file
        output_path: Path to save the output, if None returns as string
        width: Width of the ASCII art in characters
        height: Height of the ASCII art in characters (calculated from aspect ratio if None)
        char_set: Name of predefined character set or custom string (darkest to lightest)
        invert: Whether to invert the character set (light to dark instead of dark to light)
        output_format: Format of the output ('text', 'html', 'colored_html', 'ansi')

    Returns:
        ASCII art as a string or path to the output file
    """
    converter = AsciiArtConverter(char_set=char_set, invert=invert)
    return converter.convert(
        image_path=image_path,
        width=width,
        height=height,
        output_format=output_format,
        output_path=output_path,
    )


def available_char_sets() -> Dict[str, str]:
    """
    Get the available predefined character sets.

    Returns:
        Dictionary of character set names and their values
    """
    return AsciiArtConverter.CHAR_SETS


def image_to_ascii_art_preview(
    image_path: str, width: int = 40, char_set: str = "standard"
) -> str:
    """
    Generate a quick ASCII art preview of an image.

    Args:
        image_path: Path to the image file
        width: Width of the ASCII art in characters
        char_set: Name of predefined character set or custom string

    Returns:
        ASCII art preview as a string
    """
    converter = AsciiArtConverter(char_set=char_set)
    return converter.convert(image_path, width=width, output_format="text")

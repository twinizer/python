"""
PDF text formatting functions.

This module provides functions to format extracted PDF text into Markdown.
"""

import re

from rich.console import Console

console = Console()


def process_text(text):
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

        # Check if line looks like a heading
        is_heading, heading_level = _detect_heading(line, i, lines)

        if is_heading:
            processed_lines.append(f"{'#' * heading_level} {line}")
        else:
            processed_lines.append(line)

    # Format lists
    processed_text = "\n".join(processed_lines)
    processed_text = _format_lists(processed_text)

    # Format code blocks
    processed_text = _format_code_blocks(processed_text)

    # Format tables
    processed_text = _format_tables(processed_text)

    return processed_text


def _detect_heading(line, line_index, all_lines):
    """
    Detect if a line is a heading and determine its level.

    Args:
        line: Line to check
        line_index: Index of the line
        all_lines: All lines in the text

    Returns:
        Tuple of (is_heading, heading_level)
    """
    # Check if line is all caps and not too long
    if len(line) < 100 and line.isupper():
        return True, 2  # Level 2 heading (##)

    # Check if line starts with a capital letter, ends with punctuation, and is not too long
    if (
        len(line) < 100
        and line[0].isupper()
        and line[-1] in [".", ":", "?", "!"]
        and not line.endswith("etc.")
        and not ":" in line[:-1]
    ):
        # Check if the next line is blank or very short
        is_heading = False
        if line_index + 1 < len(all_lines):
            next_line = all_lines[line_index + 1].strip()
            if not next_line or len(next_line) < 10:
                is_heading = True

        # Also check if previous line is blank
        if line_index > 0:
            prev_line = all_lines[line_index - 1].strip()
            if not prev_line:
                is_heading = True

        if is_heading:
            # Determine heading level based on some heuristics
            if len(line) < 30:
                return True, 3  # Level 3 heading (###)
            else:
                return True, 4  # Level 4 heading (####)

    # Check for numbered headings like "1. Introduction"
    if re.match(r"^\d+\.(\d+\.)*\s+[A-Z]", line) and len(line) < 100:
        # Level depends on the number of dots
        dots = line.split(" ")[0].count(".")
        return True, dots + 2

    return False, 0


def _format_lists(text):
    """
    Format lists in the text.

    Args:
        text: Text to process

    Returns:
        Text with formatted lists
    """
    lines = text.split("\n")
    processed_lines = []
    in_list = False

    for line in lines:
        # Check for bullet lists (lines starting with - or • or *)
        if re.match(r"^\s*[\-\•\*]\s+", line):
            # Ensure there's a blank line before the list starts
            if not in_list and processed_lines and processed_lines[-1].strip():
                processed_lines.append("")

            # Format the list item
            line = re.sub(r"^\s*[\-\•\*]\s+", "- ", line)
            in_list = True

        # Check for numbered lists (lines starting with 1., 2., etc.)
        elif re.match(r"^\s*\d+\.\s+", line) and not re.match(
            r"^\s*\d+\.\d+\.\s+", line
        ):
            # Ensure there's a blank line before the list starts
            if not in_list and processed_lines and processed_lines[-1].strip():
                processed_lines.append("")

            in_list = True

        # End of list
        elif in_list and (not line.strip() or line.startswith("#")):
            if processed_lines and processed_lines[-1].strip():
                processed_lines.append("")
            in_list = False

        processed_lines.append(line)

    return "\n".join(processed_lines)


def _format_code_blocks(text):
    """
    Format code blocks in the text.

    Args:
        text: Text to process

    Returns:
        Text with formatted code blocks
    """
    lines = text.split("\n")
    processed_lines = []
    in_code_block = False
    potential_code_lines = 0

    for i, line in enumerate(lines):
        # Detect code blocks based on indentation and special characters
        is_code_line = (
            line.startswith("    ")
            and not line.strip().startswith("-")
            and not line.strip().startswith("*")
        )

        # Check if line contains code-like characters
        code_chars = [
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
            ";",
            "=",
            "+",
            "-",
            "*",
            "//",
            "/*",
            "*/",
        ]
        has_code_chars = any(char in line for char in code_chars)

        if is_code_line or (
            has_code_chars and not line.startswith("#") and len(line.strip()) > 0
        ):
            if not in_code_block:
                potential_code_lines += 1

                # If we have enough potential code lines, start a code block
                if potential_code_lines >= 2:
                    in_code_block = True
                    # Insert code block marker before the first code line
                    processed_lines.insert(
                        len(processed_lines) - potential_code_lines + 1, "```"
                    )
        else:
            if in_code_block:
                processed_lines.append("```")
                in_code_block = False
            potential_code_lines = 0

        processed_lines.append(line)

    # Close any open code block
    if in_code_block:
        processed_lines.append("```")

    return "\n".join(processed_lines)


def _format_tables(text):
    """
    Format tables in the text.

    Args:
        text: Text to process

    Returns:
        Text with formatted tables
    """
    lines = text.split("\n")
    processed_lines = []
    in_table = False
    table_lines = []

    for line in lines:
        # Check if line has multiple column-like separations
        columns = re.split(r"\s{3,}", line.strip())

        # If line has multiple columns and they are balanced
        if len(columns) >= 3 and all(len(col.strip()) > 0 for col in columns):
            if not in_table:
                in_table = True
                # Start collecting table lines
                table_lines = [line]
            else:
                table_lines.append(line)
        else:
            # End of table
            if in_table:
                # Process and add the table
                markdown_table = _convert_to_markdown_table(table_lines)
                processed_lines.append(markdown_table)
                in_table = False
                table_lines = []

            processed_lines.append(line)

    # Process any remaining table
    if in_table:
        markdown_table = _convert_to_markdown_table(table_lines)
        processed_lines.append(markdown_table)

    return "\n".join(processed_lines)


def _convert_to_markdown_table(table_lines):
    """
    Convert a list of table lines to a Markdown table.

    Args:
        table_lines: List of lines representing a table

    Returns:
        Markdown table representation
    """
    if not table_lines:
        return ""

    # Split each line into columns
    rows = []
    max_cols = 0

    for line in table_lines:
        # Split by multiple spaces
        columns = [col.strip() for col in re.split(r"\s{3,}", line.strip())]
        rows.append(columns)
        max_cols = max(max_cols, len(columns))

    # Ensure all rows have the same number of columns
    for row in rows:
        while len(row) < max_cols:
            row.append("")

    # Create Markdown table
    markdown_rows = []
    markdown_rows.append("| " + " | ".join(rows[0]) + " |")
    markdown_rows.append("| " + " | ".join(["---"] * max_cols) + " |")

    for row in rows[1:]:
        markdown_rows.append("| " + " | ".join(row) + " |")

    return "\n".join(markdown_rows)


def create_markdown(metadata, pages_content):
    """
    Create complete Markdown document from metadata and page content.

    Args:
        metadata: Dictionary of document metadata
        pages_content: List of dictionaries with page content

    Returns:
        Complete Markdown document
    """
    markdown_parts = []

    # Add metadata as YAML frontmatter
    if metadata:
        markdown_parts.append("---")
        for key, value in metadata.items():
            markdown_parts.append(f"{key}: {value}")
        markdown_parts.append("---\n")

    # Process each page
    for page in pages_content:
        page_num = page["page_num"]
        text = page["text"]
        images = page["images"]
        ocr_text = page["ocr_text"]

        # Add page header if there's more than one page
        if len(pages_content) > 1:
            markdown_parts.append(f"\n## Page {page_num}\n")

        # Add text content
        if text:
            markdown_parts.append(text)

        # Add OCR text if available
        if ocr_text:
            if text:  # Add separator if there's already text
                markdown_parts.append("\n")
            markdown_parts.append(ocr_text)

        # Add images
        for image in images:
            markdown_parts.append(f"\n![Image {image['index']}]({image['filename']})\n")

    return "\n".join(markdown_parts)

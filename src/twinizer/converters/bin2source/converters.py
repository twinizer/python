"""
Binary to source code converter module.

This module provides functionality to convert binary files to various source code
representations, including C arrays, Python byte arrays, and other formats.
"""

import binascii
import os
from typing import BinaryIO, Dict, List, Optional, Union


class BinaryConverter:
    """
    Base class for binary file converters.
    """

    def __init__(self, input_file: str):
        """
        Initialize the binary converter.

        Args:
            input_file: Path to the binary file to convert
        """
        self.input_file = input_file
        self._validate_input_file()

    def _validate_input_file(self):
        """Validate that the input file exists and is readable."""
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Binary file not found: {self.input_file}")
        if not os.path.isfile(self.input_file):
            raise ValueError(f"Not a file: {self.input_file}")
        if not os.access(self.input_file, os.R_OK):
            raise PermissionError(f"No permission to read file: {self.input_file}")

    def _read_binary_data(self) -> bytes:
        """Read binary data from the input file."""
        with open(self.input_file, "rb") as f:
            return f.read()

    def convert(self, output_file: Optional[str] = None, **kwargs) -> str:
        """
        Convert binary file to source code.

        Args:
            output_file: Path to the output file, if None returns as string
            **kwargs: Additional options for the converter

        Returns:
            Source code as a string or path to the output file
        """
        raise NotImplementedError("Subclasses must implement this method")


class CArrayConverter(BinaryConverter):
    """
    Converter for binary files to C arrays.
    """

    def convert(
        self,
        output_file: Optional[str] = None,
        variable_name: str = "binary_data",
        bytes_per_line: int = 16,
        const: bool = True,
        include_size: bool = True,
        include_header: bool = True,
    ) -> str:
        """
        Convert binary file to C array.

        Args:
            output_file: Path to the output file, if None returns as string
            variable_name: Name of the C array variable
            bytes_per_line: Number of bytes per line in the output
            const: Whether to declare the array as const
            include_size: Whether to include a size variable
            include_header: Whether to include a header comment

        Returns:
            C array source code as a string or path to the output file
        """
        data = self._read_binary_data()
        size = len(data)

        # Generate C array code
        lines = []

        # Add header comment
        if include_header:
            lines.append("/**")
            lines.append(
                f" * Binary data from file: {os.path.basename(self.input_file)}"
            )
            lines.append(f" * Size: {size} bytes")
            lines.append(" */")
            lines.append("")

        # Add array declaration
        const_keyword = "const " if const else ""
        lines.append(f"{const_keyword}unsigned char {variable_name}[{size}] = {{")

        # Add array data
        for i in range(0, size, bytes_per_line):
            chunk = data[i : i + bytes_per_line]
            hex_values = [f"0x{byte:02x}" for byte in chunk]
            if i + bytes_per_line < size:
                lines.append("    " + ", ".join(hex_values) + ",")
            else:
                lines.append("    " + ", ".join(hex_values))

        lines.append("};")

        # Add size variable
        if include_size:
            lines.append("")
            lines.append(f"{const_keyword}unsigned int {variable_name}_size = {size};")

        # Join lines
        c_code = "\n".join(lines)

        # Write to file or return as string
        if output_file:
            with open(output_file, "w") as f:
                f.write(c_code)
            return output_file
        else:
            return c_code


class PythonBytesConverter(BinaryConverter):
    """
    Converter for binary files to Python bytes or bytearray.
    """

    def convert(
        self,
        output_file: Optional[str] = None,
        variable_name: str = "binary_data",
        use_bytearray: bool = False,
        bytes_per_line: int = 16,
        include_size: bool = True,
        include_header: bool = True,
    ) -> str:
        """
        Convert binary file to Python bytes or bytearray.

        Args:
            output_file: Path to the output file, if None returns as string
            variable_name: Name of the Python variable
            use_bytearray: Whether to use bytearray instead of bytes
            bytes_per_line: Number of bytes per line in the output
            include_size: Whether to include a size variable
            include_header: Whether to include a header comment

        Returns:
            Python code as a string or path to the output file
        """
        data = self._read_binary_data()
        size = len(data)

        # Generate Python code
        lines = []

        # Add header comment
        if include_header:
            lines.append('"""')
            lines.append(f"Binary data from file: {os.path.basename(self.input_file)}")
            lines.append(f"Size: {size} bytes")
            lines.append('"""')
            lines.append("")

        # Add variable declaration
        data_type = "bytearray" if use_bytearray else "bytes"
        lines.append(f"{variable_name} = {data_type}([")

        # Add array data
        for i in range(0, size, bytes_per_line):
            chunk = data[i : i + bytes_per_line]
            hex_values = [f"0x{byte:02x}" for byte in chunk]
            if i + bytes_per_line < size:
                lines.append("    " + ", ".join(hex_values) + ",")
            else:
                lines.append("    " + ", ".join(hex_values))

        lines.append("])")

        # Add size variable
        if include_size:
            lines.append("")
            lines.append(f"{variable_name}_size = {size}")

        # Join lines
        python_code = "\n".join(lines)

        # Write to file or return as string
        if output_file:
            with open(output_file, "w") as f:
                f.write(python_code)
            return output_file
        else:
            return python_code


class HexDumpConverter(BinaryConverter):
    """
    Converter for binary files to hex dump format.
    """

    def convert(
        self,
        output_file: Optional[str] = None,
        bytes_per_line: int = 16,
        show_ascii: bool = True,
        show_offset: bool = True,
        offset_format: str = "hex",
    ) -> str:
        """
        Convert binary file to hex dump format.

        Args:
            output_file: Path to the output file, if None returns as string
            bytes_per_line: Number of bytes per line in the output
            show_ascii: Whether to show ASCII representation
            show_offset: Whether to show offset
            offset_format: Format of the offset ('hex' or 'dec')

        Returns:
            Hex dump as a string or path to the output file
        """
        data = self._read_binary_data()
        size = len(data)

        # Generate hex dump
        lines = []

        for i in range(0, size, bytes_per_line):
            chunk = data[i : i + bytes_per_line]

            # Add offset
            if show_offset:
                if offset_format == "hex":
                    offset = f"{i:08x}"
                else:
                    offset = f"{i:10d}"
                line = f"{offset}: "
            else:
                line = ""

            # Add hex values
            hex_values = [f"{byte:02x}" for byte in chunk]
            line += " ".join(hex_values)

            # Pad for alignment if the last line is shorter
            if len(chunk) < bytes_per_line:
                line += "   " * (bytes_per_line - len(chunk))

            # Add ASCII representation
            if show_ascii:
                ascii_repr = "".join(
                    [chr(byte) if 32 <= byte <= 126 else "." for byte in chunk]
                )
                line += "  |" + ascii_repr + "|"

            lines.append(line)

        # Join lines
        hex_dump = "\n".join(lines)

        # Write to file or return as string
        if output_file:
            with open(output_file, "w") as f:
                f.write(hex_dump)
            return output_file
        else:
            return hex_dump


def convert_binary_to_source(
    input_file: str,
    output_file: Optional[str] = None,
    format_type: str = "c_array",
    **kwargs,
) -> str:
    """
    Convert a binary file to source code.

    Args:
        input_file: Path to the binary file
        output_file: Path to the output file, if None returns as string
        format_type: Type of source code to generate ('c_array', 'python_bytes', 'hex_dump')
        **kwargs: Additional options for the converter

    Returns:
        Source code as a string or path to the output file
    """
    # Select converter based on format type
    if format_type == "c_array":
        converter = CArrayConverter(input_file)
    elif format_type == "python_bytes":
        converter = PythonBytesConverter(input_file)
    elif format_type == "hex_dump":
        converter = HexDumpConverter(input_file)
    else:
        raise ValueError(f"Unsupported format type: {format_type}")

    # Convert binary to source
    return converter.convert(output_file, **kwargs)


def available_formats() -> Dict[str, str]:
    """
    Get the available source code formats.

    Returns:
        Dictionary of format names and descriptions
    """
    return {
        "c_array": "C/C++ array of unsigned char",
        "python_bytes": "Python bytes or bytearray",
        "hex_dump": "Hexadecimal dump with optional ASCII representation",
    }

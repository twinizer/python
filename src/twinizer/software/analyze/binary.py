"""
Binary file analyzer module.

This module provides functionality to analyze binary files, including
executables, firmware images, and other binary formats.
"""

import os
import subprocess
from typing import Any, Dict, List, Optional

from rich.console import Console

console = Console()


class BinaryAnalyzer:
    """
    Analyzer for binary files.

    This class provides methods to analyze binary files, extract information,
    and identify patterns and structures.
    """

    def __init__(self, binary_path: str):
        """
        Initialize the analyzer with a binary file path.

        Args:
            binary_path: Path to the binary file
        """
        self.binary_path = binary_path

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the binary file and extract information.

        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(self.binary_path):
            raise FileNotFoundError(f"Binary file not found: {self.binary_path}")

        # Get file size
        file_size = os.path.getsize(self.binary_path)

        # Determine file type
        file_type = self._determine_file_type()

        # Extract basic information
        result = {
            "path": self.binary_path,
            "size": file_size,
            "format": file_type,
            "architecture": self._detect_architecture(),
            "strings": self._extract_strings(limit=10),
            "entropy": self._calculate_entropy(),
        }

        # Add format-specific information
        if file_type == "ELF":
            result.update(self._analyze_elf())
        elif file_type == "PE":
            result.update(self._analyze_pe())
        elif file_type == "HEX":
            result.update(self._analyze_hex())

        return result

    def _determine_file_type(self) -> str:
        """
        Determine the type of binary file.

        Returns:
            String describing the file type
        """
        # Check file extension first
        _, ext = os.path.splitext(self.binary_path)
        ext = ext.lower()

        if ext == ".elf":
            return "ELF"
        elif ext == ".exe" or ext == ".dll":
            return "PE"
        elif ext == ".hex":
            return "HEX"
        elif ext == ".bin":
            return "BIN"
        elif ext == ".so":
            return "ELF"  # Shared objects are ELF format

        # Check file signature
        with open(self.binary_path, "rb") as f:
            header = f.read(16)

        # Check for ELF signature
        if header[:4] == b"\x7fELF":
            return "ELF"
        # Check for PE signature
        elif header[:2] == b"MZ":
            return "PE"
        # Check for Intel HEX format (text-based)
        elif all(c < 128 for c in header) and header[0:1] == b":":
            return "HEX"

        # Default to raw binary
        return "BIN"

    def _detect_architecture(self) -> str:
        """
        Detect the architecture of the binary.

        Returns:
            String describing the architecture
        """
        # This is a simplified implementation
        file_type = self._determine_file_type()

        if file_type == "ELF":
            try:
                result = subprocess.run(
                    ["readelf", "-h", self.binary_path],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                output = result.stdout

                if "ARM" in output:
                    return "ARM"
                elif "X86-64" in output:
                    return "x86-64"
                elif "80386" in output:
                    return "x86"
                elif "RISC-V" in output:
                    return "RISC-V"
            except FileNotFoundError:
                pass

        # Default response if we can't determine
        return "Unknown"

    def _extract_strings(
        self, min_length: int = 4, limit: Optional[int] = None
    ) -> List[str]:
        """
        Extract printable strings from the binary.

        Args:
            min_length: Minimum string length to extract
            limit: Maximum number of strings to return

        Returns:
            List of extracted strings
        """
        strings = []

        try:
            result = subprocess.run(
                ["strings", "-n", str(min_length), self.binary_path],
                capture_output=True,
                text=True,
                check=False,
            )
            strings = result.stdout.splitlines()
        except FileNotFoundError:
            # Fallback if strings command is not available
            with open(self.binary_path, "rb") as f:
                content = f.read()

            current_string = ""
            for byte in content:
                if 32 <= byte <= 126:  # Printable ASCII
                    current_string += chr(byte)
                else:
                    if len(current_string) >= min_length:
                        strings.append(current_string)
                    current_string = ""

            if len(current_string) >= min_length:
                strings.append(current_string)

        # Limit the number of strings if requested
        if limit and len(strings) > limit:
            return strings[:limit]

        return strings

    def _calculate_entropy(self) -> float:
        """
        Calculate the entropy of the binary file.

        Returns:
            Entropy value between 0 and 8
        """
        # Simple entropy calculation
        try:
            import math

            with open(self.binary_path, "rb") as f:
                data = f.read(1024 * 1024)  # Read up to 1MB

            if not data:
                return 0.0

            # Count byte frequencies
            byte_counts = {}
            for byte in data:
                byte_counts[byte] = byte_counts.get(byte, 0) + 1

            # Calculate entropy
            entropy = 0.0
            for count in byte_counts.values():
                probability = count / len(data)
                entropy -= probability * math.log2(probability)

            return entropy
        except Exception:
            return 0.0

    def _analyze_elf(self) -> Dict[str, Any]:
        """
        Analyze ELF-specific information.

        Returns:
            Dictionary with ELF-specific analysis
        """
        result = {
            "sections": [],
            "symbols": [],
        }

        try:
            # Get sections
            sections_result = subprocess.run(
                ["readelf", "-S", self.binary_path],
                capture_output=True,
                text=True,
                check=False,
            )

            if sections_result.returncode == 0:
                # Simple parsing of section headers
                for line in sections_result.stdout.splitlines():
                    if "]" in line and "[" in line and "Name" not in line:
                        parts = line.split()
                        if len(parts) >= 7:
                            result["sections"].append(
                                {
                                    "name": parts[1],
                                    "type": parts[2],
                                    "addr": parts[3],
                                    "size": parts[5],
                                }
                            )
        except FileNotFoundError:
            pass

        return result

    def _analyze_pe(self) -> Dict[str, Any]:
        """
        Analyze PE-specific information.

        Returns:
            Dictionary with PE-specific analysis
        """
        # Simplified PE analysis
        return {
            "imports": [],
            "exports": [],
        }

    def _analyze_hex(self) -> Dict[str, Any]:
        """
        Analyze Intel HEX file information.

        Returns:
            Dictionary with HEX-specific analysis
        """
        # Simplified HEX analysis
        return {
            "address_range": {
                "start": 0,
                "end": 0,
            },
            "record_count": 0,
        }

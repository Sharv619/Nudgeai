"""
Code chunker module for NudgeAI codebase analysis
Chunks code into digestible segments for processing
"""

import re
from typing import List, Dict, Any
from data_ingestion.codebase.code_parser import CodeParser


class CodeChunker:
    """
    Chunks code files into digestible segments for processing and analysis
    """

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        """
        Initialize the code chunker

        Args:
            max_chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.parser = CodeParser()

    def chunk_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Chunk a code file into digestible segments

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            List of chunk dictionaries
        """
        ext = self._get_file_extension(file_path)

        if ext == ".py":
            return self._chunk_python_file(file_path, content)
        else:
            # Default chunking for other file types
            return self._chunk_generic_file(file_path, content)

    def _get_file_extension(self, file_path: str) -> str:
        """
        Get the file extension from a file path

        Args:
            file_path: Path to the file

        Returns:
            File extension
        """
        return "." + file_path.split(".")[-1]

    def _chunk_python_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Specialized chunking for Python files based on code structure

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            List of chunk dictionaries
        """
        chunks = []

        # Parse the file to identify logical units
        parsed = self.parser.parse_python(file_path, content)

        # Create chunks based on functions and classes
        pos = 0
        lines = content.split("\n")
        current_line = 0

        # First, try to chunk by logical units (functions, classes)
        logical_units = []

        # Add functions
        for func in parsed["functions"]:
            logical_units.append(
                {
                    "type": "function",
                    "name": func["name"],
                    "start_line": func["line_start"],
                    "end_line": func["line_end"],
                    "content": "\n".join(
                        lines[func["line_start"] - 1 : func["line_end"]]
                    ),
                }
            )

        # Add classes
        for cls in parsed["classes"]:
            logical_units.append(
                {
                    "type": "class",
                    "name": cls["name"],
                    "start_line": cls["line_start"],
                    "end_line": cls["line_end"],
                    "content": "\n".join(
                        lines[cls["line_start"] - 1 : cls["line_end"]]
                    ),
                }
            )

        # Sort by line number
        logical_units.sort(key=lambda x: x["start_line"])

        # Process logical units
        for unit in logical_units:
            if len(unit["content"]) <= self.max_chunk_size:
                chunks.append(
                    {
                        "file_path": file_path,
                        "type": unit["type"],
                        "name": unit["name"],
                        "content": unit["content"],
                        "start_line": unit["start_line"],
                        "end_line": unit["end_line"],
                        "size": len(unit["content"]),
                        "metadata": {
                            "language": "python",
                            "chunk_method": "logical_unit",
                        },
                    }
                )
            else:
                # If the logical unit is too big, split it further
                sub_chunks = self._create_sub_chunks(
                    unit["content"],
                    file_path,
                    unit["start_line"],
                    unit["type"],
                    unit["name"],
                )
                chunks.extend(sub_chunks)

        # If no logical units were found, fall back to generic chunking
        if not chunks:
            chunks = self._chunk_generic_file(file_path, content)

        return chunks

    def _chunk_generic_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Generic chunking for any type of file

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            List of chunk dictionaries
        """
        chunks = []

        # Split content into chunks based on size
        start = 0
        content_length = len(content)

        while start < content_length:
            end = min(start + self.max_chunk_size, content_length)

            # Try to break at a convenient boundary (end of line)
            if end < content_length:
                # Look for the next newline to avoid breaking mid-line
                next_newline = content.find("\n", end - self.overlap, end + 50)
                if next_newline != -1 and next_newline < end + 50:
                    end = next_newline + 1

            chunk_content = content[start:end]

            chunks.append(
                {
                    "file_path": file_path,
                    "type": "generic",
                    "name": f"chunk_{len(chunks) + 1}",
                    "content": chunk_content,
                    "start_pos": start,
                    "end_pos": end,
                    "size": len(chunk_content),
                    "metadata": {
                        "language": self._get_file_extension(file_path)[
                            1:
                        ],  # Remove the dot
                        "chunk_method": "size_based",
                    },
                }
            )

            start = end - self.overlap if end < content_length else end

        return chunks

    def _create_sub_chunks(
        self,
        content: str,
        file_path: str,
        start_line: int,
        unit_type: str,
        unit_name: str,
    ) -> List[Dict[str, Any]]:
        """
        Create sub-chunks for when a logical unit is too large

        Args:
            content: Content to chunk
            file_path: Path to the original file
            start_line: Starting line number in the original file
            unit_type: Type of the logical unit (function, class, etc.)
            unit_name: Name of the logical unit

        Returns:
            List of sub-chunk dictionaries
        """
        sub_chunks = []
        lines = content.split("\n")

        # Chunk by groups of lines
        lines_per_chunk = (
            self.max_chunk_size // 80
        )  # Rough estimate: 80 chars per line avg

        for i in range(0, len(lines), lines_per_chunk):
            chunk_lines = lines[i : i + lines_per_chunk]
            chunk_content = "\n".join(chunk_lines)

            sub_chunks.append(
                {
                    "file_path": file_path,
                    "type": f"{unit_type}_subchunk",
                    "name": f"{unit_name}_part_{len(sub_chunks) + 1}",
                    "content": chunk_content,
                    "start_line": start_line + i,
                    "end_line": start_line + i + len(chunk_lines) - 1,
                    "size": len(chunk_content),
                    "metadata": {
                        "language": "python",
                        "chunk_method": "logical_unit_split",
                        "parent": unit_name,
                        "parent_type": unit_type,
                    },
                }
            )

        return sub_chunks


def main():
    """
    Main function to demonstrate code chunking
    """
    print("NudgeAI Code Chunker")
    print("=" * 30)

    chunker = CodeChunker(max_chunk_size=500, overlap=50)

    # Example: chunk the current file
    with open(__file__, "r") as f:
        content = f.read()

    chunks = chunker.chunk_file(__file__, content)

    print(f"Chunked file '{__file__}' into {len(chunks)} chunks:")

    for i, chunk in enumerate(chunks):
        print(
            f"  Chunk {i + 1}: {chunk['size']} chars, "
            f"type='{chunk['type']}', name='{chunk['name']}'"
        )


if __name__ == "__main__":
    main()

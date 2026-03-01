"""
Code fetcher module for NudgeAI codebase analysis
Fetches code files from the local project
"""

import os
import glob
from typing import List, Dict, Optional


class CodeFetcher:
    """
    Fetches code files from the local project directory
    """

    def __init__(
        self, project_root: str = ".", exclude_dirs: Optional[List[str]] = None
    ):
        """
        Initialize the code fetcher

        Args:
            project_root: Root directory of the project to analyze
            exclude_dirs: Directories to exclude from analysis (e.g., venv, .git, __pycache__)
        """
        self.project_root = project_root
        if exclude_dirs is None:
            exclude_dirs = [
                "venv",
                ".git",
                "__pycache__",
                ".pytest_cache",
                "node_modules",
                ".vscode",
                ".idea",
            ]
        self.exclude_dirs = exclude_dirs

    def fetch_files(
        self, extensions: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Fetch code files from the project directory

        Args:
            extensions: List of file extensions to include (e.g., ['.py', '.js', '.ts'])

        Returns:
            List of dictionaries containing file information
        """
        if extensions is None:
            extensions = [
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".java",
                ".cpp",
                ".c",
                ".html",
                ".css",
                ".md",
            ]

        code_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories from search
            dirs[:] = [
                d for d in dirs if d not in self.exclude_dirs and not d.startswith(".")
            ]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.relpath(
                        os.path.join(root, file), self.project_root
                    )

                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                        code_files.append(
                            {
                                "path": file_path,
                                "filename": file,
                                "full_path": os.path.abspath(file_path),
                                "extension": os.path.splitext(file)[1],
                                "size": len(content),
                                "content": content,
                                "lines": len(content.splitlines()),
                            }
                        )
                    except Exception as e:
                        print(f"Could not read file {file_path}: {str(e)}")

        return code_files

    def fetch_file_content(self, file_path: str) -> Optional[str]:
        """
        Fetch content of a specific file

        Args:
            file_path: Path to the file to read

        Returns:
            File content as string or None if file cannot be read
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return None


def main():
    """
    Main function to demonstrate code fetching
    """
    print("NudgeAI Code Fetcher")
    print("=" * 30)

    fetcher = CodeFetcher()
    files = fetcher.fetch_files([".py"])  # Only Python files for demo

    print(f"Found {len(files)} Python files in the project")

    # Show the largest files
    largest_files = sorted(files, key=lambda x: x["size"], reverse=True)[:5]
    print("\nLargest Python files:")
    for file_info in largest_files:
        print(
            f"  {file_info['path']} ({file_info['size']} bytes, {file_info['lines']} lines)"
        )


if __name__ == "__main__":
    main()

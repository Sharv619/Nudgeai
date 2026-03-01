"""
Code parser module for NudgeAI codebase analysis
Parses code files and extracts relevant information for analysis
"""

import ast
import re
from typing import Dict, List, Any, Optional
from data_ingestion.codebase.code_fetcher import CodeFetcher


class CodeParser:
    """
    Parses code files and extracts relevant information for analysis
    """

    def __init__(self):
        self.supported_languages = {
            ".py": self.parse_python,
            ".js": self.parse_javascript,
            ".ts": self.parse_typescript,
            ".java": self.parse_java,
        }

    def parse_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Parse a code file based on its extension

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            Dictionary containing parsed information
        """
        ext = self.get_file_extension(file_path)

        if ext in self.supported_languages:
            return self.supported_languages[ext](file_path, content)
        else:
            # For unsupported languages, return basic info
            return {
                "file_path": file_path,
                "language": "unknown",
                "content_preview": content[:500],
                "lines_of_code": len(content.split("\n")),
                "functions": [],
                "classes": [],
                "imports": [],
                "potential_issues": [],
            }

    def get_file_extension(self, file_path: str) -> str:
        """
        Get the file extension from a file path

        Args:
            file_path: Path to the file

        Returns:
            File extension
        """
        return "." + file_path.split(".")[-1]

    def parse_python(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Parse a Python file using AST

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            Dictionary containing parsed Python information
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # If there's a syntax error, return basic info
            return {
                "file_path": file_path,
                "language": "python",
                "content_preview": content[:500],
                "lines_of_code": len(content.split("\n")),
                "functions": [],
                "classes": [],
                "imports": [],
                "potential_issues": ["SyntaxError"],
            }

        functions = []
        classes = []
        imports = []
        potential_issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": getattr(node, "end_lineno", node.lineno),
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                    }
                )
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": getattr(node, "end_lineno", node.lineno),
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "is_async": True,
                    }
                )
            elif isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": getattr(node, "end_lineno", node.lineno),
                        "methods": [
                            n.name
                            for n in node.body
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        ],
                        "docstring": ast.get_docstring(node),
                    }
                )
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

        # Check for potential performance issues
        content_lower = content.lower()
        if "for" in content_lower and "in range(" in content_lower:
            # Count nested loops
            loop_pattern = r"for\s+\w+\s+in\s+range\s*\("
            loops = re.findall(loop_pattern, content)
            if len(loops) > 2:
                potential_issues.append(
                    f"Multiple loops detected ({len(loops)}) - potential performance issue"
                )

        # Check for frequent append operations in loops
        append_pattern = r"for.*:\s*\n(\s+.+\.append\(.+\)\s*\n)+"
        append_matches = re.findall(append_pattern, content, re.MULTILINE)
        if len(append_matches) > 1:
            potential_issues.append(
                f"Multiple append operations in loops detected - consider list comprehension"
            )

        return {
            "file_path": file_path,
            "language": "python",
            "content_preview": content[:500],
            "lines_of_code": len(content.split("\n")),
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "potential_issues": potential_issues,
        }

    def parse_javascript(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Parse a JavaScript file (basic regex-based parsing)

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            Dictionary containing parsed JavaScript information
        """
        # Basic regex patterns for JavaScript
        functions = []
        classes = []
        imports = []
        potential_issues = []

        # Find function declarations
        func_pattern = r"(async\s+)?function\s+(\w+)\s*\("
        for match in re.finditer(func_pattern, content):
            is_async = bool(match.group(1))
            functions.append({"name": match.group(2), "is_async": is_async})

        # Find arrow functions
        arrow_func_pattern = r"const\s+(\w+)\s*=\s*\([^)]*\)\s*=>"
        for match in re.finditer(arrow_func_pattern, content):
            functions.append({"name": match.group(1), "is_arrow": True})

        # Find class declarations
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, content):
            classes.append({"name": match.group(1)})

        # Find imports
        import_pattern = r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]'
        imports = re.findall(import_pattern, content)

        return {
            "file_path": file_path,
            "language": "javascript",
            "content_preview": content[:500],
            "lines_of_code": len(content.split("\n")),
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "potential_issues": potential_issues,
        }

    def parse_typescript(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Parse a TypeScript file (similar to JavaScript for now)

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            Dictionary containing parsed TypeScript information
        """
        # For now, use the same logic as JavaScript parsing
        return self.parse_javascript(file_path, content)

    def parse_java(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Parse a Java file (basic regex-based parsing)

        Args:
            file_path: Path to the file
            content: Content of the file

        Returns:
            Dictionary containing parsed Java information
        """
        functions = []
        classes = []
        imports = []
        potential_issues = []

        # Find class declarations
        class_pattern = r"public\s+class\s+(\w+)"
        for match in re.finditer(class_pattern, content):
            classes.append({"name": match.group(1)})

        # Find method declarations
        method_pattern = r"(public|private|protected)\s+[\w<>[\]]+\s+(\w+)\s*\("
        for match in re.finditer(method_pattern, content):
            functions.append({"name": match.group(2)})

        # Find imports
        import_pattern = r"import\s+([.\w]+);"
        imports = re.findall(import_pattern, content)

        return {
            "file_path": file_path,
            "language": "java",
            "content_preview": content[:500],
            "lines_of_code": len(content.split("\n")),
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "potential_issues": potential_issues,
        }


def analyze_codebase(project_root: str = ".") -> List[Dict[str, Any]]:
    """
    Analyze the entire codebase

    Args:
        project_root: Root directory of the project to analyze

    Returns:
        List of parsed file information
    """
    fetcher = CodeFetcher(project_root)
    parser = CodeParser()

    files = fetcher.fetch_files()
    parsed_files = []

    for file_info in files:
        parsed = parser.parse_file(file_info["path"], file_info["content"])
        parsed_files.append(parsed)

    return parsed_files


def main():
    """
    Main function to demonstrate code parsing
    """
    print("NudgeAI Code Parser")
    print("=" * 30)

    # Analyze the current project
    parsed_files = analyze_codebase()

    print(f"Parsed {len(parsed_files)} files")

    # Count statistics
    total_functions = sum(len(f["functions"]) for f in parsed_files)
    total_classes = sum(len(f["classes"]) for f in parsed_files)
    python_files = len([f for f in parsed_files if f["language"] == "python"])

    print(f"  Python files: {python_files}")
    print(f"  Total functions: {total_functions}")
    print(f"  Total classes: {total_classes}")

    # Show potential issues
    all_issues = []
    for file_info in parsed_files:
        if file_info["potential_issues"]:
            for issue in file_info["potential_issues"]:
                all_issues.append((file_info["file_path"], issue))

    if all_issues:
        print(f"\nPotential issues found in {len(all_issues)} locations:")
        for file_path, issue in all_issues[:10]:  # Show first 10
            print(f"  {file_path}: {issue}")
        if len(all_issues) > 10:
            print(f"  ... and {len(all_issues) - 10} more")


if __name__ == "__main__":
    main()

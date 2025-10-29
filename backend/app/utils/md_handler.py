"""
Markdown file handler utility.

Handles Markdown file creation, reading, and formatting for report generation.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional


class MarkdownHandler:
    """Markdown file operations handler."""

    @staticmethod
    def save_md_file(content: str, filepath: str) -> bool:
        """Saves content to a Markdown file.

        Args:
            content: Markdown content to save
            filepath: Target file path (absolute)

        Returns:
            True if saved successfully, False otherwise

        Raises:
            IOError: If file write fails

        Examples:
            >>> content = "# Report Title\\n\\nThis is content"
            >>> MarkdownHandler.save_md_file(content, "/path/to/report.md")
            True
        """
        try:
            # Create parent directories if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Write file with UTF-8 encoding
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            raise IOError(f"Failed to save MD file: {e}")

    @staticmethod
    def read_md_file(filepath: str) -> str:
        """Reads content from a Markdown file.

        Args:
            filepath: Source file path (absolute)

        Returns:
            Markdown content as string

        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file read fails

        Examples:
            >>> content = MarkdownHandler.read_md_file("/path/to/report.md")
            >>> print(content[:20])
            # Report Title

This
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"MD file not found: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            raise IOError(f"Failed to read MD file: {e}")

    @staticmethod
    def format_report_as_md(report_data: Dict[str, Any]) -> str:
        """Formats report data dictionary as Markdown.

        Args:
            report_data: Report data with keys: title, summary, background, main_content, conclusion

        Returns:
            Formatted Markdown string

        Examples:
            >>> report_data = {
            ...     "title": "Digital Banking Trends",
            ...     "summary": "Overview of trends",
            ...     "background": "Background info",
            ...     "main_content": "Detailed analysis",
            ...     "conclusion": "Final thoughts"
            ... }
            >>> md = MarkdownHandler.format_report_as_md(report_data)
            >>> print(md[:30])
            # Digital Banking Trends

##
        """
        title = report_data.get("title", "Untitled Report")
        summary = report_data.get("summary", "")
        background = report_data.get("background", "")
        main_content = report_data.get("main_content", "")
        conclusion = report_data.get("conclusion", "")

        # Build Markdown structure
        md_content = []

        # Title
        md_content.append(f"# {title}")
        md_content.append("")  # Empty line

        # Summary section
        if summary:
            md_content.append("## 요약")
            md_content.append("")
            md_content.append(summary)
            md_content.append("")

        # Background section
        if background:
            md_content.append("## 배경 및 목적")
            md_content.append("")
            md_content.append(background)
            md_content.append("")

        # Main content section
        if main_content:
            md_content.append("## 주요 내용")
            md_content.append("")
            md_content.append(main_content)
            md_content.append("")

        # Conclusion section
        if conclusion:
            md_content.append("## 결론 및 제언")
            md_content.append("")
            md_content.append(conclusion)
            md_content.append("")

        return "\n".join(md_content)

    @staticmethod
    def parse_md_report(md_content: str) -> Dict[str, Any]:
        """Parses Markdown report content into structured data.

        Args:
            md_content: Markdown content string

        Returns:
            Dictionary with keys: title, summary, background, main_content, conclusion

        Note:
            This is a simple parser that extracts sections based on ## headers.
            More sophisticated parsing may be needed for complex documents.

        Examples:
            >>> md_content = "# Title\\n\\n## 요약\\nSummary text\\n\\n## 배경 및 목적\\nBackground"
            >>> report_data = MarkdownHandler.parse_md_report(md_content)
            >>> print(report_data["title"])
            Title
        """
        lines = md_content.split("\n")
        report_data = {
            "title": "",
            "summary": "",
            "background": "",
            "main_content": "",
            "conclusion": ""
        }

        current_section = None
        section_content = []

        for line in lines:
            # Title (# heading)
            if line.startswith("# "):
                if current_section:
                    report_data[current_section] = "\n".join(section_content).strip()
                    section_content = []

                report_data["title"] = line[2:].strip()
                current_section = None

            # Section headers (## heading)
            elif line.startswith("## "):
                if current_section:
                    report_data[current_section] = "\n".join(section_content).strip()
                    section_content = []

                header = line[3:].strip()

                # Map Korean headers to keys
                if "요약" in header:
                    current_section = "summary"
                elif "배경" in header or "목적" in header:
                    current_section = "background"
                elif "주요" in header or "내용" in header:
                    current_section = "main_content"
                elif "결론" in header or "제언" in header:
                    current_section = "conclusion"
                else:
                    current_section = None

            # Content lines
            else:
                if current_section:
                    section_content.append(line)

        # Save last section
        if current_section and section_content:
            report_data[current_section] = "\n".join(section_content).strip()

        return report_data

    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Gets the size of a file in bytes.

        Args:
            filepath: File path

        Returns:
            File size in bytes

        Raises:
            FileNotFoundError: If file does not exist
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        return os.path.getsize(filepath)

    @staticmethod
    def delete_md_file(filepath: str) -> bool:
        """Deletes a Markdown file.

        Args:
            filepath: File path to delete

        Returns:
            True if deleted successfully, False if file doesn't exist

        Raises:
            IOError: If deletion fails
        """
        if not os.path.exists(filepath):
            return False

        try:
            os.remove(filepath)
            return True

        except Exception as e:
            raise IOError(f"Failed to delete MD file: {e}")

"""
Artifact file management utility.

Provides abstraction layer for artifact file storage and retrieval.
Supports local filesystem storage (future: S3, Azure Blob, etc.).
"""
import os
import hashlib
from pathlib import Path
from typing import Optional
from shared.types.enums import ArtifactKind
from shared.constants import ProjectPath


class ArtifactManager:
    """Artifact file storage manager."""

    # Base directory for artifacts (local storage)
    ARTIFACTS_BASE_DIR = ProjectPath.BACKEND_DIR / "artifacts"

    @staticmethod
    def generate_artifact_path(
        topic_id: int,
        message_id: int,
        filename: str
    ) -> str:
        """Generates storage path for an artifact.

        Args:
            topic_id: Topic ID
            message_id: Message ID
            filename: Desired filename

        Returns:
            Absolute file path as string

        Examples:
            >>> path = ArtifactManager.generate_artifact_path(1, 2, "report.md")
            >>> print(path)
            /path/to/artifacts/topics/topic_1/messages/msg_2_report.md
        """
        # Structure: artifacts/topics/topic_{id}/messages/msg_{id}_{filename}
        topic_dir = ArtifactManager.ARTIFACTS_BASE_DIR / "topics" / f"topic_{topic_id}" / "messages"
        os.makedirs(topic_dir, exist_ok=True)

        # Prefix filename with message ID to avoid conflicts
        prefixed_filename = f"msg_{message_id}_{filename}"
        file_path = topic_dir / prefixed_filename

        return str(file_path)

    @staticmethod
    def store_artifact(
        content: str | bytes,
        filepath: str,
        is_binary: bool = False
    ) -> int:
        """Stores artifact content to file.

        Args:
            content: Content to store (str for text, bytes for binary)
            filepath: Target file path
            is_binary: True for binary files (HWPX, PDF), False for text (MD)

        Returns:
            File size in bytes

        Raises:
            IOError: If file write fails

        Examples:
            >>> content = "# Report Content"
            >>> size = ArtifactManager.store_artifact(content, "/path/to/report.md")
            >>> print(size)
            16
        """
        try:
            # Create parent directories
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Write file
            mode = 'wb' if is_binary else 'w'
            encoding = None if is_binary else 'utf-8'

            with open(filepath, mode, encoding=encoding) as f:
                f.write(content)

            # Return file size
            return os.path.getsize(filepath)

        except Exception as e:
            raise IOError(f"Failed to store artifact: {e}")

    @staticmethod
    def retrieve_artifact(filepath: str, is_binary: bool = False) -> str | bytes:
        """Retrieves artifact content from file.

        Args:
            filepath: Source file path
            is_binary: True for binary files, False for text

        Returns:
            File content (str for text, bytes for binary)

        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file read fails

        Examples:
            >>> content = ArtifactManager.retrieve_artifact("/path/to/report.md")
            >>> print(type(content))
            <class 'str'>
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Artifact file not found: {filepath}")

        try:
            mode = 'rb' if is_binary else 'r'
            encoding = None if is_binary else 'utf-8'

            with open(filepath, mode, encoding=encoding) as f:
                return f.read()

        except Exception as e:
            raise IOError(f"Failed to retrieve artifact: {e}")

    @staticmethod
    def delete_artifact(filepath: str) -> bool:
        """Deletes an artifact file.

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
            raise IOError(f"Failed to delete artifact: {e}")

    @staticmethod
    def calculate_sha256(filepath: str) -> str:
        """Calculates SHA256 hash of a file for deduplication.

        Args:
            filepath: File path

        Returns:
            SHA256 hash as hexadecimal string

        Raises:
            FileNotFoundError: If file does not exist

        Examples:
            >>> hash_value = ArtifactManager.calculate_sha256("/path/to/report.md")
            >>> print(len(hash_value))
            64
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        sha256_hash = hashlib.sha256()

        with open(filepath, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

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
    def get_extension_for_kind(kind: ArtifactKind) -> str:
        """Gets file extension for an artifact kind.

        Args:
            kind: Artifact kind enum

        Returns:
            File extension (including dot)

        Examples:
            >>> ext = ArtifactManager.get_extension_for_kind(ArtifactKind.MD)
            >>> print(ext)
            .md
        """
        extensions = {
            ArtifactKind.MD: ".md",
            ArtifactKind.HWPX: ".hwpx",
            ArtifactKind.PDF: ".pdf"
        }

        return extensions.get(kind, ".bin")

    @staticmethod
    def generate_filename(
        topic_id: int,
        kind: ArtifactKind,
        version: int = 1,
        locale: str = "ko"
    ) -> str:
        """Generates a standardized filename for an artifact.

        Args:
            topic_id: Topic ID
            kind: Artifact kind
            version: Version number
            locale: Language code

        Returns:
            Generated filename

        Examples:
            >>> filename = ArtifactManager.generate_filename(1, ArtifactKind.MD, 1, "ko")
            >>> print(filename)
            topic_1_v1_ko.md
        """
        ext = ArtifactManager.get_extension_for_kind(kind)
        return f"topic_{topic_id}_v{version}_{locale}{ext}"

    @staticmethod
    def ensure_artifacts_directory() -> Path:
        """Ensures the artifacts base directory exists.

        Returns:
            Path to artifacts directory

        Examples:
            >>> artifacts_dir = ArtifactManager.ensure_artifacts_directory()
            >>> print(artifacts_dir.exists())
            True
        """
        os.makedirs(ArtifactManager.ARTIFACTS_BASE_DIR, exist_ok=True)
        return ArtifactManager.ARTIFACTS_BASE_DIR

"""
Artifact models for generated files (MD, HWPX, PDF).

Artifacts represent generated files at various stages of the report creation process.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from shared.types.enums import ArtifactKind


class ArtifactCreate(BaseModel):
    """Request model for creating a new artifact.

    Attributes:
        kind: Artifact type (md/hwpx/pdf)
        locale: Language/locale code (ko/en)
        version: Version number (default: 1)
        filename: File name
        file_path: File storage path
        file_size: File size in bytes
        sha256: SHA256 hash for deduplication (optional)
    """
    kind: ArtifactKind = Field(..., description="Artifact type")
    locale: str = Field(default="ko", max_length=10, description="Language code")
    version: int = Field(default=1, ge=1, description="Version number")
    filename: str = Field(..., max_length=255, description="File name")
    file_path: str = Field(..., max_length=500, description="File storage path")
    file_size: int = Field(default=0, ge=0, description="File size in bytes")
    sha256: Optional[str] = Field(None, max_length=64, description="SHA256 hash")


class Artifact(BaseModel):
    """Full artifact entity model.

    Attributes:
        id: Artifact ID
        topic_id: ID of the parent topic
        message_id: ID of the message that generated this artifact
        kind: Artifact type
        locale: Language code
        version: Version number
        filename: File name
        file_path: File storage path
        file_size: File size in bytes
        sha256: SHA256 hash (optional)
        created_at: Creation timestamp
    """
    id: int
    topic_id: int
    message_id: int
    kind: ArtifactKind
    locale: str
    version: int
    filename: str
    file_path: str
    file_size: int
    sha256: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ArtifactResponse(BaseModel):
    """Public artifact response model.

    Suitable for API responses.

    Attributes:
        id: Artifact ID
        topic_id: Parent topic ID
        message_id: Source message ID
        kind: Artifact type
        locale: Language code
        version: Version number
        filename: File name
        file_path: File storage path (may be relative)
        file_size: File size in bytes
        created_at: Creation timestamp
    """
    id: int
    topic_id: int
    message_id: int
    kind: ArtifactKind
    locale: str
    version: int
    filename: str
    file_path: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArtifactListResponse(BaseModel):
    """Paginated list of artifacts.

    Attributes:
        artifacts: List of artifact responses
        total: Total number of artifacts
        topic_id: Parent topic ID (optional filter)
    """
    artifacts: list[ArtifactResponse]
    total: int
    topic_id: Optional[int] = None


class ArtifactContentResponse(BaseModel):
    """Response model for artifact content (e.g., MD file).

    Attributes:
        artifact_id: Artifact ID
        content: File content as text
        filename: File name
        kind: Artifact type
    """
    artifact_id: int
    content: str
    filename: str
    kind: ArtifactKind

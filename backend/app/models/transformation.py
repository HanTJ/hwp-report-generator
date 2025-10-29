"""
Transformation models for tracking file conversions and translations.

Transformations track the lineage of artifact conversions (MD→HWPX, EN→KO).
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from shared.types.enums import TransformOperation


class TransformationCreate(BaseModel):
    """Request model for creating a transformation record.

    Attributes:
        from_artifact_id: Source artifact ID
        to_artifact_id: Target artifact ID
        operation: Type of transformation (convert/translate)
        params_json: JSON string of transformation parameters (optional)
    """
    from_artifact_id: int = Field(..., description="Source artifact ID")
    to_artifact_id: int = Field(..., description="Target artifact ID")
    operation: TransformOperation = Field(..., description="Transformation operation")
    params_json: Optional[str] = Field(None, max_length=2000, description="Transformation parameters (JSON)")


class Transformation(BaseModel):
    """Full transformation entity model.

    Attributes:
        id: Transformation ID
        from_artifact_id: Source artifact ID
        to_artifact_id: Target artifact ID
        operation: Transformation operation type
        params_json: Transformation parameters as JSON string
        created_at: Creation timestamp
    """
    id: int
    from_artifact_id: int
    to_artifact_id: int
    operation: TransformOperation
    params_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransformationResponse(BaseModel):
    """Public transformation response model.

    Attributes:
        id: Transformation ID
        from_artifact_id: Source artifact ID
        to_artifact_id: Target artifact ID
        operation: Operation type
        params_json: Parameters JSON string
        created_at: Creation timestamp
    """
    id: int
    from_artifact_id: int
    to_artifact_id: int
    operation: TransformOperation
    params_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

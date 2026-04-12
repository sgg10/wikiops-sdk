from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field

from wikiops_sdk.domain.models import AssetRef, DocumentRef, DocumentVersion


class OperationStatus(str, Enum):
    """Terminal status reported after attempting to apply an operation."""

    APPLIED = "applied"
    SKIPPED = "skipped"
    FAILED = "failed"


class AppliedOperationResult(BaseModel):
    """Per-operation apply outcome including optional resolved refs and version."""

    operation_id: str = Field(..., description="Unique identifier for the operation.")
    status: OperationStatus = Field(..., description="Status of the operation.")
    message: Optional[str] = Field(
        None, description="Detailed message about the operation result."
    )
    resolved_ref: Optional[DocumentRef] = Field(
        None, description="Reference to the document that was processed."
    )
    resolved_asset_ref: Optional[AssetRef] = Field(
        None, description="Reference to the asset that was processed."
    )
    resolved_asset_reference: Optional[str] = Field(
        None,
        description="Provider-specific reference string that can be embedded in content.",
    )
    resulting_version: Optional[DocumentVersion] = Field(
        None, description="Version of the document after the operation was applied."
    )


class ApplyResult(BaseModel):
    """Provider-level aggregate result for a batch apply execution."""

    provider_name: str = Field(
        ..., description="Name of the provider that processed the operations."
    )
    results: List[AppliedOperationResult] = Field(
        default_factory=list, description="List of results for each applied operation."
    )

    def has_failures(self) -> bool:
        """Return ``True`` when at least one operation result is failed."""

        return any(result.status == OperationStatus.FAILED for result in self.results)

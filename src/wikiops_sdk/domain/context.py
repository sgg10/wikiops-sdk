from typing import Any, Dict

from pydantic import BaseModel, Field

from wikiops_sdk.domain.models import Document, DocumentRef


class ExecutionContext(BaseModel):
    """Mutable execution state shared across orchestration and plugin steps."""

    run_id: str = Field(
        ..., description="Unique identifier for the current execution run."
    )
    profile_name: str = Field(..., description="Name of the profile being executed.")
    provider_name: str = Field(..., description="Name of the provider being used.")
    dry_run: bool = Field(
        True,
        description="Indicates whether the execution is a dry run (no actual changes will be made).",
    )

    refs: Dict[str, DocumentRef] = Field(
        default_factory=dict,
        description=(
            "Mapping of operation IDs to document references. This allows operations to "
            "reference documents created or modified by previous operations in the same run."
        ),
    )
    documents: Dict[str, Document] = Field(
        default_factory=dict,
        description=(
            "Mapping of document references to their corresponding document payloads. This "
            "allows operations to access the content and metadata of documents referenced in "
            "the execution context."
        ),
    )

    plugin_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration settings for plugins used during execution.",
    )
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input data provided to the execution, which may be used by operations.",
    )
    runtime_vars: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Runtime variables that can be set and accessed by operations during execution. This allows "
            "operations to share data and state across the execution context."
        ),
    )

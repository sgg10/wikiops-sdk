from enum import Enum
from uuid import uuid4
from typing import Any, Literal, Union, Annotated, Optional, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class DocumentFormat(str, Enum):
    """Canonical content formats supported by SDK document models."""

    MARKDOWN = "markdown"


class RefKind(str, Enum):
    """Logical strategies used to identify documents across providers."""

    ID = "id"
    PATH = "path"
    ALIAS = "alias"


class ProviderCapability(str, Enum):
    """Feature flags that describe the operations a provider supports."""

    READ_DOCUMENT = "read_document"
    CHECK_EXISTS = "check_exists"
    CREATE_DOCUMENT = "create_document"
    UPDATE_DOCUMENT = "update_document"
    CREATE_CHILD_DOCUMENT = "create_child_document"
    BUILD_LINK = "build_link"
    RESOLVE_BY_PATH = "resolve_by_path"
    RESOLVE_BY_ID = "resolve_by_id"
    HIERARCHICAL_PAGES = "hierarchical_pages"
    VERSION_CHECK = "version_check"


class DocumentVersion(BaseModel):
    """Provider-agnostic version metadata for optimistic concurrency checks."""

    token: Optional[str] = Field(
        None, description="Opaque version token provided by the provider."
    )
    revision: Optional[int] = Field(
        None, description="Revision number, if supported by the provider."
    )
    etag: Optional[str] = Field(
        None, description="ETag value, if supported by the provider."
    )


class DocumentRef(BaseModel):
    """Provider-scoped locator that resolves a concrete document instance."""

    model_config = ConfigDict(extra="allow")

    provider: str = Field(..., description="Logical provider identifier.")
    kind: RefKind = Field(..., description="Kind of reference.")
    locator: Dict[str, str] = Field(
        default_factory=dict, description="Locator information for the reference."
    )
    alias: Optional[str] = Field(
        None, description="Optional alias for the reference, if kind is 'alias'."
    )
    title_hint: Optional[str] = Field(
        None, description="Optional title hint for the referenced document."
    )
    parent_alias: Optional[str] = Field(
        None, description="Optional parent alias for hierarchical documents."
    )


class Document(BaseModel):
    """Portable document payload with normalized content and metadata fields."""

    ref: DocumentRef = Field(..., description="Logical reference to the document.")
    title: str = Field(..., description="Document title.")
    content: str = Field(
        default_factory=str, description="Document content in the specified format."
    )
    format: DocumentFormat = Field(
        DocumentFormat.MARKDOWN, description="Format of the document content."
    )
    version: Optional[DocumentVersion] = Field(
        None, description="Optional version information for the document."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Optional provider-specific metadata."
    )


class BaseMessage(BaseModel):
    """Shared envelope for machine- and human-readable planning messages."""

    code: str = Field(..., description="Machine-readable warning code.")
    message: str = Field(..., description="Human-readable warning message.")


class WarningMessage(BaseMessage):
    """Structured warning message emitted during planning."""

    details: Optional[Dict[str, Any]] = Field(
        None, description="Optional additional details about the warning."
    )


class NoteMessage(BaseMessage):
    """Structured informational message emitted during planning."""


class BaseOperation(BaseModel):
    """Common metadata for mutation operations emitted by plugins."""

    operation_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the operation.",
    )
    reason: Optional[str] = Field(
        None, description="Optional human-readable reason for the operation."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Optional list of tags for categorizing the operation.",
    )


class CreateDocumentOperation(BaseOperation):
    """Operation that creates a new document in the provider namespace."""

    operation: Literal["create_document"] = Field(
        "create_document", description="Type of the operation."
    )
    ref: Optional[DocumentRef] = Field(
        None,
        description=(
            "Optional reference for the new document. If not provided, the provider "
            "will generate a reference upon creation."
        ),
    )
    parent_ref: Optional[DocumentRef] = Field(
        None, description="Optional reference for the parent document."
    )
    title: str = Field(..., description="Document title.")
    content: str = Field(..., description="Document content.")
    format: DocumentFormat = Field(
        DocumentFormat.MARKDOWN, description="Format of the document content."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Optional provider-specific metadata."
    )


class UpdateDocumentOperation(BaseOperation):
    """Operation that updates the content of an existing document."""

    operation: Literal["update_document"] = Field(
        "update_document", description="Type of the operation."
    )
    ref: DocumentRef = Field(..., description="Reference for the document to update.")
    new_content: str = Field(..., description="New content for the document.")
    expected_version: Optional[DocumentVersion] = Field(
        None,
        description=(
            "Optional expected version for concurrency control. If provided, the "
            "provider should verify that the current version of the document matches "
            "the expected version before applying the update."
        ),
    )
    format: DocumentFormat = Field(
        DocumentFormat.MARKDOWN, description="Format of the document content."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Optional provider-specific metadata."
    )


class CreateChildDocumentOperation(BaseOperation):
    """Operation that creates a new child document under a parent reference."""

    operation: Literal["create_child_document"] = Field(
        "create_child_document", description="Type of the operation."
    )
    parent_ref: DocumentRef = Field(
        ..., description="Reference for the parent document."
    )
    ref: Optional[DocumentRef] = Field(
        None,
        description=(
            "Optional reference for the new child document. If not provided, the "
            "provider will generate a reference upon creation."
        ),
    )
    child_title: str = Field(..., description="Child document title.")
    child_content: str = Field(..., description="Child document content.")
    child_format: DocumentFormat = Field(
        DocumentFormat.MARKDOWN, description="Format of the child document content."
    )
    child_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional provider-specific metadata for the child document.",
    )


Operation = Annotated[
    Union[
        CreateDocumentOperation,
        UpdateDocumentOperation,
        CreateChildDocumentOperation,
    ],
    Field(discriminator="operation"),
]


class ChangeSet(BaseModel):
    """Provider-targeted batch of planned operations and planning messages."""

    plugin_id: str = Field(
        ..., description="Identifier of the plugin that generated the changeset."
    )
    operations: List[Operation] = Field(
        default_factory=list, description="List of operations to apply."
    )
    warnings: List[WarningMessage] = Field(
        default_factory=list,
        description="Optional list of warnings related to the changeset.",
    )
    notes: List[NoteMessage] = Field(
        default_factory=list,
        description="Optional list of notes related to the changeset.",
    )

    def is_empty(self) -> bool:
        """Return ``True`` when no operations were planned in this change set."""

        return len(self.operations) == 0

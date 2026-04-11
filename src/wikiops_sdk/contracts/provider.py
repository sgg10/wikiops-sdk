from typing import Optional, Protocol, Set, runtime_checkable

from pydantic import BaseModel, Field

from wikiops_sdk.compat import PROVIDER_API_VERSION
from wikiops_sdk.domain.context import ExecutionContext
from wikiops_sdk.domain.models import (
    Asset,
    AssetRef,
    ChangeSet,
    Document,
    DocumentRef,
    PutAssetOperation,
    ProviderCapability,
)
from wikiops_sdk.domain.results import ApplyResult


class ProviderSettings(BaseModel):
    """Base model for provider-specific configuration settings."""

    provider_name: str = Field(..., description="Logical name of the target provider.")
    provider_api_version: str = Field(
        default=PROVIDER_API_VERSION,
        description="Version of the provider API that this provider implements.",
    )


@runtime_checkable
class DocumentProvider(Protocol):
    """Behavioral contract implemented by backend document providers."""

    provider_id: str

    def capabilities(self) -> Set[ProviderCapability]:
        """Return the provider capabilities supported by this implementation."""

        ...

    def validate_settings(self) -> None:
        """Validate provider settings and raise if configuration is invalid."""

        ...

    def resolve_ref(
        self, ref: DocumentRef, ctx: Optional[ExecutionContext]
    ) -> DocumentRef:
        """Resolve a logical reference into a concrete provider reference."""

        ...

    def exists(self, ref: DocumentRef) -> bool:
        """Return whether the referenced document currently exists."""

        ...

    def get_document(self, ref: DocumentRef) -> Document:
        """Fetch and return the current document payload for ``ref``."""

        ...

    def build_link(self, ref: DocumentRef) -> Optional[str]:
        """Build a user-facing URL for ``ref`` when the provider supports it."""

        ...

    def put_asset(self, operation: PutAssetOperation, content: bytes) -> Asset:
        """Persist the asset bytes described by ``operation`` and return the stored asset."""

        ...

    def build_asset_reference(self, ref: AssetRef) -> str:
        """Build a document-embeddable reference string for ``ref``."""

        ...

    def apply_changes(self, changeset: ChangeSet) -> ApplyResult:
        """Apply a change set and return per-operation execution results."""

        ...

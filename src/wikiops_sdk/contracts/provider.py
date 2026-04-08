from typing import Optional, Protocol, Set, runtime_checkable

from pydantic import BaseModel, Field

from wikiops_sdk.domain.context import ExecutionContext
from wikiops_sdk.domain.models import (
    ChangeSet,
    Document,
    DocumentRef,
    ProviderCapability,
)
from wikiops_sdk.domain.results import ApplyResult


class ProviderSettings(BaseModel):
    """Base model for provider-specific configuration settings."""

    provider_name: str = Field(..., description="Logical name of the target provider.")


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

    def apply_changes(self, changeset: ChangeSet) -> ApplyResult:
        """Apply a change set and return per-operation execution results."""

        ...

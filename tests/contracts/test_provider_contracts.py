from typing import Optional, Set

from wikiops_sdk.compat import PROVIDER_API_VERSION
from wikiops_sdk.contracts.provider import DocumentProvider, ProviderSettings
from wikiops_sdk.domain.context import ExecutionContext
from wikiops_sdk.domain.models import ChangeSet, Document, DocumentRef, ProviderCapability
from wikiops_sdk.domain.results import ApplyResult


def test_provider_settings_default_api_version() -> None:
    settings = ProviderSettings(provider_name="notion")
    assert settings.provider_api_version == PROVIDER_API_VERSION


def test_provider_settings_allows_explicit_api_version() -> None:
    settings = ProviderSettings(provider_name="confluence", provider_api_version="1.2.3")
    assert settings.provider_api_version == "1.2.3"


class _DummyProvider:
    provider_id = "dummy"

    def capabilities(self) -> Set[ProviderCapability]:
        return {ProviderCapability.READ_DOCUMENT}

    def validate_settings(self) -> None:
        return None

    def resolve_ref(
        self,
        ref: DocumentRef,
        ctx: Optional[ExecutionContext],
    ) -> DocumentRef:
        return ref

    def exists(self, ref: DocumentRef) -> bool:
        return True

    def get_document(self, ref: DocumentRef) -> Document:
        return Document(ref=ref, title="Doc")

    def build_link(self, ref: DocumentRef) -> Optional[str]:
        return "https://example.test/doc"

    def apply_changes(self, changeset: ChangeSet) -> ApplyResult:
        return ApplyResult(provider_name="dummy")


def test_document_provider_runtime_protocol_positive() -> None:
    provider = _DummyProvider()
    assert isinstance(provider, DocumentProvider)


def test_document_provider_runtime_protocol_negative() -> None:
    class IncompleteProvider:
        provider_id = "incomplete"

    assert not isinstance(IncompleteProvider(), DocumentProvider)

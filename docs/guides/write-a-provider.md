# Write A Provider

This guide explains how to implement a document provider against the current SDK.

## Provider Responsibilities

A provider is responsible for interacting with a concrete documentation system.

That includes:

- resolving references
- checking whether documents exist
- reading documents
- building user-facing links when supported
- storing assets when supported
- building embeddable asset references when supported
- applying planned changes and reporting results

A provider is not responsible for deciding what content should change. That decision belongs to plugins and the host workflow.

## The Main Contract

Providers implement the `DocumentProvider` protocol from `wikiops_sdk.contracts`.

The protocol expects:

- `provider_id`
- `capabilities()`
- `validate_settings()`
- `resolve_ref(ref, ctx)`
- `exists(ref)`
- `get_document(ref)`
- `build_link(ref)`
- `put_asset(operation, content)`
- `build_asset_reference(ref)`
- `apply_changes(changeset)`

## Minimal Provider Example

```python
from wikiops_sdk.contracts import DocumentProvider, ProviderSettings
from wikiops_sdk.domain import (
    ApplyResult,
    AppliedOperationResult,
    Asset,
    AssetRef,
    AssetRefKind,
    ChangeSet,
    Document,
    DocumentRef,
    DocumentVersion,
    OperationStatus,
    PutAssetOperation,
    ProviderCapability,
    RefKind,
)


class DemoProviderSettings(ProviderSettings):
    base_url: str


class DemoProvider:
    provider_id = "demo-provider"

    def __init__(self, settings: DemoProviderSettings) -> None:
        self.settings = settings

    def capabilities(self) -> set[ProviderCapability]:
        return {
            ProviderCapability.READ_DOCUMENT,
            ProviderCapability.CHECK_EXISTS,
            ProviderCapability.CREATE_DOCUMENT,
            ProviderCapability.UPDATE_DOCUMENT,
            ProviderCapability.CREATE_CHILD_DOCUMENT,
            ProviderCapability.BUILD_LINK,
            ProviderCapability.PUT_ASSET,
            ProviderCapability.RESOLVE_BY_ID,
            ProviderCapability.RESOLVE_BY_PATH,
            ProviderCapability.VERSION_CHECK,
        }

    def validate_settings(self) -> None:
        if not self.settings.base_url.startswith("https://"):
            raise ValueError("Provider base URL must be HTTPS.")

    def resolve_ref(self, ref: DocumentRef, ctx=None) -> DocumentRef:
        if ref.kind is RefKind.ALIAS and ref.alias == "root":
            return DocumentRef(
                provider="demo-provider",
                kind=RefKind.ID,
                locator={"id": "root-page-id"},
            )
        return ref

    def exists(self, ref: DocumentRef) -> bool:
        return True

    def get_document(self, ref: DocumentRef) -> Document:
        return Document(
            ref=ref,
            title="Example Page",
            content="# Example Page\n\nExisting content.",
            version=DocumentVersion(revision=3),
        )

    def build_link(self, ref: DocumentRef) -> str | None:
        document_id = ref.locator.get("id")
        if document_id is None:
            return None
        return f"{self.settings.base_url}/pages/{document_id}"

    def put_asset(self, operation: PutAssetOperation, content: bytes) -> Asset:
        return Asset(
            ref=AssetRef(
                provider=self.settings.provider_name,
                kind=AssetRefKind.PATH,
                locator={"path": f"/.assets/{operation.name or 'asset.bin'}"},
            ),
            name=operation.name or "asset.bin",
            media_type=operation.media_type or "application/octet-stream",
            size_bytes=len(content),
        )

    def build_asset_reference(self, ref: AssetRef) -> str:
        return ref.locator["path"]

    def apply_changes(self, changeset: ChangeSet) -> ApplyResult:
        results = []
        for operation in changeset.operations:
            results.append(
                AppliedOperationResult(
                    operation_id=operation.operation_id,
                    status=OperationStatus.APPLIED,
                    message="Applied by demo provider.",
                    resulting_version=DocumentVersion(revision=4),
                )
            )
        return ApplyResult(provider_name=self.settings.provider_name, results=results)
```

## `provider_id`, `provider_name`, And `DocumentRef.provider`

These names sound similar but serve different roles.

Recommended interpretation:

- `provider_id`
  - identifier of the provider implementation itself
  - usually stable across instances of the same provider implementation
- `provider_name`
  - configured runtime name used by a profile or host configuration
  - may identify a specific configured provider instance
- `DocumentRef.provider`
  - provider namespace recorded on a reference
  - should be chosen consistently by the host/provider ecosystem

The SDK does not enforce a single naming policy, but projects should adopt one and document it consistently.

## `ProviderSettings`

`ProviderSettings` is the base model for provider configuration.

It already includes:

- `provider_name`
- `provider_api_version`

### Important Caveat

`ProviderSettings` does not enforce compatibility on its own. Hosts should use `ensure_provider_api_compatible(...)` explicitly during provider initialization.

## Advertising Capabilities

`capabilities()` should return the real capabilities of the provider.

Recommended practice:

- do not advertise unsupported capabilities as placeholders
- do not implement behavior for capabilities you do not advertise unless you intentionally want hidden support
- let the host fail fast when plugin requirements and provider capabilities do not match

## `resolve_ref(...)`

`resolve_ref(...)` should turn a logical or indirect reference into the most concrete provider reference possible.

Typical cases:

- `RefKind.ID`
  - already concrete, return as-is or normalize
- `RefKind.PATH`
  - map a path to a concrete provider identifier
- `RefKind.ALIAS`
  - resolve a logical alias like `root` into a concrete page reference

If the provider supports richer resolution context, the optional `ExecutionContext` can help, but the SDK does not mandate how that context is used.

## `get_document(...)` And `exists(...)`

These methods expose read-side infrastructure to the host.

Common uses:

- preflight checks
- content-aware planning workflows
- dry-run previews that include current content
- optimistic concurrency flows

## `build_link(...)`

This method returns a user-facing link when supported.

Recommended practice:

- advertise `ProviderCapability.BUILD_LINK` when implemented
- return `None` when a link cannot be built for the given reference

## `apply_changes(...)`

This is the provider's main write-side method.

The provider receives a provider-agnostic `ChangeSet` and is expected to translate and persist each operation appropriately.

### Recommended Result Population

For each operation, return an `AppliedOperationResult` that includes:

- `operation_id`
- `status`
- `message` when useful
- `resolved_ref` for newly created or normalized references
- `resulting_version` when version-aware persistence is available

### Example: Create Result With A Concrete Ref

```python
AppliedOperationResult(
    operation_id=operation.operation_id,
    status=OperationStatus.APPLIED,
    resolved_ref=DocumentRef(
        provider="demo-provider",
        kind=RefKind.ID,
        locator={"id": "new-page-id"},
    ),
    resulting_version=DocumentVersion(revision=1),
)
```

## Version Checks

If the provider advertises `ProviderCapability.VERSION_CHECK`, it should honor `UpdateDocumentOperation.expected_version` where possible.

This is the basis for optimistic concurrency.

Recommended practice:

- fail the operation when the expected version does not match
- surface a clear message in the result
- avoid silently overwriting newer content

## Recommended Provider Workflow

1. Define a settings model.
2. Validate provider configuration.
3. Advertise real capabilities.
4. Normalize or resolve refs consistently.
5. Apply each operation deterministically.
6. Return precise per-operation results.

## Common Mistakes To Avoid

- mixing host orchestration logic into the provider
- advertising unsupported capabilities
- hiding apply failures behind generic messages
- ignoring version checks when claiming `VERSION_CHECK`
- treating `DocumentRef` as provider-internal only and losing portability

## Related Documentation

- [`../concepts.md`](../concepts.md)
- [`../compatibility.md`](../compatibility.md)
- [`../api/contracts.md`](../api/contracts.md)
- [`../api/domain.md`](../api/domain.md)

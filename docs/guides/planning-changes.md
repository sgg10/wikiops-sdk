# Planning Changes

This guide explains how plugins should build operations and compose a `ChangeSet`.

## Planning Is Provider Agnostic

Plugins should emit provider-agnostic operations, not provider-specific API calls.

The provider receives those operations later and translates them into concrete persistence behavior.

## Operation Types

The current SDK supports three operation types:

- `CreateDocumentOperation`
- `UpdateDocumentOperation`
- `CreateChildDocumentOperation`

## Create A Top-Level Document

```python
from wikiops_sdk.domain import CreateDocumentOperation

operation = CreateDocumentOperation(
    title="Engineering Handbook",
    content="# Engineering Handbook\n\nManaged by WikiOps.",
)
```

Use this when the document should be created as a normal document without relying on a dedicated child-page semantic.

## Update An Existing Document

```python
from wikiops_sdk.domain import UpdateDocumentOperation

operation = UpdateDocumentOperation(
    ref=existing_ref,
    new_content="# Updated Content\n\nThis page was updated.",
)
```

Use this when the target document already exists and should be updated in place.

## Update With Optimistic Concurrency

```python
from wikiops_sdk.domain import DocumentVersion, UpdateDocumentOperation

operation = UpdateDocumentOperation(
    ref=existing_ref,
    new_content="# Updated Content\n\nThis update expects revision 5.",
    expected_version=DocumentVersion(revision=5),
)
```

This only becomes meaningful when the provider supports `ProviderCapability.VERSION_CHECK`.

## Create A Child Document

```python
from wikiops_sdk.domain import CreateChildDocumentOperation

operation = CreateChildDocumentOperation(
    parent_ref=parent_ref,
    child_title="Runbook",
    child_content="# Runbook\n\nChild page content.",
)
```

Use this when the hierarchy itself is a meaningful part of the requested mutation.

## Build A `ChangeSet`

```python
from wikiops_sdk.domain import ChangeSet

changeset = ChangeSet(
    plugin_id="wikiops.handbook",
    operations=[operation],
)
```

`plugin_id` should match the plugin manifest identity so the host can attribute the plan correctly.

## Add Planning Messages

Plugins can make their plans more useful by attaching warnings and notes.

```python
from wikiops_sdk.domain import ChangeSet, NoteMessage, WarningMessage

changeset = ChangeSet(
    plugin_id="wikiops.handbook",
    warnings=[
        WarningMessage(
            code="MISSING_SECTION_OWNER",
            message="The owner field was not provided for this section.",
        )
    ],
    notes=[
        NoteMessage(
            code="GENERATED_FROM_TEMPLATE",
            message="The default handbook template was used.",
        )
    ],
)
```

These messages are especially valuable during dry-run previews or CI enforcement flows.

## Using Resolved References In Planning

The host typically resolves aliases before planning. Plugins should then consume those references from `ExecutionContext.refs`.

```python
def plan(self, ctx):
    root_ref = ctx.refs["root"]
    return ChangeSet(
        plugin_id=self.manifest.plugin_id,
        operations=[
            CreateChildDocumentOperation(
                parent_ref=root_ref,
                child_title="Operations",
                child_content="# Operations\n\nManaged by WikiOps.",
            )
        ],
    )
```

## Recommended Planning Practices

- keep operations minimal and explicit
- use provider-agnostic data where possible
- attach versions when safe updates matter
- emit planning messages when the host or user would benefit from additional context
- avoid mixing planning with provider-specific persistence assumptions

## Common Pitfalls

- emitting child-document semantics without requiring the right provider capability
- hardcoding concrete provider IDs or paths into otherwise portable plugins
- updating content without preserving version expectations when concurrency matters
- leaving warnings and notes unused even when planning is degraded or partial

## Relationship To Applying

Planning ends with a `ChangeSet`.

Applying begins when the host passes that `ChangeSet` to a provider. This separation is one of the core architectural principles of the SDK.

## Related Documentation

- [`../concepts.md`](../concepts.md)
- [`../api/domain.md`](../api/domain.md)
- [`write-a-plugin.md`](write-a-plugin.md)
- [`write-a-provider.md`](write-a-provider.md)

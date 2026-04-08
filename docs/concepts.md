# Core Concepts

This page explains the shared vocabulary of the SDK. These concepts are the center of the public model and should be understood before implementing plugins or providers.

## `DocumentRef`

`DocumentRef` is the portable way to identify a document.

It contains:

- `provider`: the provider namespace associated with the reference
- `kind`: how the reference should be interpreted
- `locator`: provider-relevant locator data
- optional helper fields such as `alias`, `title_hint`, and `parent_alias`

The current reference kinds are:

- `RefKind.ID`
- `RefKind.PATH`
- `RefKind.ALIAS`

### Why `DocumentRef` Exists

The host and plugins should not need to know how every provider identifies documents internally. A provider can resolve a logical reference into a concrete one, but the rest of the system can still speak a provider-agnostic language.

### Example: ID-Based Reference

```python
from wikiops_sdk.domain import DocumentRef, RefKind

ref = DocumentRef(
    provider="azure-devops",
    kind=RefKind.ID,
    locator={"id": "12345"},
)
```

### Example: Path-Based Reference

```python
ref = DocumentRef(
    provider="confluence",
    kind=RefKind.PATH,
    locator={"path": "/engineering/platform/runbooks"},
)
```

### Example: Alias-Based Reference

```python
ref = DocumentRef(
    provider="azure-devops",
    kind=RefKind.ALIAS,
    locator={"alias": "team-home"},
    alias="team-home",
    title_hint="Team Home",
)
```

### Important Note

`DocumentRef` allows extra fields. This is intentional and lets providers attach provider-specific metadata without forking the SDK-wide shape. Use that flexibility carefully and document any provider-specific additions in the provider project.

## `Document`

`Document` is the portable content payload.

It contains:

- a `ref`
- a `title`
- `content`
- a `format`
- optional `version`
- arbitrary provider-specific `metadata`

At the moment, the built-in content format is `DocumentFormat.MARKDOWN`.

### Example

```python
from wikiops_sdk.domain import Document, DocumentFormat

document = Document(
    ref=ref,
    title="Platform Runbook",
    content="# Platform Runbook\n\nThis page is managed by WikiOps.",
    format=DocumentFormat.MARKDOWN,
)
```

## `DocumentVersion`

`DocumentVersion` is a provider-agnostic wrapper for optimistic concurrency data.

It can hold:

- `token`
- `revision`
- `etag`

Not every provider will support every field.

### Why It Matters

If a provider supports version checks, a plugin or host can plan safer updates by attaching an `expected_version` to an update operation.

## `ProviderCapability`

`ProviderCapability` describes which operations or behaviors a provider supports.

Current capabilities include:

- `READ_DOCUMENT`
- `CHECK_EXISTS`
- `CREATE_DOCUMENT`
- `UPDATE_DOCUMENT`
- `CREATE_CHILD_DOCUMENT`
- `BUILD_LINK`
- `RESOLVE_BY_PATH`
- `RESOLVE_BY_ID`
- `HIERARCHICAL_PAGES`
- `VERSION_CHECK`

### Why Capabilities Exist

Plugins can declare what they require. Hosts can compare those requirements with the provider capabilities before execution starts.

## Planning Messages

The SDK supports structured messages emitted during planning:

- `WarningMessage`
- `NoteMessage`

These messages are part of a `ChangeSet` and are meant to help the host surface useful feedback without relying on ad hoc logging.

### Recommended Use

- emit `WarningMessage` for risky, incomplete, or degraded planning situations
- emit `NoteMessage` for informative but non-problematic outcomes

## Operations

Operations describe intended document mutations. They are planned by plugins and applied by providers.

The current operation types are:

- `CreateDocumentOperation`
- `UpdateDocumentOperation`
- `CreateChildDocumentOperation`

### `CreateDocumentOperation`

Use when the plugin wants to create a document, typically at the top level.

It includes:

- optional `ref`
- optional `parent_ref`
- `title`
- `content`
- `format`
- `metadata`

### `UpdateDocumentOperation`

Use when the plugin wants to update an existing document.

It includes:

- `ref`
- `new_content`
- optional `expected_version`
- `format`
- `metadata`

### `CreateChildDocumentOperation`

Use when the plugin wants to create a child document beneath a known parent reference.

It includes:

- `parent_ref`
- optional `ref`
- `child_title`
- `child_content`
- `child_format`
- `child_metadata`

### Recommended Interpretation Of Parenting

The current API contains both `CreateDocumentOperation.parent_ref` and `CreateChildDocumentOperation.parent_ref`.

Recommended convention:

- prefer `CreateChildDocumentOperation` for canonical hierarchical creation
- use `CreateDocumentOperation.parent_ref` only when a provider treats parent placement as a provider-specific hint rather than a dedicated hierarchical operation

This recommendation is not enforced by the SDK itself, but documenting and following it keeps host and provider behavior easier to reason about.

## `ChangeSet`

`ChangeSet` is the main output of plugin planning.

It contains:

- `plugin_id`
- `operations`
- `warnings`
- `notes`

### Why It Matters

The host can treat a `ChangeSet` as a plan that can be:

- previewed
- validated
- inspected
- applied

### Example

```python
from wikiops_sdk.domain import ChangeSet, CreateDocumentOperation

changeset = ChangeSet(
    plugin_id="example.plugin",
    operations=[
        CreateDocumentOperation(
            title="Team Overview",
            content="# Team Overview\n\nManaged by WikiOps.",
        )
    ],
)
```

## `ExecutionContext`

`ExecutionContext` is the mutable execution-time state shared across orchestration and plugin planning.

It includes:

- execution identifiers and runtime metadata
- `refs`
- `documents`
- `plugin_config`
- `input_data`
- `runtime_vars`

### Recommended Keying Convention

The SDK does not enforce a strict key scheme for `refs` and `documents`.

Recommended convention:

- key `refs` by alias or host-managed symbolic names
- key `documents` by the same symbolic names used during orchestration

This keeps planning deterministic and avoids host-specific magic leaking into plugins.

### Example

```python
from wikiops_sdk.domain import ExecutionContext

ctx = ExecutionContext(
    run_id="run-001",
    profile_name="default",
    provider_name="azure-devops",
    dry_run=True,
    refs={"root": ref},
    plugin_config={"section_title": "Platform"},
    input_data={"team": "platform"},
)
```

## `ApplyResult` And `AppliedOperationResult`

These models represent what happened when a provider attempted to apply a `ChangeSet`.

`AppliedOperationResult` describes a single operation outcome and includes:

- `operation_id`
- `status`
- optional `message`
- optional `resolved_ref`
- optional `resulting_version`

`ApplyResult` aggregates those results for the provider execution.

### Recommended Provider Behavior

- populate `resolved_ref` for create operations when the provider generates or resolves a new concrete reference
- populate `resulting_version` when version-aware persistence is supported
- use `message` to explain skips and failures clearly

## Planning Versus Applying

One of the most important design boundaries in the SDK is the distinction between planning and applying:

- plugins create a `ChangeSet`
- providers execute that `ChangeSet`
- the host coordinates everything around them

That separation is what keeps the system extensible across multiple wiki backends and multiple automation flows.

# Constraints And Design Notes

This page documents the boundaries and caveats of the current SDK implementation.

## Non-Goals

The SDK does not include:

- a host orchestrator
- a CLI
- concrete wiki providers
- concrete documentation plugins
- provider credentials management
- runtime discovery logic
- host-side workflow policy

Those concerns belong in other repositories or projects built on top of the SDK.

## Current Scope

The current implementation focuses on:

- portable domain models
- extension contracts
- compatibility helpers

This is a deliberate choice. The SDK is not intended to become a monolithic runtime.

## Markdown-Centered Content Model

The SDK is built for Markdown-oriented documentation workflows.

Current built-in format support:

- `DocumentFormat.MARKDOWN`

If the ecosystem later needs richer formats, that should be added carefully and documented explicitly as a public API expansion.

## Current Mutation Model Is Intentionally Small

The SDK currently models only:

- create document
- update document
- create child document

It does not model:

- delete operations
- move or rename operations
- permission changes
- attachment uploads
- batch ref resolution APIs

Hosts and providers should not assume these concepts exist until the SDK models them explicitly.

## Contracts Are Structural

`DocumentationPlugin`, `DocumentProvider`, and `PluginResourceProvider` are runtime-checkable protocols, not abstract base classes with built-in behavior.

That means:

- extensions can implement the required shape without inheriting from SDK types
- the SDK does not provide runtime lifecycle hooks or default implementations

## Compatibility Is Explicit

The SDK provides rich compatibility helpers, but callers must still use them deliberately.

Examples:

- `PluginManifest` carrying a version does not validate itself automatically
- `ProviderSettings` carrying a version does not validate itself automatically

Hosts should explicitly call the compatibility helpers during extension loading and startup.

## Strict Mode Is A Policy Tool, Not A Magic Safety Layer

Strict compatibility mode helps separate developer ergonomics from release discipline, but it does not replace host validation.

Recommended use:

- non-strict mode for local extension development
- strict mode for CI and production-like checks

## `ExecutionContext` Is Mutable Shared State

`ExecutionContext` is intentionally mutable and shared. That makes it useful during orchestration, but it also means hosts should treat it as a carefully managed runtime object.

Recommended host behavior:

- construct it centrally
- populate it with validated data
- avoid ambiguous keying conventions across plugins
- document local conventions outside the SDK when needed

## Recommended Interpretation Of Ambiguous Areas

The current SDK leaves some policy choices open. These are the recommended conventions for teams adopting it.

### `refs` And `documents` Keys In `ExecutionContext`

Recommended convention:

- use logical aliases or host-managed symbolic names as keys
- keep those keys stable throughout a single execution

### `CreateDocumentOperation.parent_ref` Versus `CreateChildDocumentOperation.parent_ref`

Recommended convention:

- use `CreateChildDocumentOperation` as the canonical hierarchical creation operation
- treat `CreateDocumentOperation.parent_ref` as a provider-specific placement hint when needed

### `provider_id`, `provider_name`, And `DocumentRef.provider`

Recommended convention:

- `provider_id`: implementation identity
- `provider_name`: configured runtime identity
- `DocumentRef.provider`: provider namespace recorded on references

Document these choices in the host or provider repository if you adopt them.

## Dry-Run Caveat

`ExecutionContext` exposes `dry_run`, but `DocumentProvider.apply_changes()` does not receive the execution context directly.

That means dry-run enforcement is primarily a host concern in the current design. Providers may still choose to expose internal dry-run behavior, but the SDK does not mandate how that should work.

## Provider-Agnostic Does Not Mean Capability-Free

The SDK is provider-agnostic, not provider-oblivious.

Capability negotiation remains important because:

- some providers support hierarchical pages and others do not
- some providers support version checking and others do not
- some providers can build user-facing links and others cannot

The host should validate capability requirements before execution.

## Authoritative Sources Inside This Repository

When in doubt, these are the authoritative sources of truth:

- `src/wikiops_sdk/compat.py`
- `src/wikiops_sdk/contracts/`
- `src/wikiops_sdk/domain/`
- `tests/`

The tests are especially valuable because they encode the expected behavior of the current public API.

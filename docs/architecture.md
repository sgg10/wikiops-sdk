# Architecture

## WikiOps Ecosystem Overview

The WikiOps ecosystem is split into separate concerns:

- `wikiops-sdk`
  - public contracts
  - portable domain models
  - compatibility rules
- `wikiops` host
  - orchestration
  - extension discovery and loading
  - execution lifecycle management
  - runtime policy decisions
- plugins
  - business logic that plans documentation changes
- providers
  - infrastructure adapters that read and persist documents in a concrete wiki system

The design intent is to keep the SDK stable and provider-agnostic while allowing multiple hosts, plugins, and providers to interoperate.

## Responsibility Boundaries

### The SDK

The SDK defines the common language only.

Examples:

- what a document reference looks like
- what a planned operation looks like
- how a plugin announces required capabilities
- how a provider reports apply results
- how compatibility between host and extensions is checked

### Plugins

Plugins own business logic.

Examples:

- deciding what content should exist
- reading runtime inputs and configuration
- deciding whether to create, update, or skip documents
- emitting warnings and notes for the host or user

Plugins do not persist data directly through the SDK contracts. They plan changes.

### Providers

Providers own infrastructure and persistence.

Examples:

- resolving references for a specific wiki system
- checking whether a document exists
- reading a document from the remote system
- generating user-facing links
- applying planned operations and returning execution results

Providers do not own the business decision of what should change. They execute requested changes.

### The Host

The host is responsible for orchestration and policy.

Examples:

- discovering plugins and providers through entry points
- validating compatibility and runtime constraints
- instantiating extensions
- validating user configuration and inputs
- building the `ExecutionContext`
- deciding how dry-run mode is enforced
- deciding how warnings, notes, and apply failures are surfaced

This repository documents the SDK side of that contract. Host-specific execution guidance belongs in the host project documentation.

## Intended Dependency Direction

```text
plugin -> sdk <- host
provider -> sdk <- host
```

This means:

- plugins depend on the SDK, not on the host internals
- providers depend on the SDK, not on plugin internals
- the host depends on the SDK to speak to both plugins and providers

## Public Module Map

### `wikiops_sdk.compat`

Defines version and compatibility rules for:

- SDK package version
- plugin API version
- provider API version
- Python runtime compatibility
- strict versus non-strict compatibility behavior

### `wikiops_sdk.contracts`

Defines extension contracts:

- `DocumentationPlugin`
- `DocumentProvider`
- `PluginResourceProvider`
- associated manifest, config, input, and settings models

### `wikiops_sdk.domain`

Defines provider-agnostic shared data models:

- documents and references
- planned operations and change sets
- execution context
- apply results

## Extension Discovery Model

The SDK reserves these entry point groups:

- `wikiops.plugins`
- `wikiops.providers`

The SDK does not perform discovery itself. It only centralizes the canonical group names so the host and extensions do not rely on duplicated string literals.

## Design Principles

### Provider Agnostic Domain

The domain models are intentionally portable. A `DocumentRef` can represent a document in multiple wiki systems without making the rest of the SDK provider-specific.

### Documentation As Code

The core content model is Markdown-oriented, but the SDK still exposes richer concepts than raw files or strings: references, versions, capabilities, operations, and results.

### Stable Extension Surface

The SDK exists to make plugins and providers durable across host changes. Compatibility rules and version helpers are part of that promise.

### Clear Separation Of Planning And Persistence

Plugins plan. Providers persist. The host orchestrates. The SDK defines the boundary objects that make that separation practical.

## Current Implementation Boundaries

The current SDK is intentionally narrow:

- only `DocumentFormat.MARKDOWN` is built in
- only create, update, and create-child operations are modeled
- no concrete provider behavior is embedded in the SDK
- no plugin runtime or base implementation is provided beyond protocols and models

For the precise caveats and recommendations around these boundaries, see [`reference/constraints.md`](reference/constraints.md).

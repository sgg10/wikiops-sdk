# WikiOps SDK Documentation

This documentation describes the current implementation of `wikiops-sdk` and the design intentions behind it.

It is written for:

- plugin authors
- provider authors
- host authors integrating the SDK
- AI agents that need accurate repository boundaries and public API semantics

## What The SDK Is

`wikiops-sdk` is the contract layer of the WikiOps ecosystem.

It defines:

- portable domain models
- public extension protocols
- compatibility rules

It does not define:

- host orchestration
- a CLI
- concrete providers
- concrete plugins
- project-specific business logic

## Documentation Structure

### Conceptual Documentation

- [`getting-started.md`](getting-started.md): package purpose, structure, and reading strategy
- [`architecture.md`](architecture.md): how the SDK fits into the WikiOps ecosystem
- [`concepts.md`](concepts.md): the shared vocabulary of the SDK
- [`compatibility.md`](compatibility.md): versioning, strict mode, and compatibility helpers

### Guides

- [`guides/write-a-plugin.md`](guides/write-a-plugin.md): how to implement a documentation plugin
- [`guides/write-a-provider.md`](guides/write-a-provider.md): how to implement a document provider
- [`guides/planning-changes.md`](guides/planning-changes.md): how to build operations and change sets

### API Reference

- [`api/index.md`](api/index.md): API map and recommended import paths
- [`api/top-level.md`](api/top-level.md): top-level package exports
- [`api/compat.md`](api/compat.md): compatibility API
- [`api/contracts.md`](api/contracts.md): plugin, provider, and resource contracts
- [`api/domain.md`](api/domain.md): domain and result models

### Constraints And Shared Vocabulary

- [`reference/constraints.md`](reference/constraints.md): design limits, non-goals, and caveats
- [`reference/glossary.md`](reference/glossary.md): canonical terminology

## Reading Paths

### If You Are Writing A Plugin

1. [`getting-started.md`](getting-started.md)
2. [`concepts.md`](concepts.md)
3. [`guides/write-a-plugin.md`](guides/write-a-plugin.md)
4. [`api/contracts.md`](api/contracts.md)
5. [`api/domain.md`](api/domain.md)

### If You Are Writing A Provider

1. [`getting-started.md`](getting-started.md)
2. [`concepts.md`](concepts.md)
3. [`guides/write-a-provider.md`](guides/write-a-provider.md)
4. [`api/contracts.md`](api/contracts.md)
5. [`api/domain.md`](api/domain.md)

### If You Are Integrating The SDK Into A Host

1. [`architecture.md`](architecture.md)
2. [`compatibility.md`](compatibility.md)
3. [`concepts.md`](concepts.md)
4. [`reference/constraints.md`](reference/constraints.md)

## Documentation Scope

This documentation is implementation-focused. It describes what the SDK currently exposes and how it is intended to be used. Where the current API leaves room for host-specific policy, the docs call that out explicitly and provide recommended conventions without pretending those conventions are enforced by the SDK itself.

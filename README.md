# wikiops-sdk

`wikiops-sdk` is the public SDK for the WikiOps ecosystem.

It defines the shared language used by the WikiOps host, documentation plugins, and document providers. The package is intentionally small and focused: it provides portable domain models, public extension contracts, and compatibility rules, but it does not implement orchestration, a CLI, concrete providers, or concrete plugins.

## What This Repository Contains

- Provider-agnostic domain models for documentation planning and application.
- Public protocols and Pydantic models for plugins and providers.
- Compatibility helpers for SDK, plugin, provider, and Python runtime versions.
- A strict automated test suite that validates the public SDK behavior.
- A dedicated `docs/` directory with conceptual guides and API reference material.

## What This Repository Does Not Contain

- The WikiOps host application.
- A CLI.
- A scheduler or orchestrator.
- Provider implementations such as Azure DevOps Wiki or Confluence.
- Documentation plugin implementations.

In the intended ecosystem, the relationship is:

```text
plugin -> sdk <- host
provider -> sdk <- host
```

The SDK is the stable contract layer in the middle.

## Why This Exists

WikiOps treats documentation as code. The long-term goal is to automate how Markdown-based documentation is read, transformed, generated, and persisted across multiple wiki systems while keeping business logic, provider infrastructure, and orchestration decoupled.

This SDK gives all participants a common model for concepts such as:

- `DocumentRef`
- `Document`
- `ChangeSet`
- `ExecutionContext`
- `ProviderCapability`
- `ApplyResult`

## Repository Layout

```text
src/wikiops_sdk/
  compat.py
  contracts/
  domain/
docs/
tests/
```

## Documentation Map

Start here depending on your role:

- New to the project: [`docs/index.md`](docs/index.md)
- Need the architectural model: [`docs/architecture.md`](docs/architecture.md)
- Need the core concepts: [`docs/concepts.md`](docs/concepts.md)
- Need compatibility rules: [`docs/compatibility.md`](docs/compatibility.md)
- Writing a plugin: [`docs/guides/write-a-plugin.md`](docs/guides/write-a-plugin.md)
- Writing a provider: [`docs/guides/write-a-provider.md`](docs/guides/write-a-provider.md)
- Planning change sets: [`docs/guides/planning-changes.md`](docs/guides/planning-changes.md)
- Need API reference: [`docs/api/index.md`](docs/api/index.md)
- Need SDK constraints and caveats: [`docs/reference/constraints.md`](docs/reference/constraints.md)

## Recommended Reading Order

For plugin authors:

1. [`docs/getting-started.md`](docs/getting-started.md)
2. [`docs/concepts.md`](docs/concepts.md)
3. [`docs/guides/write-a-plugin.md`](docs/guides/write-a-plugin.md)
4. [`docs/api/contracts.md`](docs/api/contracts.md)
5. [`docs/api/domain.md`](docs/api/domain.md)

For provider authors:

1. [`docs/getting-started.md`](docs/getting-started.md)
2. [`docs/concepts.md`](docs/concepts.md)
3. [`docs/guides/write-a-provider.md`](docs/guides/write-a-provider.md)
4. [`docs/api/contracts.md`](docs/api/contracts.md)
5. [`docs/api/domain.md`](docs/api/domain.md)

For host authors:

1. [`docs/architecture.md`](docs/architecture.md)
2. [`docs/concepts.md`](docs/concepts.md)
3. [`docs/compatibility.md`](docs/compatibility.md)
4. [`docs/reference/constraints.md`](docs/reference/constraints.md)

## Import Paths

The top-level package mainly exposes compatibility helpers:

```python
from wikiops_sdk import ensure_plugin_api_compatible
```

Contracts and domain models are intentionally imported from subpackages:

```python
from wikiops_sdk.contracts import DocumentationPlugin, DocumentProvider, PluginManifest
from wikiops_sdk.domain import ChangeSet, DocumentRef, ExecutionContext
```

## Host Documentation

This repository documents the SDK only. The WikiOps host application should maintain its own documentation for orchestration, runtime loading, command-line workflows, and deployment concerns.

## Status

The current SDK implementation is intentionally narrow and precise:

- Markdown is the only built-in content format.
- The current operation model supports create, update, and create-child flows.
- Compatibility defaults to a `same_major` policy.
- The SDK is designed to be provider-agnostic and orchestration-agnostic.

## Tests

The repository ships with a strict test suite and coverage thresholds.

```bash
poetry install --with tests
poetry run pytest
```

The tests also serve as executable examples of the current public API.

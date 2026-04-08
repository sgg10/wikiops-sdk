# Getting Started

## Purpose

`wikiops-sdk` provides the shared language for the WikiOps ecosystem.

If you are building any of the following, this is the package you consume:

- a documentation plugin
- a document provider
- a host integration layer that orchestrates plugins and providers

## What The SDK Gives You

The SDK is organized into three main surfaces:

- `wikiops_sdk.compat`
  - compatibility constants
  - version parsing and validation helpers
  - strict compatibility mode support
  - Python runtime checks
- `wikiops_sdk.contracts`
  - public protocols for plugins and providers
  - resource access protocol for plugin-owned bundled files
  - manifest, config, input, and settings models
- `wikiops_sdk.domain`
  - provider-agnostic document and reference models
  - execution context model
  - mutation operations and change sets
  - apply result models

## What The SDK Does Not Do

The SDK intentionally avoids runtime concerns that belong in the host:

- discovering entry points and instantiating extensions
- reading configuration files
- validating provider-specific credentials
- orchestrating execution order
- deciding dry-run policy
- persisting documents to a concrete wiki system

## Package Layout

```text
wikiops_sdk/
  __init__.py
  compat.py
  contracts/
    __init__.py
    plugin.py
    provider.py
    resources.py
  domain/
    __init__.py
    context.py
    models.py
    results.py
```

## Recommended Import Style

Use the top-level package for compatibility helpers only:

```python
from wikiops_sdk import ensure_plugin_api_compatible
```

Use subpackages for contracts and models:

```python
from wikiops_sdk.contracts import DocumentationPlugin, PluginManifest
from wikiops_sdk.domain import ChangeSet, DocumentRef, ExecutionContext
```

This keeps imports explicit and aligned with the intended API boundaries.

## Python And Dependency Requirements

Current SDK requirements:

- Python `>=3.10,<4.0`
- Pydantic v2

The SDK also exposes `MIN_SUPPORTED_PYTHON` and runtime helpers through `wikiops_sdk.compat`.

## Development Workflow

Install the project and test dependencies with Poetry:

```bash
poetry install --with tests
```

Run the test suite:

```bash
poetry run pytest
```

## What To Read Next

- To understand how the SDK fits into the broader system, continue with [`architecture.md`](architecture.md).
- To understand the meaning of the core models, continue with [`concepts.md`](concepts.md).
- To implement extensions, continue with the guides in [`guides/`](guides/).

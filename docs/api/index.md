# API Reference

This section maps the public API exposed by the SDK.

## Import Strategy

The SDK deliberately exposes different surfaces from different import paths.

### Top-Level Package

Use `wikiops_sdk` for compatibility helpers and constants.

- [`top-level.md`](top-level.md)

### Contracts Package

Use `wikiops_sdk.contracts` for public extension contracts.

- [`contracts.md`](contracts.md)

### Domain Package

Use `wikiops_sdk.domain` for provider-agnostic shared models.

- [`domain.md`](domain.md)

### Compatibility Module

Use `wikiops_sdk.compat` for detailed compatibility behavior and exception types.

- [`compat.md`](compat.md)

## Recommended Imports

```python
from wikiops_sdk import ensure_plugin_api_compatible
from wikiops_sdk.contracts import DocumentationPlugin, DocumentProvider, PluginManifest
from wikiops_sdk.domain import ChangeSet, DocumentRef, ExecutionContext
```

## Important Note

The top-level package does not re-export the full contracts and domain surface. That is intentional. If you need plugin/provider contracts or domain models, import them from `wikiops_sdk.contracts` and `wikiops_sdk.domain`.

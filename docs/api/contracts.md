# `wikiops_sdk.contracts`

The contracts package defines the public extension interfaces for plugins, providers, and plugin-owned bundled resources.

## Re-Exported Public Surface

`wikiops_sdk.contracts` exposes:

- `DocumentationPlugin`
- `DocumentProvider`
- `PluginConfigModel`
- `PluginInputModel`
- `PluginManifest`
- `PluginResourceProvider`
- `ProviderSettings`

## Plugin Contracts

### `PluginManifest`

`PluginManifest` is the metadata model for a documentation plugin.

Fields:

- `plugin_id`
- `display_name`
- `version`
- `plugin_api_version`
- `description`
- `required_capabilities`

Convenience API:

- `PluginManifest.for_current_api(...)`
- `resolved_plugin_api_version(...)`

Recommended usage:

```python
from wikiops_sdk.contracts import PluginManifest
from wikiops_sdk.domain import ProviderCapability

manifest = PluginManifest.for_current_api(
    plugin_id="wikiops.example",
    display_name="Example Plugin",
    version="0.1.0",
    description="Example planning plugin.",
    required_capabilities={ProviderCapability.CREATE_DOCUMENT},
)
```

### `PluginConfigModel`

Base class for plugin configuration payloads.

Subclasses should define the plugin's configuration schema.

### `PluginInputModel`

Base class for plugin execution input payloads.

Subclasses should define the runtime input schema.

### `DocumentationPlugin`

Runtime-checkable protocol for documentation plugins.

Expected members:

- `manifest`
- `resources`
- `get_config_model()`
- `get_input_model()`
- `required_ref_aliases(...)`
- `plan(ctx)`

This is a structural protocol, not a base class with behavior.

## Provider Contracts

### `ProviderSettings`

Base configuration model for provider settings.

Fields:

- `provider_name`
- `provider_api_version`

Subclasses should add provider-specific fields such as base URLs, credentials, namespaces, or profile options.

### `DocumentProvider`

Runtime-checkable protocol for backend providers.

Expected members:

- `provider_id`
- `capabilities()`
- `validate_settings()`
- `resolve_ref(ref, ctx)`
- `exists(ref)`
- `get_document(ref)`
- `build_link(ref)`
- `apply_changes(changeset)`

This is also a structural protocol.

## Resource Contract

### `PluginResourceProvider`

Read-only accessor for files bundled with a plugin.

Methods:

- `has(relative_path)`
- `read_text(relative_path, encoding="utf-8")`
- `list(prefix="")`

This contract is intentionally small because it is meant to expose packaged resources without leaking storage details into plugins.

## Design Notes

### Protocols Instead Of Base Classes

The SDK uses runtime-checkable protocols so extension authors can implement the required surface without inheriting from SDK-specific runtime classes.

### Thin Base Models

The SDK provides only the minimum base Pydantic models needed to describe configuration and input shapes. Validation and lifecycle policies remain host concerns.

### Compatibility Is Adjacent, Not Automatic

Contracts may carry version data, but compatibility validation should still be performed through `wikiops_sdk.compat`.

## Related Documentation

- [`../guides/write-a-plugin.md`](../guides/write-a-plugin.md)
- [`../guides/write-a-provider.md`](../guides/write-a-provider.md)
- [`../compatibility.md`](../compatibility.md)

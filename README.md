# wikiops-sdk
Public SDK for WikiOps plugins and integrations. Provides the shared contracts, domain models, compatibility rules, and extension interfaces needed to build providers and documentation plugins.

## Compatibility Model

The SDK separates package versioning from extension API versioning:

- `SDK_VERSION`: version of the installed `wikiops-sdk` package.
- `PLUGIN_API_VERSION`: public API version for documentation plugins.
- `PROVIDER_API_VERSION`: public API version for document providers.

Compatibility helpers live in `wikiops_sdk.compat`:

- `is_plugin_api_compatible(...)` / `ensure_plugin_api_compatible(...)`
- `is_provider_api_compatible(...)` / `ensure_provider_api_compatible(...)`
- `is_python_compatible(...)` / `ensure_python_compatible(...)`

### Developer Experience Mode (No Manual Plugin API Version)

Plugin manifests can omit `plugin_api_version` during local development.

- In non-strict mode (default), omitted plugin/provider API versions are resolved
  to the SDK defaults (`PLUGIN_API_VERSION` and `PROVIDER_API_VERSION`).
- In strict mode, omitted versions raise an error so CI and production can enforce
  explicit compatibility declarations.

Strict mode is controlled by `WIKIOPS_SDK_STRICT_COMPAT`:

- Truthy values: `1`, `true`, `yes`, `on`
- Falsy values: `0`, `false`, `no`, `off`

Example:

```python
from wikiops_sdk.compat import ensure_plugin_api_compatible

# local/dev: resolves missing version automatically
ensure_plugin_api_compatible(None)

# CI/prod strict mode
# export WIKIOPS_SDK_STRICT_COMPAT=true
```

You can also build a manifest pinned to the current API via
`PluginManifest.for_current_api(...)`.

Default policy is `same_major`, which means API `1.x` components are compatible
with API `1.y` hosts, while API `2.x` is considered breaking for API `1.x`.

The SDK also centralizes extension discovery constants:

- `PLUGIN_ENTRYPOINT_GROUP = "wikiops.plugins"`
- `PROVIDER_ENTRYPOINT_GROUP = "wikiops.providers"`

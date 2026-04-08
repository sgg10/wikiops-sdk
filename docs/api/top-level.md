# Top-Level Package API

The top-level package `wikiops_sdk` currently re-exports compatibility helpers and constants.

## Exported Names

- `DEFAULT_COMPATIBILITY_POLICY`
- `MIN_SUPPORTED_PYTHON`
- `PLUGIN_API_VERSION`
- `PLUGIN_ENTRYPOINT_GROUP`
- `PROVIDER_API_VERSION`
- `PROVIDER_ENTRYPOINT_GROUP`
- `SDK_VERSION`
- `STRICT_COMPAT_MODE_ENV`
- `ensure_plugin_api_compatible`
- `ensure_provider_api_compatible`
- `ensure_python_compatible`
- `get_sdk_version`
- `is_plugin_api_compatible`
- `is_provider_api_compatible`
- `is_python_compatible`
- `is_strict_compat_mode_enabled`
- `resolve_plugin_api_version`
- `resolve_provider_api_version`

## Example

```python
from wikiops_sdk import ensure_plugin_api_compatible, PLUGIN_ENTRYPOINT_GROUP

ensure_plugin_api_compatible("1.0.0")
print(PLUGIN_ENTRYPOINT_GROUP)
```

## What Is Not Re-Exported Here

The following are intentionally not exported at the top level:

- plugin and provider protocols
- domain models such as `DocumentRef` and `ChangeSet`
- compatibility exception classes

For those, use the dedicated subpackages.

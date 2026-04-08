# `wikiops_sdk.compat`

`wikiops_sdk.compat` centralizes compatibility rules, version parsing, strict mode behavior, and compatibility-related exceptions.

## Constants

### `SDK_DISTRIBUTION`

The distribution name used for installed package metadata lookup.

### `LOCAL_SDK_VERSION_FALLBACK`

Fallback version returned when installed package metadata is unavailable.

### `PLUGIN_API_VERSION`

Current plugin API version expected by the SDK.

### `PROVIDER_API_VERSION`

Current provider API version expected by the SDK.

### `PLUGIN_ENTRYPOINT_GROUP`

Canonical entry point group for plugins: `wikiops.plugins`.

### `PROVIDER_ENTRYPOINT_GROUP`

Canonical entry point group for providers: `wikiops.providers`.

### `STRICT_COMPAT_MODE_ENV`

Environment variable name used to enable strict compatibility mode.

### `MIN_SUPPORTED_PYTHON`

Minimum supported Python version tuple.

### `DEFAULT_COMPATIBILITY_POLICY`

Current default compatibility policy, which is `same_major`.

## Exceptions

### `CompatibilityError`

Base compatibility failure.

### `InvalidVersionError`

Raised when a provided version string does not match `major.minor.patch`.

### `PluginAPIIncompatibleError`

Raised when a plugin API version is incompatible with the host SDK.

### `ProviderAPIIncompatibleError`

Raised when a provider API version is incompatible with the host SDK.

### `PythonRuntimeIncompatibleError`

Raised when the running Python version is below the supported minimum.

## Version Helpers

### `get_sdk_version() -> str`

Returns the installed SDK version or `LOCAL_SDK_VERSION_FALLBACK` when metadata is unavailable.

### `parse_api_version(api_version: str) -> tuple[int, int, int]`

Parses a semantic API version in `major.minor.patch` format.

Example:

```python
from wikiops_sdk.compat import parse_api_version

major, minor, patch = parse_api_version("1.2.3")
```

## Strict Mode Helpers

### `is_strict_compat_mode_enabled(raw_value: str | None = None) -> bool`

Returns whether strict compatibility mode is enabled.

If `raw_value` is omitted, the helper reads `WIKIOPS_SDK_STRICT_COMPAT` from the environment.

### `resolve_plugin_api_version(...)`

Normalizes or resolves the effective plugin API version.

Behavior:

- non-strict mode: missing value resolves to `PLUGIN_API_VERSION`
- strict mode: missing value raises `InvalidVersionError`

### `resolve_provider_api_version(...)`

Equivalent helper for provider API versions.

## Compatibility Checks

### `is_api_compatible(candidate_api_version, host_api_version, *, policy=...)`

Generic compatibility boolean helper.

### `ensure_api_compatible(candidate_api_version, host_api_version, *, policy=..., subject=..., error_cls=...)`

Generic compatibility enforcement helper that raises on mismatch.

### `is_plugin_api_compatible(...)`

Boolean plugin-specific compatibility helper.

### `ensure_plugin_api_compatible(...)`

Plugin-specific compatibility enforcement helper.

### `is_provider_api_compatible(...)`

Boolean provider-specific compatibility helper.

### `ensure_provider_api_compatible(...)`

Provider-specific compatibility enforcement helper.

## Python Runtime Checks

### `is_python_compatible(python_version: tuple[int, int] | None = None) -> bool`

Returns whether a given or current Python runtime is compatible.

### `ensure_python_compatible(python_version: tuple[int, int] | None = None) -> None`

Raises `PythonRuntimeIncompatibleError` if the runtime is unsupported.

## Usage Examples

### Validate A Plugin In CI

```python
from wikiops_sdk.compat import ensure_plugin_api_compatible

ensure_plugin_api_compatible(plugin.manifest.plugin_api_version, strict=True)
```

### Allow Omitted Version During Local Development

```python
from wikiops_sdk.compat import resolve_plugin_api_version

effective_version = resolve_plugin_api_version(None, strict=False)
```

### Validate Python Runtime

```python
from wikiops_sdk.compat import ensure_python_compatible

ensure_python_compatible()
```

## Design Note

The compatibility module is the normative place for these rules. Models such as `PluginManifest` and `ProviderSettings` may carry version information, but compatibility decisions should be centralized through this module rather than reimplemented elsewhere.

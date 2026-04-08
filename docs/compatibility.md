# Compatibility

Compatibility rules are defined in `wikiops_sdk.compat` and re-exported at the top level of the package.

This module exists so that hosts, plugins, and providers share one compatibility policy instead of duplicating version checks or string literals across repositories.

## Core Constants

The current implementation defines:

- `SDK_DISTRIBUTION`
- `SDK_VERSION`
- `LOCAL_SDK_VERSION_FALLBACK`
- `PLUGIN_API_VERSION`
- `PROVIDER_API_VERSION`
- `PLUGIN_ENTRYPOINT_GROUP`
- `PROVIDER_ENTRYPOINT_GROUP`
- `MIN_SUPPORTED_PYTHON`
- `STRICT_COMPAT_MODE_ENV`
- `DEFAULT_COMPATIBILITY_POLICY`

## SDK Version Versus API Versions

These values do different jobs.

### `SDK_VERSION`

This is the version of the installed `wikiops-sdk` package.

When package metadata is unavailable, the SDK falls back to `0.0.0+local`.

This is useful in local development contexts where installed distribution metadata may not exist yet.

### `PLUGIN_API_VERSION`

This is the current public API version expected by the SDK for documentation plugins.

### `PROVIDER_API_VERSION`

This is the current public API version expected by the SDK for providers.

## Compatibility Policy

The default policy is:

```python
DEFAULT_COMPATIBILITY_POLICY = "same_major"
```

This means:

- plugin or provider API `1.0.0` is compatible with host API `1.2.0`
- plugin or provider API `1.9.1` is compatible with host API `1.0.0`
- plugin or provider API `2.0.0` is not compatible with host API `1.0.0`

The module also supports an `exact` policy for callers that want an exact match.

## Strict Versus Non-Strict Mode

The SDK supports a strict compatibility mode controlled either explicitly or through the `WIKIOPS_SDK_STRICT_COMPAT` environment variable.

### Non-Strict Mode

Non-strict mode is intended to improve local developer experience.

When a plugin or provider API version is omitted:

- plugin versions resolve to `PLUGIN_API_VERSION`
- provider versions resolve to `PROVIDER_API_VERSION`

This is especially helpful during early plugin development.

### Strict Mode

Strict mode is intended for CI and production-like environments.

When a plugin or provider API version is omitted, the SDK raises an `InvalidVersionError` instead of silently resolving the current default.

### Accepted Environment Values

Truthy values:

- `1`
- `true`
- `yes`
- `on`

Falsy values:

- `0`
- `false`
- `no`
- `off`
- empty string

## Recommended Usage Patterns

### Host Side Validation

Hosts should validate compatibility before execution:

```python
from wikiops_sdk import ensure_plugin_api_compatible, ensure_provider_api_compatible

ensure_plugin_api_compatible(plugin.manifest.plugin_api_version, strict=True)
ensure_provider_api_compatible(settings.provider_api_version, strict=True)
```

### Local Development Validation

For local developer workflows:

```python
from wikiops_sdk import ensure_plugin_api_compatible

ensure_plugin_api_compatible(None, strict=False)
```

This allows a plugin to omit the version temporarily while still following the SDK's compatibility rules.

### Python Runtime Validation

```python
from wikiops_sdk import ensure_python_compatible

ensure_python_compatible()
```

This can be used by a host during startup or by CI checks.

## Resolving Versions Explicitly

If a caller wants the normalized effective version, use the resolver helpers:

```python
from wikiops_sdk import resolve_plugin_api_version, resolve_provider_api_version

plugin_api_version = resolve_plugin_api_version(None, strict=False)
provider_api_version = resolve_provider_api_version("1.0.0", strict=True)
```

## Exceptions

The module defines these exception types:

- `CompatibilityError`
- `InvalidVersionError`
- `PluginAPIIncompatibleError`
- `ProviderAPIIncompatibleError`
- `PythonRuntimeIncompatibleError`

Hosts should treat these as explicit signals that an extension or runtime should not proceed.

## Entry Point Group Names

The SDK centralizes the canonical extension discovery groups:

```python
PLUGIN_ENTRYPOINT_GROUP = "wikiops.plugins"
PROVIDER_ENTRYPOINT_GROUP = "wikiops.providers"
```

The SDK does not itself perform discovery, but these constants ensure the host and extensions share the same public names.

## Design Rationale

The compatibility layer exists to solve two different problems:

- ecosystem stability across SDK evolution
- smooth developer workflows during extension development

That is why the SDK supports both strict validation and a more forgiving local development path.

## Caveat

`ProviderSettings` and `PluginManifest` can carry API version information, but those models do not enforce compatibility by themselves. Compatibility is enforced only when callers explicitly use the helpers in `wikiops_sdk.compat`.

"""Compatibility rules and helpers for hosts, plugins, and providers."""

from __future__ import annotations

import os
import re
import sys
from importlib.metadata import PackageNotFoundError, version as distribution_version
from typing import Final, Literal, Type

SDK_DISTRIBUTION: Final[str] = "wikiops-sdk"
LOCAL_SDK_VERSION_FALLBACK: Final[str] = "0.0.0+local"

PLUGIN_API_VERSION: Final[str] = "1.0.0"
PROVIDER_API_VERSION: Final[str] = "1.0.0"

PLUGIN_ENTRYPOINT_GROUP: Final[str] = "wikiops.plugins"
PROVIDER_ENTRYPOINT_GROUP: Final[str] = "wikiops.providers"
STRICT_COMPAT_MODE_ENV: Final[str] = "WIKIOPS_SDK_STRICT_COMPAT"

_STRICT_TRUE_VALUES: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on"})
_STRICT_FALSE_VALUES: Final[frozenset[str]] = frozenset(
    {"0", "false", "no", "off", ""}
)

MIN_SUPPORTED_PYTHON: Final[tuple[int, int]] = (3, 10)

CompatibilityPolicy = Literal["same_major", "exact"]
DEFAULT_COMPATIBILITY_POLICY: Final[CompatibilityPolicy] = "same_major"

_SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)$"
)


class CompatibilityError(RuntimeError):
    """Base error raised when a compatibility check fails."""


class InvalidVersionError(CompatibilityError):
    """Raised when a version does not follow ``major.minor.patch`` format."""


class PluginAPIIncompatibleError(CompatibilityError):
    """Raised when a plugin API version is incompatible with the host."""


class ProviderAPIIncompatibleError(CompatibilityError):
    """Raised when a provider API version is incompatible with the host."""


class PythonRuntimeIncompatibleError(CompatibilityError):
    """Raised when the running Python version is not supported by the SDK."""


def get_sdk_version() -> str:
    """Return the installed SDK version, or a local fallback when unavailable."""

    try:
        return distribution_version(SDK_DISTRIBUTION)
    except PackageNotFoundError:
        return LOCAL_SDK_VERSION_FALLBACK


SDK_VERSION: Final[str] = get_sdk_version()


def is_strict_compat_mode_enabled(raw_value: str | None = None) -> bool:
    """Return whether strict compatibility mode is enabled.

    If ``raw_value`` is omitted, this reads ``STRICT_COMPAT_MODE_ENV`` from
    the process environment. Accepted truthy values are ``1``, ``true``,
    ``yes``, and ``on``. Accepted falsy values are ``0``, ``false``,
    ``no``, ``off``, and the empty string.
    """

    if raw_value is None:
        raw_value = os.getenv(STRICT_COMPAT_MODE_ENV)

    if raw_value is None:
        return False

    normalized = raw_value.strip().lower()
    if normalized in _STRICT_TRUE_VALUES:
        return True
    if normalized in _STRICT_FALSE_VALUES:
        return False

    raise ValueError(
        f"Invalid strict compatibility flag '{raw_value}'. Supported values are "
        "1/0, true/false, yes/no, and on/off."
    )


def parse_api_version(api_version: str) -> tuple[int, int, int]:
    """Parse an API version in ``major.minor.patch`` format."""

    match = _SEMVER_PATTERN.fullmatch(api_version.strip())
    if match is None:
        raise InvalidVersionError(
            f"Invalid API version '{api_version}'. Expected 'major.minor.patch'."
        )

    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def resolve_plugin_api_version(
    plugin_api_version: str | None,
    *,
    strict: bool | None = None,
) -> str:
    """Resolve a plugin API version, applying strict-mode fallback rules.

    In non-strict mode, an omitted value resolves to ``PLUGIN_API_VERSION``.
    In strict mode, omitted values raise ``InvalidVersionError``.
    """

    resolved_strict = _resolve_strict_mode(strict)
    if plugin_api_version is None or plugin_api_version.strip() == "":
        if resolved_strict:
            raise InvalidVersionError(
                "Plugin API version is required when strict compatibility "
                "mode is enabled."
            )
        return PLUGIN_API_VERSION

    normalized = plugin_api_version.strip()
    parse_api_version(normalized)
    return normalized


def resolve_provider_api_version(
    provider_api_version: str | None,
    *,
    strict: bool | None = None,
) -> str:
    """Resolve a provider API version, applying strict-mode fallback rules.

    In non-strict mode, an omitted value resolves to ``PROVIDER_API_VERSION``.
    In strict mode, omitted values raise ``InvalidVersionError``.
    """

    resolved_strict = _resolve_strict_mode(strict)
    if provider_api_version is None or provider_api_version.strip() == "":
        if resolved_strict:
            raise InvalidVersionError(
                "Provider API version is required when strict compatibility "
                "mode is enabled."
            )
        return PROVIDER_API_VERSION

    normalized = provider_api_version.strip()
    parse_api_version(normalized)
    return normalized


def is_api_compatible(
    candidate_api_version: str,
    host_api_version: str,
    *,
    policy: CompatibilityPolicy = DEFAULT_COMPATIBILITY_POLICY,
) -> bool:
    """Return whether a candidate API version is compatible with a host API version."""

    candidate = parse_api_version(candidate_api_version)
    host = parse_api_version(host_api_version)
    return _match_policy(candidate, host, policy)


def ensure_api_compatible(
    candidate_api_version: str,
    host_api_version: str,
    *,
    policy: CompatibilityPolicy = DEFAULT_COMPATIBILITY_POLICY,
    subject: str = "component",
    error_cls: Type[CompatibilityError] = CompatibilityError,
) -> None:
    """Raise a compatibility error when candidate and host API versions mismatch."""

    try:
        candidate = parse_api_version(candidate_api_version)
    except InvalidVersionError as exc:
        raise InvalidVersionError(
            f"Invalid {subject} API version '{candidate_api_version}'. "
            "Expected 'major.minor.patch'."
        ) from exc

    host = parse_api_version(host_api_version)
    if _match_policy(candidate, host, policy):
        return

    raise error_cls(
        f"Incompatible {subject} API version '{candidate_api_version}' for host "
        f"API '{host_api_version}' with policy '{policy}'."
    )


def is_plugin_api_compatible(
    plugin_api_version: str | None,
    *,
    policy: CompatibilityPolicy = DEFAULT_COMPATIBILITY_POLICY,
    strict: bool | None = None,
) -> bool:
    """Return whether a plugin API version is compatible with this SDK.

    When strict mode is disabled, omitted versions are treated as the current
    ``PLUGIN_API_VERSION``.
    """

    try:
        resolved_version = resolve_plugin_api_version(
            plugin_api_version,
            strict=strict,
        )
        return is_api_compatible(
            resolved_version,
            PLUGIN_API_VERSION,
            policy=policy,
        )
    except InvalidVersionError:
        return False


def ensure_plugin_api_compatible(
    plugin_api_version: str | None,
    *,
    policy: CompatibilityPolicy = DEFAULT_COMPATIBILITY_POLICY,
    strict: bool | None = None,
) -> None:
    """Raise when a plugin API version is not compatible with this SDK."""

    resolved_version = resolve_plugin_api_version(
        plugin_api_version,
        strict=strict,
    )

    ensure_api_compatible(
        resolved_version,
        PLUGIN_API_VERSION,
        policy=policy,
        subject="plugin",
        error_cls=PluginAPIIncompatibleError,
    )


def is_provider_api_compatible(
    provider_api_version: str | None,
    *,
    policy: CompatibilityPolicy = DEFAULT_COMPATIBILITY_POLICY,
    strict: bool | None = None,
) -> bool:
    """Return whether a provider API version is compatible with this SDK.

    When strict mode is disabled, omitted versions are treated as the current
    ``PROVIDER_API_VERSION``.
    """

    try:
        resolved_version = resolve_provider_api_version(
            provider_api_version,
            strict=strict,
        )
        return is_api_compatible(
            resolved_version,
            PROVIDER_API_VERSION,
            policy=policy,
        )
    except InvalidVersionError:
        return False


def ensure_provider_api_compatible(
    provider_api_version: str | None,
    *,
    policy: CompatibilityPolicy = DEFAULT_COMPATIBILITY_POLICY,
    strict: bool | None = None,
) -> None:
    """Raise when a provider API version is not compatible with this SDK."""

    resolved_version = resolve_provider_api_version(
        provider_api_version,
        strict=strict,
    )

    ensure_api_compatible(
        resolved_version,
        PROVIDER_API_VERSION,
        policy=policy,
        subject="provider",
        error_cls=ProviderAPIIncompatibleError,
    )


def is_python_compatible(python_version: tuple[int, int] | None = None) -> bool:
    """Return whether a Python ``(major, minor)`` version is supported by the SDK."""

    if python_version is None:
        python_version = (sys.version_info.major, sys.version_info.minor)
    return python_version >= MIN_SUPPORTED_PYTHON


def ensure_python_compatible(python_version: tuple[int, int] | None = None) -> None:
    """Raise when the provided or running Python version is not SDK-compatible."""

    if not is_python_compatible(python_version):
        current = python_version or (sys.version_info.major, sys.version_info.minor)
        raise PythonRuntimeIncompatibleError(
            f"Python {current[0]}.{current[1]} is not supported. "
            f"Minimum supported version is {MIN_SUPPORTED_PYTHON[0]}.{MIN_SUPPORTED_PYTHON[1]}."
        )


def _match_policy(
    candidate: tuple[int, int, int],
    host: tuple[int, int, int],
    policy: CompatibilityPolicy,
) -> bool:
    if policy == "exact":
        return candidate == host
    if policy == "same_major":
        return candidate[0] == host[0]

    raise ValueError(f"Unsupported compatibility policy '{policy}'.")


def _resolve_strict_mode(strict: bool | None) -> bool:
    if strict is None:
        return is_strict_compat_mode_enabled()
    return strict


__all__ = [
    "CompatibilityError",
    "CompatibilityPolicy",
    "DEFAULT_COMPATIBILITY_POLICY",
    "InvalidVersionError",
    "LOCAL_SDK_VERSION_FALLBACK",
    "MIN_SUPPORTED_PYTHON",
    "PLUGIN_API_VERSION",
    "PLUGIN_ENTRYPOINT_GROUP",
    "PluginAPIIncompatibleError",
    "PROVIDER_API_VERSION",
    "PROVIDER_ENTRYPOINT_GROUP",
    "ProviderAPIIncompatibleError",
    "PythonRuntimeIncompatibleError",
    "SDK_DISTRIBUTION",
    "SDK_VERSION",
    "STRICT_COMPAT_MODE_ENV",
    "ensure_api_compatible",
    "ensure_plugin_api_compatible",
    "ensure_provider_api_compatible",
    "ensure_python_compatible",
    "get_sdk_version",
    "is_api_compatible",
    "is_plugin_api_compatible",
    "is_provider_api_compatible",
    "is_python_compatible",
    "is_strict_compat_mode_enabled",
    "parse_api_version",
    "resolve_plugin_api_version",
    "resolve_provider_api_version",
]

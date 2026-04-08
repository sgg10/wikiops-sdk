import pytest

import wikiops_sdk.compat as compat


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1.2.3", (1, 2, 3)),
        ("0.0.0", (0, 0, 0)),
        (" 10.20.30 ", (10, 20, 30)),
    ],
)
def test_parse_api_version_valid(raw: str, expected: tuple[int, int, int]) -> None:
    assert compat.parse_api_version(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "1", "1.2", "v1.2.3", "1.2.3.4", "1.2.x", "01.2.3", "1.-2.3"],
)
def test_parse_api_version_invalid(raw: str) -> None:
    with pytest.raises(compat.InvalidVersionError):
        compat.parse_api_version(raw)


@pytest.mark.parametrize("raw", ["1", "true", "TRUE", "yes", "on", " On "])
def test_is_strict_compat_mode_enabled_truthy(raw: str) -> None:
    assert compat.is_strict_compat_mode_enabled(raw) is True


@pytest.mark.parametrize("raw", ["0", "false", "FALSE", "no", "off", "", " Off "])
def test_is_strict_compat_mode_enabled_falsy(raw: str) -> None:
    assert compat.is_strict_compat_mode_enabled(raw) is False


def test_is_strict_compat_mode_enabled_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(compat.STRICT_COMPAT_MODE_ENV, "true")
    assert compat.is_strict_compat_mode_enabled() is True


def test_is_strict_compat_mode_enabled_invalid_value() -> None:
    with pytest.raises(ValueError):
        compat.is_strict_compat_mode_enabled("maybe")


def test_resolve_plugin_api_version_non_strict_fallback() -> None:
    assert compat.resolve_plugin_api_version(None, strict=False) == compat.PLUGIN_API_VERSION
    assert compat.resolve_plugin_api_version("", strict=False) == compat.PLUGIN_API_VERSION


def test_resolve_provider_api_version_non_strict_fallback() -> None:
    assert (
        compat.resolve_provider_api_version(None, strict=False)
        == compat.PROVIDER_API_VERSION
    )


def test_resolve_plugin_api_version_strict_requires_value() -> None:
    with pytest.raises(compat.InvalidVersionError):
        compat.resolve_plugin_api_version(None, strict=True)


def test_resolve_provider_api_version_strict_requires_value() -> None:
    with pytest.raises(compat.InvalidVersionError):
        compat.resolve_provider_api_version("", strict=True)


@pytest.mark.parametrize("raw", ["1.0.0", "2.4.9"])
def test_resolve_versions_validate_format(raw: str) -> None:
    assert compat.resolve_plugin_api_version(raw, strict=True) == raw
    assert compat.resolve_provider_api_version(raw, strict=True) == raw


def test_resolve_versions_invalid_format_raises() -> None:
    with pytest.raises(compat.InvalidVersionError):
        compat.resolve_plugin_api_version("1", strict=False)
    with pytest.raises(compat.InvalidVersionError):
        compat.resolve_provider_api_version("1.0", strict=False)


@pytest.mark.parametrize(
    "candidate,host,policy,expected",
    [
        ("1.0.0", "1.0.0", "same_major", True),
        ("1.9.9", "1.0.0", "same_major", True),
        ("2.0.0", "1.0.0", "same_major", False),
        ("1.0.1", "1.0.0", "exact", False),
        ("1.0.0", "1.0.0", "exact", True),
    ],
)
def test_is_api_compatible(
    candidate: str,
    host: str,
    policy: compat.CompatibilityPolicy,
    expected: bool,
) -> None:
    assert compat.is_api_compatible(candidate, host, policy=policy) is expected


def test_is_api_compatible_rejects_invalid_policy() -> None:
    with pytest.raises(ValueError):
        compat.is_api_compatible("1.0.0", "1.0.0", policy="weird")  # type: ignore[arg-type]


def test_ensure_api_compatible_success() -> None:
    compat.ensure_api_compatible("1.2.0", "1.0.0", policy="same_major")


def test_ensure_api_compatible_invalid_candidate_reworded_message() -> None:
    with pytest.raises(compat.InvalidVersionError, match="Invalid plugin API version"):
        compat.ensure_api_compatible("bad", "1.0.0", subject="plugin")


def test_ensure_api_compatible_incompatible_raises_specific_error() -> None:
    with pytest.raises(compat.PluginAPIIncompatibleError):
        compat.ensure_api_compatible(
            "2.0.0",
            compat.PLUGIN_API_VERSION,
            subject="plugin",
            error_cls=compat.PluginAPIIncompatibleError,
        )


def test_plugin_compat_non_strict_none_is_compatible() -> None:
    assert compat.is_plugin_api_compatible(None, strict=False) is True


def test_plugin_compat_non_strict_invalid_version_is_false() -> None:
    assert compat.is_plugin_api_compatible("invalid", strict=False) is False


def test_plugin_compat_strict_none_is_false() -> None:
    assert compat.is_plugin_api_compatible(None, strict=True) is False


def test_provider_compat_non_strict_none_is_compatible() -> None:
    assert compat.is_provider_api_compatible(None, strict=False) is True


def test_provider_compat_strict_none_is_false() -> None:
    assert compat.is_provider_api_compatible(None, strict=True) is False


def test_ensure_plugin_api_compatible_non_strict_none_passes() -> None:
    compat.ensure_plugin_api_compatible(None, strict=False)


def test_ensure_plugin_api_compatible_strict_none_raises() -> None:
    with pytest.raises(compat.InvalidVersionError):
        compat.ensure_plugin_api_compatible(None, strict=True)


def test_ensure_plugin_api_compatible_major_mismatch_raises() -> None:
    with pytest.raises(compat.PluginAPIIncompatibleError):
        compat.ensure_plugin_api_compatible("2.0.0", strict=False)


def test_ensure_provider_api_compatible_major_mismatch_raises() -> None:
    with pytest.raises(compat.ProviderAPIIncompatibleError):
        compat.ensure_provider_api_compatible("2.0.0", strict=False)


def test_is_python_compatible_defaults_to_runtime() -> None:
    assert isinstance(compat.is_python_compatible(), bool)


@pytest.mark.parametrize(
    "version,expected",
    [((3, 10), True), ((3, 9), False), ((3, 11), True)],
)
def test_is_python_compatible_explicit(
    version: tuple[int, int], expected: bool
) -> None:
    assert compat.is_python_compatible(version) is expected


def test_ensure_python_compatible_raises_for_unsupported() -> None:
    with pytest.raises(compat.PythonRuntimeIncompatibleError):
        compat.ensure_python_compatible((3, 9))


def test_get_sdk_version_uses_distribution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(compat, "distribution_version", lambda _: "9.9.9")
    assert compat.get_sdk_version() == "9.9.9"


def test_get_sdk_version_fallback_when_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise_not_found(_: str) -> str:
        raise compat.PackageNotFoundError

    monkeypatch.setattr(compat, "distribution_version", _raise_not_found)
    assert compat.get_sdk_version() == compat.LOCAL_SDK_VERSION_FALLBACK


def test_all_exports_are_present() -> None:
    module_dict = vars(compat)
    for export in compat.__all__:
        assert export in module_dict


def test_resolvers_obey_env_when_strict_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(compat.STRICT_COMPAT_MODE_ENV, "true")
    with pytest.raises(compat.InvalidVersionError):
        compat.resolve_plugin_api_version(None)


def test_is_plugin_api_compatible_obeys_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(compat.STRICT_COMPAT_MODE_ENV, "true")
    assert compat.is_plugin_api_compatible(None) is False

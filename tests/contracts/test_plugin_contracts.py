from typing import Set

from wikiops_sdk.compat import PLUGIN_API_VERSION
from wikiops_sdk.contracts.plugin import (
    DocumentationPlugin,
    PluginConfigModel,
    PluginInputModel,
    PluginManifest,
)
from wikiops_sdk.contracts.resources import PluginResourceProvider
from wikiops_sdk.domain.context import ExecutionContext
from wikiops_sdk.domain.models import ChangeSet, ProviderCapability


def test_plugin_manifest_defaults_without_api_version() -> None:
    manifest = PluginManifest(
        plugin_id="demo",
        display_name="Demo",
        version="0.1.0",
        description="Demo plugin",
    )
    assert manifest.plugin_api_version is None
    assert manifest.resolved_plugin_api_version(strict=False) == PLUGIN_API_VERSION


def test_plugin_manifest_for_current_api_sets_explicit_version() -> None:
    manifest = PluginManifest.for_current_api(
        plugin_id="demo",
        display_name="Demo",
        version="0.1.0",
        description="Demo plugin",
        required_capabilities={ProviderCapability.READ_DOCUMENT},
    )
    assert manifest.plugin_api_version == PLUGIN_API_VERSION
    assert manifest.required_capabilities == {ProviderCapability.READ_DOCUMENT}


def test_plugin_manifest_for_current_api_default_capabilities_not_shared() -> None:
    a = PluginManifest.for_current_api(
        plugin_id="a",
        display_name="A",
        version="0.1.0",
        description="A",
    )
    b = PluginManifest.for_current_api(
        plugin_id="b",
        display_name="B",
        version="0.1.0",
        description="B",
    )

    a.required_capabilities.add(ProviderCapability.BUILD_LINK)
    assert ProviderCapability.BUILD_LINK not in b.required_capabilities


def test_plugin_manifest_resolved_version_strict_requires_explicit() -> None:
    manifest = PluginManifest(
        plugin_id="demo",
        display_name="Demo",
        version="0.1.0",
        description="Demo plugin",
    )
    import wikiops_sdk.compat as compat

    try:
        manifest.resolved_plugin_api_version(strict=True)
    except compat.InvalidVersionError:
        pass
    else:
        raise AssertionError("Expected InvalidVersionError in strict mode")


class _DummyResources:
    def has(self, relative_path: str) -> bool:
        return relative_path == "README.md"

    def read_text(self, relative_path: str, encoding: str = "utf-8") -> str:
        return f"{relative_path}:{encoding}"

    def list(self, prefix: str = "") -> list[str]:
        return [f"{prefix}file.md"]


class _DummyPlugin:
    manifest = PluginManifest.for_current_api(
        plugin_id="dummy",
        display_name="Dummy",
        version="0.1.0",
        description="Dummy plugin",
    )
    resources: PluginResourceProvider = _DummyResources()

    def get_config_model(self) -> type[PluginConfigModel]:
        return PluginConfigModel

    def get_input_model(self) -> type[PluginInputModel]:
        return PluginInputModel

    def required_ref_aliases(
        self,
        plugin_config: PluginConfigModel,
        input_data: PluginInputModel,
    ) -> Set[str]:
        return {"root"}

    def plan(self, ctx: ExecutionContext) -> ChangeSet:
        return ChangeSet(plugin_id="dummy")


def test_documentation_plugin_runtime_protocol_positive() -> None:
    plugin = _DummyPlugin()
    assert isinstance(plugin, DocumentationPlugin)


def test_documentation_plugin_runtime_protocol_negative() -> None:
    class IncompletePlugin:
        manifest = PluginManifest.for_current_api(
            plugin_id="incomplete",
            display_name="Incomplete",
            version="0.1.0",
            description="Incomplete plugin",
        )

    assert not isinstance(IncompletePlugin(), DocumentationPlugin)

from wikiops_sdk.contracts.resources import PluginResourceProvider


class _Resources:
    def has(self, relative_path: str) -> bool:
        return relative_path == "docs/index.md"

    def read_text(self, relative_path: str, encoding: str = "utf-8") -> str:
        return f"{relative_path}:{encoding}"

    def list(self, prefix: str = "") -> list[str]:
        return [f"{prefix}index.md"]


def test_plugin_resource_provider_runtime_protocol_positive() -> None:
    resources = _Resources()
    assert isinstance(resources, PluginResourceProvider)


def test_plugin_resource_provider_runtime_protocol_negative() -> None:
    class IncompleteResources:
        def has(self, relative_path: str) -> bool:
            return True

    assert not isinstance(IncompleteResources(), PluginResourceProvider)

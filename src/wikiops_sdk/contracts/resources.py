from typing import Iterable, Protocol, runtime_checkable


@runtime_checkable
class PluginResourceProvider(Protocol):
    """Read-only accessor for files distributed with a plugin."""

    def has(self, relative_path: str) -> bool:
        """Return whether ``relative_path`` exists in the plugin resources."""

        ...

    def read_text(self, relative_path: str, encoding: str = "utf-8") -> str:
        """Read and return text content from ``relative_path``."""

        ...

    def list(self, prefix: str = "") -> Iterable[str]:
        """Yield resource paths whose relative path starts with ``prefix``."""

        ...

from typing import Protocol, Set, Type, runtime_checkable

from pydantic import BaseModel, Field

from wikiops_sdk.contracts.resources import PluginResourceProvider
from wikiops_sdk.domain.context import ExecutionContext
from wikiops_sdk.domain.models import ChangeSet, ProviderCapability


class PluginManifest(BaseModel):
    """Static metadata used to register and validate a documentation plugin."""

    plugin_id: str = Field(..., description="Unique identifier for the plugin.")
    display_name: str = Field(..., description="Human-readable name for the plugin.")
    version: str = Field(..., description="Version of the plugin.")
    plugin_api_version: str = Field(
        default="1.0.0",
        description="Version of the plugin API that this plugin implements.",
    )
    description: str = Field(
        ..., description="Brief description of the plugin's functionality."
    )
    required_capabilities: Set[ProviderCapability] = Field(
        default_factory=set,
        description="Set of provider capabilities required by this plugin.",
    )


class PluginConfigModel(BaseModel):
    """Base class for plugin configuration payloads."""


class PluginInputModel(BaseModel):
    """Base class for plugin execution input payloads."""


@runtime_checkable
class DocumentationPlugin(Protocol):
    """Behavioral contract implemented by documentation plugins."""

    manifest: PluginManifest
    resources: PluginResourceProvider

    def get_config_model(self) -> Type[PluginConfigModel]:
        """Return the Pydantic model used to validate plugin configuration."""

        ...

    def get_input_model(self) -> Type[PluginInputModel]:
        """Return the Pydantic model used to validate runtime input."""

        ...

    def required_ref_aliases(
        self,
        plugin_config: PluginConfigModel,
        input_data: PluginInputModel,
    ) -> Set[str]:
        """Return aliases that must be resolved before planning starts."""

        ...

    def plan(self, ctx: ExecutionContext) -> ChangeSet:
        """Build and return the provider-agnostic change set for this run."""

        ...

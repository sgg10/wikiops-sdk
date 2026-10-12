# Write A Plugin

This guide explains how to implement a documentation plugin against the current SDK.

## Plugin Responsibilities

A plugin is responsible for planning documentation changes.

That means a plugin should:

- declare metadata
- declare the provider capabilities it requires
- declare the document aliases it expects to be resolved before planning
- inspect the execution context
- return a `ChangeSet`

A plugin should not:

- persist documents directly
- talk to provider-specific APIs directly through the SDK contracts
- orchestrate execution order

## The Main Contract

Plugins implement the `DocumentationPlugin` protocol from `wikiops_sdk.contracts`.

The protocol expects:

- `manifest`
- `resources`
- `get_config_model()`
- `get_input_model()`
- `required_ref_aliases(...)`
- `plan(ctx)`

## Minimal Plugin Example

```python
from pydantic import Field

from wikiops_sdk.contracts import (
    DocumentationPlugin,
    PluginConfigModel,
    PluginInputModel,
    PluginManifest,
    PluginResourceProvider,
)
from wikiops_sdk.domain import (
    ChangeSet,
    CreateChildDocumentOperation,
    ExecutionContext,
    ProviderCapability,
)


class TeamDocsConfig(PluginConfigModel):
    parent_alias: str = Field(..., description="Alias of the parent page.")


class TeamDocsInput(PluginInputModel):
    team_name: str = Field(..., description="Display name of the team.")


class TeamDocsPlugin:
    manifest = PluginManifest.for_current_api(
        plugin_id="wikiops.team-docs",
        display_name="Team Docs",
        version="0.1.0",
        description="Plans a child page for a team.",
        required_capabilities={ProviderCapability.CREATE_CHILD_DOCUMENT},
    )

    def __init__(self, resources: PluginResourceProvider) -> None:
        self.resources = resources

    def get_config_model(self) -> type[PluginConfigModel]:
        return TeamDocsConfig

    def get_input_model(self) -> type[PluginInputModel]:
        return TeamDocsInput

    def required_ref_aliases(
        self,
        plugin_config: PluginConfigModel,
        input_data: PluginInputModel,
    ) -> set[str]:
        config = TeamDocsConfig.model_validate(plugin_config.model_dump())
        return {config.parent_alias}

    def plan(self, ctx: ExecutionContext) -> ChangeSet:
        parent_alias = ctx.plugin_config["parent_alias"]
        team_name = ctx.input_data["team_name"]
        parent_ref = ctx.refs[parent_alias]

        return ChangeSet(
            plugin_id=self.manifest.plugin_id,
            operations=[
                CreateChildDocumentOperation(
                    parent_ref=parent_ref,
                    child_title=f"{team_name} Overview",
                    child_content=(
                        f"# {team_name} Overview\n\n"
                        "This page was planned by a WikiOps plugin."
                    ),
                )
            ],
        )
```

This class structurally conforms to `DocumentationPlugin` even though it does not inherit from it directly.

## Manifest Design

`PluginManifest` contains the plugin metadata the host can inspect.

Important fields:

- `plugin_id`
- `display_name`
- `version`
- `plugin_api_version`
- `description`
- `required_capabilities`

### Recommended Practice

Use `PluginManifest.for_current_api(...)` for released plugins. It makes the intended plugin API explicit and avoids depending on implicit non-strict resolution behavior.

If you omit `plugin_api_version`, the SDK can resolve it automatically in non-strict mode, which is useful for local development.

## Config Model And Input Model

The SDK separates:

- plugin configuration, which is usually stable for a profile or installation
- runtime input data, which varies per execution

Use:

- `PluginConfigModel` for configuration shape
- `PluginInputModel` for runtime input shape

The host is expected to validate these models before invoking the plugin.

## `required_ref_aliases(...)`

This method lets the plugin declare which logical aliases must be resolved before planning begins.

Typical use cases:

- a known root page
- a known handbook parent page
- a known team landing page

### Why This Matters

It allows the host to resolve all required references before `plan(ctx)` runs, rather than forcing the plugin to mix planning with provider-specific lookup concerns.

## `plan(ctx)`

`plan(ctx)` is the core method. It receives an `ExecutionContext` and returns a `ChangeSet`.

### Current Design Note

The current `ExecutionContext` stores `plugin_config` and `input_data` as dictionaries, not typed plugin-specific Pydantic models. That means the host may validate typed inputs first, but the plugin still consumes normalized dictionary data from the execution context.

Recommended practice:

- validate config and input in the host
- pass normalized dictionaries into the context
- keep the plugin logic predictable and dictionary-key based inside `plan`

### Structured Planning Metadata

Use `ChangeSet.metadata` for plugin-defined structured planning data that belongs to the plan as a whole. Metadata alone does not make a change set non-empty; `is_empty()` depends only on whether operations were planned.

## Using Plugin Resources

`PluginResourceProvider` gives the plugin read-only access to files shipped with the plugin package.

Typical uses:

- Markdown templates
- reusable snippets
- static fragments
- binary assets such as images or PDFs
- prompt files for future automation layers

Example:

```python
template = self.resources.read_text("templates/team-overview.md")
logo_bytes = self.resources.read_bytes("resources/assets/logo.png")
```

When a plugin wants the host/provider to persist an asset, the recommended pattern is:

1. declare the asset source in plugin config or input
2. emit a `PutAssetOperation`
3. reference it from content with `asset://<asset_key>`

Example Markdown:

```md
![System Diagram](asset://system_diagram)
```

## Emitting Warnings And Notes

Plugins can attach planning metadata to a `ChangeSet`.

Example:

```python
from wikiops_sdk.domain import ChangeSet, NoteMessage, WarningMessage

changeset = ChangeSet(
    plugin_id="wikiops.team-docs",
    warnings=[
        WarningMessage(
            code="MISSING_TEAM_OWNER",
            message="The team owner was not provided; page will omit owner details.",
        )
    ],
    notes=[
        NoteMessage(
            code="USING_DEFAULT_TEMPLATE",
            message="The default team overview template was used.",
        )
    ],
)
```

## Capability Requirements

Use `manifest.required_capabilities` to declare what the plugin needs from the provider.

Examples:

- `READ_DOCUMENT` if the plugin expects the host/provider to fetch existing content before planning
- `CREATE_CHILD_DOCUMENT` if the plugin emits child-page operations
- `BUILD_LINK` if the plugin or host workflow depends on user-facing links

The plugin should declare capabilities honestly and narrowly. The host should treat the declaration as part of execution planning and validation.

## Recommended Plugin Workflow

1. Define manifest metadata.
2. Define configuration and input models.
3. Declare required aliases.
4. Read resolved references from `ExecutionContext.refs`.
5. Build operations and compose a `ChangeSet`.
6. Emit warnings and notes where useful.

## Common Mistakes To Avoid

- hardcoding provider-specific behavior into the plugin
- treating the plugin as the persistence layer
- assuming all providers support all capabilities
- ignoring compatibility helpers during release workflows
- relying on implicit `plugin_api_version` resolution for production releases

## Related Documentation

- [`../concepts.md`](../concepts.md)
- [`../compatibility.md`](../compatibility.md)
- [`../api/contracts.md`](../api/contracts.md)
- [`../api/domain.md`](../api/domain.md)

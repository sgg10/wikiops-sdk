#!/usr/bin/env python3
"""Run a basic smoke test against an installed wikiops-sdk distribution."""

from __future__ import annotations

import argparse
from importlib.metadata import version as distribution_version

from wikiops_sdk import (
    PLUGIN_API_VERSION,
    ensure_plugin_api_compatible,
    ensure_python_compatible,
    is_provider_api_compatible,
    resolve_plugin_api_version,
)
from wikiops_sdk.compat import PLUGIN_ENTRYPOINT_GROUP, PROVIDER_ENTRYPOINT_GROUP
from wikiops_sdk.contracts import PluginManifest, ProviderSettings
from wikiops_sdk.domain import (
    ChangeSet,
    CreateDocumentOperation,
    DocumentRef,
    ProviderCapability,
    RefKind,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exercise the public SDK surface after installation."
    )
    parser.add_argument(
        "--expected-distribution-version",
        required=False,
        help="Expected installed version of the wikiops-sdk distribution.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.expected_distribution_version is not None:
        installed_version = distribution_version("wikiops-sdk")
        if installed_version != args.expected_distribution_version:
            raise RuntimeError(
                f"Installed wikiops-sdk version '{installed_version}' does not "
                f"match expected version '{args.expected_distribution_version}'."
            )

    ensure_python_compatible()
    ensure_plugin_api_compatible(None, strict=False)
    assert resolve_plugin_api_version(None, strict=False) == PLUGIN_API_VERSION
    assert is_provider_api_compatible(None, strict=False) is True
    assert PLUGIN_ENTRYPOINT_GROUP == "wikiops.plugins"
    assert PROVIDER_ENTRYPOINT_GROUP == "wikiops.providers"

    ref = DocumentRef(provider="demo", kind=RefKind.ID, locator={"id": "root"})
    settings = ProviderSettings(provider_name="demo")
    manifest = PluginManifest.for_current_api(
        plugin_id="wikiops.demo",
        display_name="Demo Plugin",
        version="0.1.0",
        description="Smoke test plugin manifest.",
        required_capabilities={ProviderCapability.CREATE_DOCUMENT},
    )
    changeset = ChangeSet(
        plugin_id=manifest.plugin_id,
        operations=[
            CreateDocumentOperation(
                parent_ref=ref,
                title="Smoke Test",
                content="# Smoke Test\n\nThe SDK import and model surface works.",
            )
        ],
    )

    assert settings.provider_name == "demo"
    assert manifest.plugin_api_version == PLUGIN_API_VERSION
    assert changeset.is_empty() is False
    assert changeset.operations[0].parent_ref == ref

    print("wikiops-sdk smoke test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

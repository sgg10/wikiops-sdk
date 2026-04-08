#!/usr/bin/env python3
"""Validate that a release tag matches the project version."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"\s*$')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ensure a release tag matches the version in pyproject.toml."
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Git tag to validate, for example 'v1.2.3'.",
    )
    parser.add_argument(
        "--pyproject",
        default="pyproject.toml",
        help="Path to pyproject.toml.",
    )
    return parser.parse_args()


def read_project_version(pyproject_path: Path) -> str:
    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        match = VERSION_PATTERN.match(line.strip())
        if match:
            return match.group(1)

    raise RuntimeError(f"Could not find a project version in {pyproject_path}.")


def normalize_tag(tag: str) -> str:
    return tag[1:] if tag.startswith("v") else tag


def main() -> int:
    args = parse_args()
    pyproject_path = Path(args.pyproject)
    if not pyproject_path.exists():
        raise FileNotFoundError(f"Missing pyproject.toml at {pyproject_path}.")

    project_version = read_project_version(pyproject_path)
    tag_version = normalize_tag(args.tag)

    if tag_version != project_version:
        print(
            f"Tag version '{tag_version}' does not match project version "
            f"'{project_version}'.",
            file=sys.stderr,
        )
        return 1

    print(f"Release tag '{args.tag}' matches project version '{project_version}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

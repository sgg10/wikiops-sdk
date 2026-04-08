#!/usr/bin/env python3
"""Wait until a package version becomes available on PyPI or TestPyPI."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


REPOSITORY_JSON_URLS = {
    "pypi": "https://pypi.org/pypi/{package}/json",
    "testpypi": "https://test.pypi.org/pypi/{package}/json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Poll package metadata until a specific version is available."
    )
    parser.add_argument(
        "--repository",
        choices=sorted(REPOSITORY_JSON_URLS),
        required=True,
        help="Package index to query.",
    )
    parser.add_argument(
        "--package",
        required=True,
        help="Distribution name, for example 'wikiops-sdk'.",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Version that must become visible on the selected repository.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Total seconds to wait before failing.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Seconds between polling attempts.",
    )
    return parser.parse_args()


def fetch_release_payload(repository: str, package: str) -> dict | None:
    url = REPOSITORY_JSON_URLS[repository].format(package=package)
    request = urllib.request.Request(url, headers={"Accept": "application/json"})

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def version_is_available(payload: dict | None, version: str) -> bool:
    if payload is None:
        return False

    files = payload.get("releases", {}).get(version, [])
    return bool(files)


def main() -> int:
    args = parse_args()
    deadline = time.monotonic() + args.timeout

    while time.monotonic() < deadline:
        payload = fetch_release_payload(args.repository, args.package)
        if version_is_available(payload, args.version):
            print(
                f"Found {args.package}=={args.version} on {args.repository}."
            )
            return 0

        print(
            f"Waiting for {args.package}=={args.version} to appear on "
            f"{args.repository}..."
        )
        time.sleep(args.interval)

    raise TimeoutError(
        f"Timed out waiting for {args.package}=={args.version} to appear on "
        f"{args.repository}."
    )


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path
import sys

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(autouse=True)
def clear_strict_compat_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WIKIOPS_SDK_STRICT_COMPAT", raising=False)

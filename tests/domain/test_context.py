from wikiops_sdk.domain.context import ExecutionContext
from wikiops_sdk.domain.models import Document, DocumentRef, RefKind


def _make_ref(alias: str = "root") -> DocumentRef:
    return DocumentRef(
        provider="demo",
        kind=RefKind.ALIAS,
        locator={"alias": alias},
        alias=alias,
    )


def test_execution_context_defaults() -> None:
    ctx = ExecutionContext(
        run_id="run-1",
        profile_name="default",
        provider_name="demo",
    )
    assert ctx.dry_run is True
    assert ctx.refs == {}
    assert ctx.documents == {}
    assert ctx.plugin_config == {}
    assert ctx.input_data == {}
    assert ctx.runtime_vars == {}


def test_execution_context_mutable_defaults_are_not_shared() -> None:
    a = ExecutionContext(run_id="a", profile_name="p", provider_name="demo")
    b = ExecutionContext(run_id="b", profile_name="p", provider_name="demo")

    a.refs["op-1"] = _make_ref("a")
    a.runtime_vars["x"] = 1

    assert "op-1" not in b.refs
    assert "x" not in b.runtime_vars


def test_execution_context_accepts_documents_map() -> None:
    ref = _make_ref("home")
    doc = Document(ref=ref, title="Home", content="# Home")
    ctx = ExecutionContext(
        run_id="run-2",
        profile_name="default",
        provider_name="demo",
        refs={"op": ref},
        documents={"home": doc},
    )
    assert ctx.refs["op"].alias == "home"
    assert ctx.documents["home"].title == "Home"

from wikiops_sdk.domain.models import AssetRef, AssetRefKind, DocumentRef, RefKind
from wikiops_sdk.domain.results import ApplyResult, AppliedOperationResult, OperationStatus


def _make_ref() -> DocumentRef:
    return DocumentRef(provider="demo", kind=RefKind.ID, locator={"id": "123"})


def test_applied_operation_result_defaults() -> None:
    result = AppliedOperationResult(operation_id="op-1", status=OperationStatus.APPLIED)
    assert result.message is None
    assert result.resolved_ref is None
    assert result.resolved_asset_ref is None
    assert result.resolved_asset_reference is None
    assert result.resulting_version is None


def test_applied_operation_result_accepts_asset_fields() -> None:
    result = AppliedOperationResult(
        operation_id="op-1",
        status=OperationStatus.APPLIED,
        resolved_asset_ref=AssetRef(
            provider="demo",
            kind=AssetRefKind.PATH,
            locator={"path": "/.assets/logo.png"},
        ),
        resolved_asset_reference="/.assets/logo.png",
    )

    assert result.resolved_asset_ref.locator["path"] == "/.assets/logo.png"
    assert result.resolved_asset_reference == "/.assets/logo.png"


def test_apply_result_defaults_and_has_failures_false() -> None:
    result = ApplyResult(provider_name="demo")
    assert result.results == []
    assert result.has_failures() is False


def test_apply_result_has_failures_true_when_any_failed() -> None:
    ok = AppliedOperationResult(operation_id="1", status=OperationStatus.APPLIED)
    bad = AppliedOperationResult(
        operation_id="2",
        status=OperationStatus.FAILED,
        resolved_ref=_make_ref(),
    )
    result = ApplyResult(provider_name="demo", results=[ok, bad])
    assert result.has_failures() is True

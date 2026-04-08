import pytest
from pydantic import TypeAdapter, ValidationError

from wikiops_sdk.domain.models import (
    ChangeSet,
    CreateChildDocumentOperation,
    CreateDocumentOperation,
    Document,
    DocumentFormat,
    DocumentRef,
    DocumentVersion,
    NoteMessage,
    Operation,
    ProviderCapability,
    RefKind,
    UpdateDocumentOperation,
    WarningMessage,
)


def _make_ref(kind: RefKind = RefKind.ID) -> DocumentRef:
    return DocumentRef(provider="demo", kind=kind, locator={"id": "123"})


def test_document_ref_allows_extra_fields() -> None:
    ref = DocumentRef(
        provider="demo",
        kind=RefKind.ID,
        locator={"id": "abc"},
        external_id="ext-1",
    )
    dumped = ref.model_dump()
    assert dumped["external_id"] == "ext-1"


def test_document_defaults() -> None:
    doc = Document(ref=_make_ref(), title="Title")
    assert doc.content == ""
    assert doc.format is DocumentFormat.MARKDOWN
    assert doc.metadata == {}
    assert doc.version is None


def test_document_mutable_defaults_not_shared() -> None:
    a = Document(ref=_make_ref(), title="A")
    b = Document(ref=_make_ref(), title="B")
    a.metadata["x"] = 1
    assert "x" not in b.metadata


def test_document_version_fields_optional() -> None:
    version = DocumentVersion()
    assert version.token is None
    assert version.revision is None
    assert version.etag is None


def test_create_document_operation_defaults() -> None:
    op = CreateDocumentOperation(title="Doc", content="Body")
    assert op.operation == "create_document"
    assert op.format is DocumentFormat.MARKDOWN
    assert op.metadata == {}
    assert op.operation_id


def test_update_document_operation_defaults() -> None:
    op = UpdateDocumentOperation(ref=_make_ref(), new_content="Updated")
    assert op.operation == "update_document"
    assert op.format is DocumentFormat.MARKDOWN
    assert op.metadata == {}


def test_create_child_document_operation_defaults() -> None:
    op = CreateChildDocumentOperation(
        parent_ref=_make_ref(),
        child_title="Child",
        child_content="Body",
    )
    assert op.operation == "create_child_document"
    assert op.child_format is DocumentFormat.MARKDOWN
    assert op.child_metadata == {}


def test_operation_discriminator_create_document() -> None:
    adapter = TypeAdapter(Operation)
    parsed = adapter.validate_python(
        {
            "operation": "create_document",
            "title": "Doc",
            "content": "Body",
        }
    )
    assert isinstance(parsed, CreateDocumentOperation)


def test_operation_discriminator_update_document() -> None:
    adapter = TypeAdapter(Operation)
    parsed = adapter.validate_python(
        {
            "operation": "update_document",
            "ref": _make_ref().model_dump(),
            "new_content": "Body",
        }
    )
    assert isinstance(parsed, UpdateDocumentOperation)


def test_operation_discriminator_create_child_document() -> None:
    adapter = TypeAdapter(Operation)
    parsed = adapter.validate_python(
        {
            "operation": "create_child_document",
            "parent_ref": _make_ref().model_dump(),
            "child_title": "Child",
            "child_content": "Body",
        }
    )
    assert isinstance(parsed, CreateChildDocumentOperation)


def test_operation_discriminator_invalid_operation_raises() -> None:
    adapter = TypeAdapter(Operation)
    with pytest.raises(ValidationError):
        adapter.validate_python(
            {
                "operation": "delete_document",
                "title": "Doc",
            }
        )


def test_changeset_defaults_and_is_empty() -> None:
    changeset = ChangeSet(plugin_id="demo")
    assert changeset.operations == []
    assert changeset.warnings == []
    assert changeset.notes == []
    assert changeset.is_empty() is True


def test_changeset_is_not_empty_when_operation_exists() -> None:
    op = CreateDocumentOperation(title="Doc", content="Body")
    changeset = ChangeSet(plugin_id="demo", operations=[op])
    assert changeset.is_empty() is False


def test_changeset_mutable_defaults_not_shared() -> None:
    a = ChangeSet(plugin_id="a")
    b = ChangeSet(plugin_id="b")
    a.warnings.append(WarningMessage(code="W1", message="warn"))
    a.notes.append(NoteMessage(code="N1", message="note"))
    assert b.warnings == []
    assert b.notes == []


def test_provider_capability_enum_values() -> None:
    assert ProviderCapability.READ_DOCUMENT.value == "read_document"
    assert ProviderCapability.VERSION_CHECK.value == "version_check"

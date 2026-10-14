import asyncio
from pathlib import Path
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import DocumentStatus
from app.documents import exceptions as document_exceptions, processing, service


@pytest.mark.asyncio
async def test_upload_document(authorized_client):
    content = b"document_1"
    response = await authorized_client.post(
        "/documents",
        files={"file": ("document_1.txt", content, "text/plain")},
        params={'auto_extract': False}
    )
    data = response.json()
    assert response.status_code == 201
    assert type(data["id"]) is int
    assert data["original_filename"] == "document_1.txt"
    assert data["size"] == len(content)
    assert data["content_type"] == "text/plain"
    assert data["status"] == DocumentStatus.uploaded


@pytest.mark.asyncio
async def test_upload_toolarge_file(authorized_client):
    response = await authorized_client.post(
        "/documents",
        files={"file": ("document_1.txt", b"x" * (5 * 1024 * 1024 + 1), "text/plain")},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "File too large"


@pytest.mark.asyncio
async def test_upload_document_with_db_error(authorized_client, monkeypatch):
    async def broken_commit():
        raise Exception("DB failure")
    monkeypatch.setattr(AsyncSession, "commit", broken_commit)
    response = await authorized_client.post(
        "/documents",
        files={"file": ("document_1.txt", b"document_1", "text/plain")},
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    "content_type, expected_status",
    [
        ("text/plain", 200),
        ("text/html", 200),
        ("application/pdf", 200),
        ("application/json", 415),
        ("image/jpeg", 415),
        ("audio/mpeg", 415),
        ("multipart/form-data", 415),
    ],
)
@pytest.mark.asyncio
async def test_process_document_supported_and_unsupported_types(
    authorized_client, content_type, expected_status
):
    file_bytes = b"document_1"
    if content_type == "application/pdf":
        file_bytes = (Path(__file__).parent / "fixtures" / "sample.pdf").read_bytes()

    created_document = (
        await authorized_client.post(
            "/documents",
            files={"file": ("document_1", file_bytes, content_type)},
            params={'auto_extract': False},
        )
    ).json()

    process_response = await authorized_client.post(
        f"/documents/{created_document['id']}/process"
    )
    assert process_response.status_code == expected_status
    if process_response.status_code != 200:
        assert process_response.json()["detail"] == "Unsupported document type"


@pytest.mark.asyncio
async def test_process_document_conflict(authorized_client, created_document, monkeypatch):
    doc_id = created_document["id"]
    started = asyncio.Event()
    finish = asyncio.Event()

    async def slow_extract(*args, **kwargs):
        started.set()
        await finish.wait()
        return "extracted test text"

    monkeypatch.setattr(processing, "extract_document_text", slow_extract)

    task1 = asyncio.create_task(authorized_client.post(f"/documents/{doc_id}/process"))
    await started.wait()
    response2 = await authorized_client.post(f"/documents/{doc_id}/process")
    finish.set()
    response1 = await task1

    assert response1.status_code == 200
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Document is already being processed"


@pytest.mark.asyncio
async def test_process_document_with_timeout_error(authorized_client, created_document, monkeypatch):
    doc_id = created_document["id"]

    async def timeout_error(*args, **kwargs):
        raise document_exceptions.DocumentProcessingTimeoutError

    monkeypatch.setattr(processing, "extract_document_text", timeout_error)
    response = await authorized_client.post(f"/documents/{doc_id}/process")
    assert response.status_code == 504
    assert response.json()["detail"] == "Document processing timeout"


@pytest.mark.parametrize(
    "exception_to_raise, expected_status, expected_detail",
    [
        (document_exceptions.DocumentDecodeError(), 422, "Document content could not be decoded"),
        (document_exceptions.FailedChangeStatusError(), 500, "Failed to process document"),
        (document_exceptions.DocumentReadError(), 500, "Failed to read document"),
        (document_exceptions.DocumentDoesNotExistError(), 404, "Document does not exist"),
    ],
)
@pytest.mark.asyncio
async def test_process_document_exceptions(
    authorized_client, created_document, monkeypatch, exception_to_raise, expected_status, expected_detail
):
    doc_id = created_document["id"]

    async def mock_process(*args, **kwargs):
        raise exception_to_raise
    monkeypatch.setattr(service, "process_document", mock_process)
    response = await authorized_client.post(f"/documents/{doc_id}/process")
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail


@pytest.mark.asyncio
async def test_get_pdf_document_text(authorized_client):
    pdf_path = Path(__file__).parent / "fixtures" / "sample.pdf"
    upload_response = await authorized_client.post(
        "/documents",
        files={"file": ("sample.pdf", pdf_path.read_bytes(), "application/pdf")},
    )
    doc_id = upload_response.json()["id"]

    process_response = await authorized_client.post(f"/documents/{doc_id}/process")
    assert process_response.status_code == 200

    response = await authorized_client.get(f"/documents/{doc_id}/text")
    assert response.status_code == 200
    assert "Привет, мир!" in response.text


@pytest.mark.asyncio
async def test_get_document_text_not_ready(authorized_client, created_document):
    response = await authorized_client.get(f"/documents/{created_document['id']}/text")
    assert response.status_code == 409
    assert response.json()["detail"] == "Document text is not ready"


@pytest.mark.asyncio
async def test_get_document_text_nonexistent(authorized_client):
    response = await authorized_client.get("/documents/999/text")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_get_document(authorized_client, created_document):
    response = await authorized_client.get(f"/documents/{created_document['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == created_document["id"]
    assert data["original_filename"] == created_document["original_filename"]


@pytest.mark.asyncio
async def test_get_nonexistent_document(authorized_client):
    response = await authorized_client.get("/documents/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_get_document_unauthorized_user(client):
    response = await client.get("/documents/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_documents(authorized_client, created_document):
    response = await authorized_client.get("/documents")
    assert response.status_code == 200
    assert type(response.json()) is list
    assert any(doc["id"] == created_document["id"] for doc in response.json())


@pytest.mark.asyncio
async def test_download_document(authorized_client, created_document):
    response = await authorized_client.get(f"/documents/{created_document['id']}/file")
    assert response.status_code == 200
    assert response.content == b"document_1"


@pytest.mark.asyncio
async def test_download_document_file_not_found(authorized_client, created_document, monkeypatch):
    async def mock_get_file(*args, **kwargs):
        raise document_exceptions.StoredFileNotFoundError

    monkeypatch.setattr(service, "get_file", mock_get_file)
    response = await authorized_client.get(f"/documents/{created_document['id']}/file")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"


@pytest.mark.asyncio
async def test_download_nonexistent_document(authorized_client):
    response = await authorized_client.get("/documents/999/file")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_delete_document(authorized_client, created_document):
    doc_id = created_document["id"]
    response = await authorized_client.delete(f"/documents/{doc_id}")
    assert response.status_code == 204

    get_response = await authorized_client.get(f"/documents/{doc_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_document(authorized_client):
    response = await authorized_client.delete("/documents/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_delete_document_db_error(authorized_client, created_document, monkeypatch):
    async def mock_delete(*args, **kwargs):
        raise document_exceptions.FailedToDeleteDocumentError

    monkeypatch.setattr(service, "delete_document", mock_delete)
    response = await authorized_client.delete(f"/documents/{created_document['id']}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to delete document"
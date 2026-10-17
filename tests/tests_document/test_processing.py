import asyncio
from pathlib import Path

import pytest

from app.documents import exceptions as document_exceptions, processing, service


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
        file_bytes = (
            Path(__file__).parent.parent / "fixtures" / "sample.pdf"
        ).read_bytes()

    created_document = (
        await authorized_client.post(
            "/documents",
            files={"file": ("document_1", file_bytes, content_type)},
            params={"auto_extract": False},
        )
    ).json()

    process_response = await authorized_client.post(
        f"/documents/{created_document['id']}/process"
    )

    assert process_response.status_code == expected_status
    if process_response.status_code != 200:
        assert process_response.json()["detail"] == "Unsupported document type"


@pytest.mark.asyncio
async def test_process_document_conflict(
    authorized_client, created_document, monkeypatch
):
    doc_id = created_document["id"]
    started = asyncio.Event()
    finish = asyncio.Event()

    async def slow_extract(*args, **kwargs):
        started.set()
        await finish.wait()
        return "extracted test text"

    monkeypatch.setattr(processing, "extract_document_text", slow_extract)

    task1 = asyncio.create_task(
        authorized_client.post(f"/documents/{doc_id}/process")
    )
    await started.wait()
    response2 = await authorized_client.post(f"/documents/{doc_id}/process")
    finish.set()
    response1 = await task1

    assert response1.status_code == 200
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Document is already being processed"


@pytest.mark.asyncio
async def test_process_document_with_timeout_error(
    authorized_client, created_document, monkeypatch
):
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
        (
            document_exceptions.DocumentDecodeError(),
            422,
            "Document content could not be decoded",
        ),
        (
            document_exceptions.FailedChangeStatusError(),
            500,
            "Failed to process document",
        ),
        (
            document_exceptions.DocumentReadError(),
            500,
            "Failed to read document",
        ),
        (
            document_exceptions.DocumentDoesNotExistError(),
            404,
            "Document does not exist",
        ),
    ],
)
@pytest.mark.asyncio
async def test_process_document_exceptions(
    authorized_client,
    created_document,
    monkeypatch,
    exception_to_raise,
    expected_status,
    expected_detail,
):
    doc_id = created_document["id"]

    async def mock_process(*args, **kwargs):
        raise exception_to_raise

    monkeypatch.setattr(service, "process_document", mock_process)
    response = await authorized_client.post(f"/documents/{doc_id}/process")

    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail

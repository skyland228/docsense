import pytest

from app.documents import exceptions as document_exceptions, service


@pytest.mark.asyncio
async def test_download_document(authorized_client, created_document):
    response = await authorized_client.get(
        f"/documents/{created_document['id']}/file"
    )

    assert response.status_code == 200
    assert response.content == b"document_1"


@pytest.mark.asyncio
async def test_download_document_file_not_found(
    authorized_client, created_document, monkeypatch
):
    async def mock_get_file(*args, **kwargs):
        raise document_exceptions.StoredFileNotFoundError

    monkeypatch.setattr(service, "get_file", mock_get_file)
    response = await authorized_client.get(
        f"/documents/{created_document['id']}/file"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"


@pytest.mark.asyncio
async def test_download_nonexistent_document(authorized_client):
    response = await authorized_client.get("/documents/999/file")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"

import pytest

from app.documents import exceptions as document_exceptions
from app.documents import service


@pytest.mark.asyncio
async def test_delete_document(authorized_client, created_document):
    doc_id = created_document["id"]
    response = await authorized_client.delete(f"/documents/{doc_id}")

    assert response.status_code == 204

    get_response = await authorized_client.get(f"/documents/{doc_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_with_extracted_text(
    authorized_client,
    created_document_with_text,
):
    doc_id = created_document_with_text["id"]

    response = await authorized_client.delete(f"/documents/{doc_id}")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_document_unauthorized_user(client, created_document):
    client.headers.pop("Authorization", None)
    response = await client.delete(f"/documents/{created_document['id']}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_nonexistent_document(authorized_client):
    response = await authorized_client.delete("/documents/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_delete_document_db_error(
    authorized_client, created_document, monkeypatch
):
    async def mock_delete(*args, **kwargs):
        raise document_exceptions.FailedToDeleteDocumentError

    monkeypatch.setattr(service, "delete_document", mock_delete)
    response = await authorized_client.delete(f"/documents/{created_document['id']}")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to delete document"

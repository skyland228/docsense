import pytest


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
async def test_get_document_unauthorized_user(client, created_document):
    client.headers.pop("Authorization", None)
    response = await client.get(f"/documents/{created_document['id']}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_documents(authorized_client, created_document):
    response = await authorized_client.get("/documents")

    assert response.status_code == 200
    assert type(response.json()) is list
    assert any(doc["id"] == created_document["id"] for doc in response.json())


@pytest.mark.asyncio
async def test_get_documents_unauthorized_user(client, created_document):
    client.headers.pop("Authorization", None)
    response = await client.get("/documents")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

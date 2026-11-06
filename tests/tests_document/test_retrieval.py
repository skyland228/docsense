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
async def test_get_documents_with_sort_desc_created_document(
    authorized_client, created_document
):
    response_document_2 = await authorized_client.post(
        "/documents",
        files={"file": ("document_1.txt", "content", "text/plain")},
    )
    assert response_document_2.status_code == 201
    response = await authorized_client.get("/documents")
    assert response.status_code == 200
    assert type(response.json()) is list
    assert any(doc["id"] == created_document["id"] for doc in response.json())
    assert response.json()[0]["id"] == response_document_2.json()["id"]
    assert response.json()[1]["id"] == created_document["id"]


@pytest.mark.asyncio
async def test_get_documents_with_limit(authorized_client, created_document):
    response_document_2 = await authorized_client.post(
        "/documents",
        files={"file": ("document_1.txt", "content", "text/plain")},
    )
    assert response_document_2.status_code == 201
    response = await authorized_client.get("/documents?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_documents_with_offset(authorized_client, created_document):
    response_document_2 = await authorized_client.post(
        "/documents",
        files={"file": ("document_1.txt", "content", "text/plain")},
    )
    assert response_document_2.status_code == 201
    response_get = await authorized_client.get("/documents")
    assert response_get.status_code == 200
    assert len(response_get.json()) == 2
    response = await authorized_client.get("/documents?offset=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == response_get.json()[1]["id"]


@pytest.mark.asyncio
async def test_get_documents_with_search_field(authorized_client):
    response_document_1 = await authorized_client.post(
        "/documents",
        files={"file": ("some.txt", "content", "text/plain")},
    )
    assert response_document_1.status_code == 201
    response_document_2 = await authorized_client.post(
        "/documents",
        files={"file": ("search", "content", "text/plain")},
    )
    assert response_document_2.status_code == 201
    response = await authorized_client.get("/documents?search=search")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["original_filename"] == "search"


@pytest.mark.asyncio
async def test_get_documents_with_invalid_offset(authorized_client):
    response = await authorized_client.get("/documents?offset=-1")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "offset"]


@pytest.mark.asyncio
async def test_get_documents_with_invalid_limit_lt(authorized_client):
    response = await authorized_client.get("/documents?limit=101")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "limit"]


@pytest.mark.asyncio
async def test_get_documents_unauthorized_user(client, created_document):
    client.headers.pop("Authorization", None)
    response = await client.get("/documents")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

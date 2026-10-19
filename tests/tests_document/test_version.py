"""Tests for creating and validating document versions."""

from unittest.mock import Mock

import pytest
from sqlalchemy import select

from app.db.models.document import DocumentVersion
from app.documents import processing, storage


# Identical content is accepted as a new version without a message.
@pytest.mark.asyncio
async def test_create_version_with_identical_content(
    authorized_client, created_document_with_text
):
    current_text = (
        await authorized_client.get(
            f"/documents/{created_document_with_text['id']}/text"
        )
    ).content

    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/versions",
        files={
            "file": (
                created_document_with_text["original_filename"],
                current_text,
                "text/plain",
            )
        },
    )
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["extracted_text"] == "document_1"
    assert response_data["similarity"] == 1
    assert response_data["msg"] is None


# A related version is accepted, but a low similarity score produces a message.
@pytest.mark.asyncio
async def test_create_version_with_similarity_message(
    authorized_client, created_document_with_text
):
    current_text = (
        await authorized_client.get(
            f"/documents/{created_document_with_text['id']}/text"
        )
    ).content

    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/versions",
        files={
            "file": (
                created_document_with_text["original_filename"],
                current_text + b" new",
                "text/plain",
            )
        },
    )
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["extracted_text"] == "document_1 new"
    assert response_data["similarity"] == pytest.approx(2 / 3)
    assert response_data["msg"] == (
        "New version differs significantly from the previous version"
    )

    version_response = await authorized_client.get(
        f"/documents/{created_document_with_text['id']}"
        f"/versions/{response_data['version_number']}"
    )
    saved_version = version_response.json()

    assert version_response.status_code == 200
    assert saved_version["version_number"] == 2
    assert saved_version["similarity"] == pytest.approx(2 / 3)
    assert saved_version["msg"] == response_data["msg"]


@pytest.mark.asyncio
async def test_create_version_with_toolarge_file(
    authorized_client, created_document_with_text
):
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/versions",
        files={
            "file": (
                "document_1.txt",
                b"x" * (5 * 1024 * 1024 + 1),
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "File too large"


# Unrelated content is rejected and must not create a database record.
@pytest.mark.asyncio
async def test_reject_version_with_completely_different_content(
    authorized_client,
    created_document_with_text,
    db_session,
):
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/versions",
        files={
            "file": (
                created_document_with_text["original_filename"],
                b"completely different content",
                "text/plain",
            )
        },
    )
    response_data = response.json()

    version_query = select(DocumentVersion).where(
        DocumentVersion.document_id == created_document_with_text["id"]
    )
    result = await db_session.execute(version_query)
    versions = result.scalars().all()

    assert response.status_code == 422
    assert response_data["detail"] == (
        "The uploaded document is too different from the previous version"
    )
    assert len(versions) == 1


@pytest.mark.asyncio
async def test_create_version_unauthorized_user(client, created_document):
    client.headers.pop("Authorization", None)
    response = await client.post(
        f"/documents/{created_document['id']}/versions",
        files={
            "file": (
                "title",
                "content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_version_for_another_users_document(
    authorized_client,
    created_document,
    another_user_token,
):
    response = await authorized_client.post(
        f"/documents/{created_document['id']}/versions",
        headers={"Authorization": f"Bearer {another_user_token}"},
        files={
            "file": (
                "title",
                "content",
                "text/plain",
            )
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_create_version_cleanup_on_extraction_failure(
    authorized_client,
    created_document_with_text,
    monkeypatch,
):
    async def fake_extract(*args, **kwargs):
        raise RuntimeError("Extraction failed")

    monkeypatch.setattr(processing, "extract_document_text", fake_extract)
    delete_mock = Mock(wraps=storage.delete_file)
    monkeypatch.setattr(storage, "delete_file", delete_mock)
    with pytest.raises(RuntimeError, match="Extraction failed"):
        response = await authorized_client.post(
            f"/documents/{created_document_with_text['id']}/versions",
            files={"file": ("title", "document_1", "text/plain")},
        )
    delete_mock.assert_called_once()
    response = await authorized_client.get(
        f"/documents/{created_document_with_text['id']}/versions/2"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Version does not exist"


@pytest.mark.asyncio
async def test_get_versions(authorized_client, created_document_with_text):
    create_version_response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/versions",
        files={
            "file": (
                "document_1.txt",
                "document_1",
                "text/plain",
            )
        },
    )
    assert create_version_response.status_code == 201
    response = await authorized_client.get(
        f"/documents/{created_document_with_text['id']}/versions",
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
    assert {item["version_number"] for item in data} == {1, 2}


@pytest.mark.asyncio
async def test_get_version(authorized_client, created_document_with_text):
    response = await authorized_client.get(
        f"/documents/{created_document_with_text['id']}/versions/1"
    )
    data = response.json()
    assert response.status_code == 200
    assert data["version_number"] == 1
    assert data["extracted_text"] == "document_1"
    assert data["similarity"] is None
    assert data["msg"] is None


@pytest.mark.asyncio
async def test_get_versions_unauthorized_user(client, created_document_with_text):
    client.headers.pop("Authorization", None)
    response = await client.get(
        f"/documents/{created_document_with_text['id']}/versions"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_version_unauthorized_user(client, created_document_with_text):
    client.headers.pop("Authorization", None)
    response = await client.get(
        f"/documents/{created_document_with_text['id']}/versions/1"
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_version_nonexistent_document(authorized_client):
    response = await authorized_client.get("/documents/999/versions/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_get_nonexistent_version(authorized_client, created_document):
    response = await authorized_client.get(
        f"/documents/{created_document['id']}/versions/1"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Version does not exist"

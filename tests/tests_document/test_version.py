"""Tests for creating and validating document versions."""

import pytest
from sqlalchemy import select

from app.db.models.document import DocumentVersion


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
        f"/documents/{created_document_with_text['id']}/version",
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
        f"/documents/{created_document_with_text['id']}/version",
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
        "New version differs significantly "
        "from the previous version"
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


# Unrelated content is rejected and must not create a database record.
@pytest.mark.asyncio
async def test_reject_version_with_completely_different_content(
    authorized_client,
    created_document_with_text,
    db_session,
):
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/version",
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
        "The uploaded document is too different "
        "from the previous version"
    )
    assert len(versions) == 1

from unittest.mock import AsyncMock

import pytest

from app.documents.ai_service import ai_service


@pytest.mark.asyncio
async def test_diff_unauthorized_user(client):
    response = await client.post("/documents/1/diff")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_diff_document_another_user(
    authorized_client,
    created_document_with_text,
    another_user_token,
):
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/diff",
        headers={"Authorization": f"Bearer {another_user_token}"},
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_diff(authorized_client, created_document_with_text):
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
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/diff",
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data["version_from"] == 1
    assert data["version_to"] == 2
    assert data["diff_summary"] == "no changes"


@pytest.mark.asyncio
async def test_diff_with_changes(
    authorized_client,
    created_document_with_text,
    monkeypatch,
):
    create_version_response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/versions",
        files={
            "file": (
                "document_1.txt",
                "document_1 new",
                "text/plain",
            )
        },
    )
    assert create_version_response.status_code == 201
    ai_mock = AsyncMock(return_value="change")
    monkeypatch.setattr(ai_service, "diff_versions", ai_mock)
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/diff",
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    ai_mock.assert_awaited_once_with("- document_1\n+ document_1 new")
    data = response.json()
    assert response.status_code == 200
    assert data["diff_summary"] == "change"


@pytest.mark.asyncio
async def test_diff_with_nonexistent_document(authorized_client):
    response = await authorized_client.post(
        "/documents/999/diff",
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"


@pytest.mark.asyncio
async def test_diff_with_nonexistent_version_first(
    authorized_client,
    created_document,
):
    response = await authorized_client.post(
        f"/documents/{created_document['id']}/diff",
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Version 1 does not exist"


@pytest.mark.asyncio
async def test_diff_with_nonexistent_version_second(
    authorized_client,
    created_document_with_text,
):
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/diff",
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Version 2 does not exist"


@pytest.mark.asyncio
async def test_diff_cache(
    authorized_client,
    created_document_with_text,
    monkeypatch,
):
    create_version_response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/versions",
        files={
            "file": (
                "document_1.txt",
                "document_1 new",
                "text/plain",
            )
        },
    )
    assert create_version_response.status_code == 201
    ai_mock = AsyncMock(return_value="change")
    monkeypatch.setattr(ai_service, "diff_versions", ai_mock)
    response_diff = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/diff",
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    assert response_diff.status_code == 200
    response = await authorized_client.post(
        f"/documents/{created_document_with_text['id']}/diff",
        json={
            "version_from": 1,
            "version_to": 2,
        },
    )
    assert response.status_code == 200
    assert response_diff.json()["diff_summary"] == response.json()["diff_summary"]
    assert response.json()["diff_summary"] == "change"
    # Verify that the second request uses the cached result instead of calling AI again.
    ai_mock.assert_awaited_once_with("- document_1\n+ document_1 new")

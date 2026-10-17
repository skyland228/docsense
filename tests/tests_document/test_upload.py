import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import DocumentStatus


@pytest.mark.asyncio
async def test_upload_document(authorized_client):
    content = b"document_1"
    response = await authorized_client.post(
        "/documents",
        files={"file": ("document_1.txt", content, "text/plain")},
        params={"auto_extract": False},
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

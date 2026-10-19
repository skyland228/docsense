from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_get_pdf_document_text(authorized_client):
    pdf_path = Path(__file__).parent.parent / "fixtures" / "sample.pdf"
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
async def test_get_document_text_unauthorized_user(client, created_document_with_text):
    client.headers.pop("Authorization", None)
    response = await client.get(f"/documents/{created_document_with_text['id']}/text")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_document_text_nonexistent(authorized_client):
    response = await authorized_client.get("/documents/999/text")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document does not exist"

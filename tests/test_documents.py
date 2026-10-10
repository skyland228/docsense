from pathlib import Path

import pytest

from app.db.models.document import DocumentStatus


@pytest.mark.asyncio
async def test_upload_document(authorized_client):
    content = b'document_1'
    response = await authorized_client.post(
        '/documents',
        files={
            'file':(
                'document_1.txt',
                content,
                'text/plain',
            )
        }, 
    )
    data = response.json()
    assert response.status_code == 201
    assert type(data['id']) == int
    assert data['original_filename'] == 'document_1.txt'
    assert data['size'] == len(content)
    assert data['content_type'] == 'text/plain'
    assert data['status'] == DocumentStatus.uploaded


@pytest.mark.asyncio
async def test_process_document(authorized_client, created_document):
    response = await authorized_client.post(
        f'/documents/{created_document['id']}/process'
    )
    data = response.json()
    assert response.status_code == 200
    assert data['status'] == DocumentStatus.ready


@pytest.mark.asyncio
async def test_get_txt_document_text(authorized_client, created_document):
    process_response = await authorized_client.post(
        f'/documents/{created_document['id']}/process',
    )
    assert process_response.status_code == 200
    response = await authorized_client.get(f'/documents/{created_document['id']}/text')
    data = response.text
    assert response.status_code == 200
    assert data == 'document_1'


@pytest.mark.asyncio
async def test_get_pdf_document_text(authorized_client):
    pdf_path = Path(__file__).parent / 'fixtures' / 'sample.pdf'
    with pdf_path.open('rb') as file:
        upload_response = await authorized_client.post(
            '/documents',
            files={'file':('sample.pdf', file, 'application/pdf')},
        )
        assert upload_response.status_code == 201
        document_id = upload_response.json()['id']
    process_response = await authorized_client.post(
        f'/documents/{document_id}/process',
    )
    assert process_response.status_code == 200
    response = await authorized_client.get(f'/documents/{document_id}/text')
    assert response.status_code == 200
    assert "Привет, мир!" in response.text


@pytest.mark.asyncio
async def test_get_documents(authorized_client, created_document):
    response = await authorized_client.get("/documents")
    assert response.status_code == 200
    assert type(response.json()) is list
    data = response.json()
    assert any(
        document['id'] == created_document['id']
        for document in data
    )
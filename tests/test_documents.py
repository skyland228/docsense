


import pytest


@pytest.mark.asyncio
async def test_get_documents(authorized_client):
    response = await authorized_client.get("/documents")
    assert response.status_code == 200
async def test_missing_api_key_returns_401(async_client):
    response = await async_client.get("/api/v1/routes")
    assert response.status_code == 401


async def test_wrong_api_key_returns_401(async_client):
    response = await async_client.get(
        "/api/v1/routes",
        headers={"X-Internal-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


async def test_valid_api_key_passes(async_client):
    response = await async_client.get(
        "/api/v1/routes",
        headers={"X-Internal-API-Key": "test-api-key"},
    )
    assert response.status_code != 401


async def test_health_exempt_from_auth(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200


async def test_docs_exempt_from_auth(async_client):
    response = await async_client.get("/docs")
    assert response.status_code == 200

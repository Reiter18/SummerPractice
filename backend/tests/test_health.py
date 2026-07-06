import pytest


@pytest.mark.anyio
async def test_health_check(client):
    """Базовый health check — корневой эндпоинт."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_health_check_detailed(client):
    """Детальный health check — ключ app должен быть ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert data["app"] == "ok"
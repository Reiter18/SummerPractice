from app.main import app
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """
    Асинхронный тестовый HTTP-клиент.
    """
    mock_es = MagicMock()
    mock_es.ping.return_value = True
    mock_es.indices.exists.return_value = False
    mock_es.indices.create.return_value = {}
    mock_es.index.return_value = {"result": "created"}
    mock_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
    mock_es.info.return_value = {"version": {"number": "8.0.0"}}

    with patch("app.dependencies.get_elasticsearch_client", return_value=mock_es), \
         patch("app.redis_client.RedisCache.get", new_callable=AsyncMock, return_value=None), \
         patch("app.redis_client.RedisCache.set", new_callable=AsyncMock, return_value=None), \
         patch("app.redis_client.RedisCache.delete", new_callable=AsyncMock, return_value=None):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            yield ac
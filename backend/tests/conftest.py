from app.main import app
import pytest
import io
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """
    Асинхронный тестовый HTTP-клиент.
    Все внешние сервисы (ES, Redis, PostgreSQL) замокированы,
    чтобы тесты работали без запущенного Docker.
    """
    mock_es = MagicMock()
    mock_es.ping.return_value = True
    mock_es.indices.exists.return_value = False
    mock_es.indices.create.return_value = {}
    mock_es.index.return_value = {"result": "created"}
    mock_es.search.return_value = {
        "hits": {
            "total": {"value": 0},
            "hits": []
        }
    }

    mock_db_session = AsyncMock()
    mock_db_session.execute.return_value = AsyncMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
    mock_db_session.commit = AsyncMock()
    mock_db_session.add = MagicMock()

    with patch("app.dependencies.get_elasticsearch_client", return_value=mock_es), \
         patch("app.database.get_db", return_value=mock_db_session), \
         patch("app.redis_client.RedisCache.get", new_callable=AsyncMock, return_value=None), \
         patch("app.redis_client.RedisCache.set", new_callable=AsyncMock, return_value=None), \
         patch("app.redis_client.RedisCache.delete", new_callable=AsyncMock, return_value=None):

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            yield ac


def make_upload_file(filename: str, content: bytes = b"fake content"):
    """
    Хелпер — создаёт объект UploadFile для юнит-тестов валидатора.
    Используется в test_validators.py напрямую (без HTTP-клиента).
    """
    from fastapi import UploadFile
    file_obj = io.BytesIO(content)
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = filename
    mock_file.file = file_obj
    return mock_file
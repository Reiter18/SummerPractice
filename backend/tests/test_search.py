import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_elasticsearch_client
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


def make_es_client_mock(index_exists: bool = True, search_result: dict = None):
    mock = MagicMock()
    mock.indices.exists.return_value = index_exists
    if search_result is not None:
        mock.search.return_value = search_result
    return mock


def make_es_response(hits: list, total: int):
    return {
        "hits": {
            "total": {"value": total},
            "hits": hits,
        }
    }


def make_hit(chunk_id, document_id, file_name, page_number, text, score=1.5, highlight=None):
    hit = {
        "_score": score,
        "_source": {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "file_name": file_name,
            "page_number": page_number,
            "text": text,
        },
    }
    if highlight:
        hit["highlight"] = {"text": highlight}
    return hit


@pytest.fixture
def mock_db():
    db = AsyncMock(spec=AsyncSession)
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def override_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.pop(get_db, None)


# Тест 1: Успешный поиск
@pytest.mark.asyncio
async def test_search_success(override_db):
    hit = make_hit("chunk-1", "doc-1", "test.pdf", 1, "Python — язык программирования")
    es_mock = make_es_client_mock(
        index_exists=True,
        search_result=make_es_response([hit], total=1),
    )
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    with patch("app.redis_client.RedisCache.get", new=AsyncMock(return_value=None)), \
         patch("app.redis_client.RedisCache.set", new=AsyncMock()):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/search/", params={"q": "python"})

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "python"
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert data["from_cache"] is False
    assert data["results"][0]["chunk_id"] == "chunk-1"
    assert data["results"][0]["file_name"] == "test.pdf"
    assert data["results"][0]["page"] == 1


# Тест 2: Результат из кеша (Redis HIT)
@pytest.mark.asyncio
async def test_search_returns_cached_result(override_db):
    cached_data = {
        "query": "python",
        "total": 1,
        "results": [
            {
                "chunk_id": "chunk-cached",
                "document_id": "doc-cached",
                "file_name": "cached.pdf",
                "page": 2,
                "text": "Из кеша",
                "score": 1.0,
            }
        ],
        "from_cache": False,
    }

    es_mock = make_es_client_mock(index_exists=True)
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    with patch("app.redis_client.RedisCache.get", new=AsyncMock(return_value=cached_data)), \
         patch("app.redis_client.RedisCache.set", new=AsyncMock()):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/search/", params={"q": "python"})

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 200
    data = response.json()
    assert data["from_cache"] is True
    assert data["results"][0]["chunk_id"] == "chunk-cached"
    es_mock.search.assert_not_called()


# Тест 3: ES индекс не существует
@pytest.mark.asyncio
async def test_search_index_not_exists(override_db):
    es_mock = make_es_client_mock(index_exists=False)
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    with patch("app.redis_client.RedisCache.get", new=AsyncMock(return_value=None)), \
         patch("app.redis_client.RedisCache.set", new=AsyncMock()):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/search/", params={"q": "python"})

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


# Тест 4: Пустой запрос — 422
@pytest.mark.asyncio
async def test_search_empty_query(override_db):
    es_mock = make_es_client_mock()
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/search/", params={"q": ""})

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 422


# Тест 5: Отсутствует параметр q — 422
@pytest.mark.asyncio
async def test_search_missing_query(override_db):
    es_mock = make_es_client_mock()
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/search/")

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 422


# Тест 6: Пагинация
@pytest.mark.asyncio
async def test_search_pagination(override_db):
    es_mock = make_es_client_mock(index_exists=True)
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    with patch("app.redis_client.RedisCache.get", new=AsyncMock(return_value=None)), \
         patch("app.redis_client.RedisCache.set", new=AsyncMock()), \
         patch(
             "app.services.elasticsearch_service.ElasticsearchService.search",
             return_value={"total": 0, "results": []},
         ) as mock_search:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/search/", params={"q": "тест", "size": 5, "page": 2}
            )

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 200
    mock_search.assert_called_once_with(query="тест", size=5, from_=5)


# Тест 7: size > 100 — 422
@pytest.mark.asyncio
async def test_search_size_exceeds_max(override_db):
    es_mock = make_es_client_mock()
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/search/", params={"q": "тест", "size": 200}
        )

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 422


# Тест 8: page < 1 — 422
@pytest.mark.asyncio
async def test_search_page_less_than_one(override_db):
    es_mock = make_es_client_mock()
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/search/", params={"q": "тест", "page": 0}
        )

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 422


# Тест 9: ES возвращает пустой результат
@pytest.mark.asyncio
async def test_search_no_results(override_db):
    es_mock = make_es_client_mock(
        index_exists=True,
        search_result=make_es_response([], total=0),
    )
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    with patch("app.redis_client.RedisCache.get", new=AsyncMock(return_value=None)), \
         patch("app.redis_client.RedisCache.set", new=AsyncMock()):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/search/", params={"q": "несуществующееслово"}
            )

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []
    assert data["from_cache"] is False


# Тест 10: Highlight — текст берётся из highlight
@pytest.mark.asyncio
async def test_search_uses_highlight_text(override_db):
    highlight_text = "...Python является <em>языком</em> программирования..."

    es_mock = make_es_client_mock(index_exists=True)
    app.dependency_overrides[get_elasticsearch_client] = lambda: es_mock

    mock_result = {
        "total": 1,
        "results": [
            {
                "chunk_id": "chunk-hl",
                "document_id": "doc-hl",
                "file_name": "hl.pdf",
                "page": 3,
                "text": highlight_text,
                "score": 1.5,
            }
        ],
    }

    with patch("app.redis_client.RedisCache.get", new=AsyncMock(return_value=None)), \
         patch("app.redis_client.RedisCache.set", new=AsyncMock()), \
         patch(
             "app.services.elasticsearch_service.ElasticsearchService.search",
             return_value=mock_result,
         ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/search/", params={"q": "python"})

    app.dependency_overrides.pop(get_elasticsearch_client, None)

    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["text"] == highlight_text
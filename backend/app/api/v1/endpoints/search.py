from fastapi import APIRouter, Query, Depends
from elasticsearch import Elasticsearch
import time
import hashlib

from app.dependencies import get_elasticsearch_client
from app.models import SearchResponse, SearchResultItem
from app.services.elasticsearch_service import ElasticsearchService
from app.services.index_manager import IndexManager
from app.redis_client import RedisCache
from app.database import get_db, SearchLog
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/", response_model=SearchResponse)
async def search(
        q: str = Query(..., min_length=1, description="Поисковый запрос"),
        size: int = Query(10, ge=1, le=100, description="Количество результатов"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        es_client: Elasticsearch = Depends(get_elasticsearch_client),
        db: AsyncSession = Depends(get_db)
):

    start_time = time.time()

    query_str = f"{q}:{size}:{page}"
    cache_key = f"search:{hashlib.md5(query_str.encode()).hexdigest()}"

    cached = await RedisCache.get(cache_key)
    if cached:
        cached.pop('from_cache', None)
        cached['from_cache'] = True
        return SearchResponse(**cached)

    if not es_client.indices.exists(index=IndexManager.INDEX_NAME):
        return SearchResponse(query=q, total=0, results=[], from_cache=False)

    es_service = ElasticsearchService(es_client)
    from_ = (page - 1) * size
    result = es_service.search(query=q, size=size, from_=from_)

    items = [
        SearchResultItem(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            file_name=r["file_name"],
            page=r["page"],
            text=r["text"],
            score=r["score"]
        )
        for r in result["results"]
    ]

    response = SearchResponse(
        query=q,
        total=result["total"],
        results=items,
        from_cache=False
    )

    await RedisCache.set(
        cache_key,
        response.model_dump()
    )

    elapsed_ms = int((time.time() - start_time) * 1000)
    await log_search(db, q, result["total"], elapsed_ms)

    return response


async def log_search(db: AsyncSession, query: str, results_count: int, response_time_ms: int):
    log = SearchLog(
        query=query,
        results_count=results_count,
        response_time_ms=response_time_ms
    )
    db.add(log)
    await db.commit()
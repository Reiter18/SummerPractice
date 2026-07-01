from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import router
from app.config import settings
from app.services.index_manager import IndexManager
from app.dependencies import get_elasticsearch_client
from app.database import init_db
from app.redis_client import RedisCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print("PostgreSQL готов к работе")
    except Exception:
        traceback.print_exc()

    try:
        es_client = get_elasticsearch_client()
        IndexManager.create_index(es_client)
        print("Elasticsearch готов к работе")
    except Exception as e:
        print(f"Ошибка Elasticsearch: {e}")

    try:
        await RedisCache.get_client()
        print("Redis готов к работе")
    except Exception as e:
        print(f"Ошибка Redis: {e}")

    yield
    print("Завершение работы приложения")


app = FastAPI(
    title="Intelligent Search System - Backend",
    description="Поисковая система по внутренней базе знаний университета",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)
app.include_router(router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "search-backend"}


@app.get("/health", tags=["Health"])
async def health_check_detailed():
    from app.dependencies import get_elasticsearch_client
    import asyncpg

    status = {
        "app": "ok",
        "elasticsearch": "unknown",
        "postgresql": "unknown",
        "redis": "unknown"
    }

    try:
        es_client = get_elasticsearch_client()
        info = es_client.info()
        status["elasticsearch"] = f"connected (v{info['version']['number']})"
    except Exception as e:
        status["elasticsearch"] = f"error: {str(e)}"

    try:
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        await conn.close()
        status["postgresql"] = "connected"
    except Exception as e:
        status["postgresql"] = f"error: {str(e)}"

    try:
        redis = await RedisCache.get_client()
        await redis.ping()
        status["redis"] = "connected"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"

    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )

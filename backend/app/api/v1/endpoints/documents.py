from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from elasticsearch import Elasticsearch
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_elasticsearch_client
from app.database import get_db, Document
from app.models import DocumentUploadResponse, DocumentInfo
from app.utils.validators import validate_file
from app.services.document_processor import DocumentProcessor
from app.services.elasticsearch_service import ElasticsearchService
from app.services.index_manager import IndexManager
from app.redis_client import RedisCache

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    es_client: Elasticsearch = Depends(get_elasticsearch_client),
    db: AsyncSession = Depends(get_db)
):
    validate_file(file)

    try:
        ext, chunks = DocumentProcessor.process_and_chunk(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Не удалось извлечь текст из файла"
        )

    document_id = chunks[0]["document_id"]

    IndexManager.create_index(es_client)

    es_service = ElasticsearchService(es_client)
    indexed_count = es_service.index_chunks(chunks)

    doc = Document(
        id=document_id,
        file_name=file.filename,
        file_size=file.size or 0,
        file_extension=ext,
        chunks_count=indexed_count,
        status="indexed" if indexed_count > 0 else "failed"
    )
    db.add(doc)
    await db.commit()

    await RedisCache.delete("documents_list")

    return DocumentUploadResponse(
        document_id=document_id,
        file_name=file.filename,
        file_size=file.size or 0,
        chunks_indexed=indexed_count,
        status="success" if indexed_count > 0 else "partial",
        message=f"Успешно проиндексировано {indexed_count} чанков"
    )


@router.get("/", response_model=List[DocumentInfo])
async def get_documents(
    db: AsyncSession = Depends(get_db),
    es_client: Elasticsearch = Depends(get_elasticsearch_client)
):
    cache_key = "documents_list"
    cached = await RedisCache.get(cache_key)
    if cached:
        return cached

    from sqlalchemy import select
    result = await db.execute(
        select(Document).order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()

    response = [
        DocumentInfo(
            document_id=doc.id,
            file_name=doc.file_name,
            uploaded_at=doc.uploaded_at,
            chunks_count=doc.chunks_count,
            file_size=doc.file_size,
            status=doc.status
        )
        for doc in documents
    ]

    await RedisCache.set(cache_key, [r.model_dump() for r in response])

    return response


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    es_client: Elasticsearch = Depends(get_elasticsearch_client),
    db: AsyncSession = Depends(get_db)
):
    es_service = ElasticsearchService(es_client)
    es_service.delete_document(document_id)

    from sqlalchemy import delete
    await db.execute(
        delete(Document).where(Document.id == document_id)
    )
    await db.commit()

    await RedisCache.delete("documents_list")

    return {"status": "deleted", "document_id": document_id}
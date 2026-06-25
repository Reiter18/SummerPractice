from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    file_name: str
    file_size: int
    chunks_indexed: int
    status: str
    message: Optional[str] = None


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    page: int
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResultItem]
    from_cache: bool = False  # BE-10: индикатор кеширования


class DocumentInfo(BaseModel):
    document_id: str
    file_name: str
    uploaded_at: datetime
    chunks_count: int
    file_size: int
    status: str
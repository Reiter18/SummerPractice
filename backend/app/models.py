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
    from_cache: bool = False


class DocumentInfo(BaseModel):
    document_id: str
    file_name: str
    uploaded_at: datetime
    chunks_count: int
    file_size: int
    status: str


class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 часа


class UserResponse(BaseModel):
    username: str
    email: Optional[str] = None
    created_at: datetime
    is_active: bool = True
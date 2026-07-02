import pytest
import io
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app
from app.database import get_db


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def make_fake_chunks(doc_id: str, filename: str = "test.pdf"):
    return [
        {
            "chunk_id": f"{doc_id}_0",
            "document_id": doc_id,
            "file_name": filename,
            "page_number": 1,
            "text": "Тестовый текст документа",
            "chunk_index": 0,
        }
    ]


def get_mock_db_override():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.close = AsyncMock()
    mock_db.rollback = AsyncMock()

    async def override():
        yield mock_db

    return override


@pytest.mark.anyio
async def test_upload_valid_pdf(client):
    """Успешная загрузка PDF — статус 200, document_id в формате UUID."""
    fake_doc_id = str(uuid.uuid4())

    app.dependency_overrides[get_db] = get_mock_db_override()

    try:
        with patch("app.api.v1.endpoints.documents.DocumentProcessor.process_and_chunk",
                   return_value=(".pdf", make_fake_chunks(fake_doc_id))), \
             patch("app.api.v1.endpoints.documents.IndexManager.create_index",
                   return_value=None), \
             patch("app.api.v1.endpoints.documents.ElasticsearchService") as mock_es_cls:

            mock_es_instance = MagicMock()
            mock_es_instance.index_chunks.return_value = 1
            mock_es_cls.return_value = mock_es_instance

            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
            )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert len(data["document_id"]) == 36
    assert data["document_id"].count("-") == 4


@pytest.mark.anyio
async def test_upload_invalid_extension_txt(client):
    """Загрузка TXT-файла — должен вернуть 400."""
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("document.txt", io.BytesIO(b"plain text"), "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_upload_invalid_extension_jpg(client):
    """Загрузка JPG-файла — должен вернуть 400."""
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("photo.jpg", io.BytesIO(b"fake image"), "image/jpeg")},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_upload_document_id_is_uuid_format(client):
    """document_id должен быть валидным UUID."""
    fake_doc_id = str(uuid.uuid4())

    app.dependency_overrides[get_db] = get_mock_db_override()

    try:
        with patch("app.api.v1.endpoints.documents.DocumentProcessor.process_and_chunk",
                   return_value=(".pdf", make_fake_chunks(fake_doc_id))), \
             patch("app.api.v1.endpoints.documents.IndexManager.create_index",
                   return_value=None), \
             patch("app.api.v1.endpoints.documents.ElasticsearchService") as mock_es_cls:

            mock_es_instance = MagicMock()
            mock_es_instance.index_chunks.return_value = 1
            mock_es_cls.return_value = mock_es_instance

            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")},
            )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    doc_id = response.json()["document_id"]
    try:
        uuid.UUID(doc_id)
    except ValueError:
        pytest.fail(f"document_id '{doc_id}' не является валидным UUID")


@pytest.mark.anyio
async def test_upload_missing_file(client):
    """Запрос без файла — должен вернуть 422."""
    response = await client.post("/api/v1/documents/upload")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_upload_wrong_format_from_fixture(client):
    """Файл wrong_format.txt из fixtures — должен вернуть 400."""
    fixture_path = os.path.join(FIXTURES_DIR, "wrong_format.txt")
    with open(fixture_path, "rb") as f:
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("wrong_format.txt", f, "text/plain")},
        )
    assert response.status_code == 400

@pytest.mark.anyio
async def test_upload_empty_pdf_from_fixture(client):
    """Пустой PDF из fixtures — должен вернуть 400 (нет текста)."""
    fake_doc_id = str(uuid.uuid4())
    fixture_path = os.path.join(FIXTURES_DIR, "empty.pdf")

    app.dependency_overrides[get_db] = get_mock_db_override()
    try:
        with patch("app.api.v1.endpoints.documents.DocumentProcessor.process_and_chunk",
                   return_value=(".pdf", [])), \
             patch("app.api.v1.endpoints.documents.IndexManager.create_index",
                   return_value=None):
            with open(fixture_path, "rb") as f:
                response = await client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("empty.pdf", f, "application/pdf")},
                )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 400
import pytest
from fastapi import UploadFile
from unittest.mock import MagicMock
from app.utils.validators import validate_file
from fastapi import HTTPException


def make_upload_file(filename: str, size: int) -> UploadFile:
    mock_file = MagicMock()
    mock_file.seek = MagicMock()
    # tell() возвращает размер при вызове после seek(0, 2)
    mock_file.tell = MagicMock(return_value=size)
    upload = MagicMock(spec=UploadFile)
    upload.filename = filename
    upload.file = mock_file
    return upload


def test_validate_file_valid_pdf():
    """Валидный PDF небольшого размера — не должен бросать исключение."""
    f = make_upload_file("document.pdf", 1 * 1024 * 1024)  # 1 MB
    validate_file(f)  # не должно быть исключения


def test_validate_file_valid_docx():
    """Валидный DOCX небольшого размера — не должен бросать исключение."""
    f = make_upload_file("document.docx", 5 * 1024 * 1024)  # 5 MB
    validate_file(f)


def test_validate_file_invalid_extension_txt():
    """TXT-файл — должен вернуть 400."""
    f = make_upload_file("document.txt", 1024)
    with pytest.raises(HTTPException) as exc_info:
        validate_file(f)
    assert exc_info.value.status_code == 400
    assert "формат" in exc_info.value.detail.lower()


def test_validate_file_invalid_extension_exe():
    """EXE-файл — должен вернуть 400."""
    f = make_upload_file("malware.exe", 1024)
    with pytest.raises(HTTPException) as exc_info:
        validate_file(f)
    assert exc_info.value.status_code == 400


def test_validate_file_no_extension():
    """Файл без расширения — должен вернуть 400."""
    f = make_upload_file("nodotfile", 1024)
    with pytest.raises(HTTPException) as exc_info:
        validate_file(f)
    assert exc_info.value.status_code == 400


def test_validate_file_too_large():
    """Файл больше максимального размера — должен вернуть 400."""
    f = make_upload_file("big.pdf", 21 * 1024 * 1024)  # 21 MB > 20 MB
    with pytest.raises(HTTPException) as exc_info:
        validate_file(f)
    assert exc_info.value.status_code == 400
    assert "большой" in exc_info.value.detail.lower()


def test_validate_file_exactly_max_size():
    """Файл ровно 20 МБ — должен пройти валидацию."""
    f = make_upload_file("exact.pdf", 20 * 1024 * 1024)
    validate_file(f)  # не должно быть исключения
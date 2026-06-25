from fastapi import UploadFile, HTTPException
from app.config import settings
import os

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_file(file: UploadFile) -> None:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимальный размер: {settings.max_file_size_mb} МБ"
        )
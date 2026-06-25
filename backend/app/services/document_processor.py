import uuid
import io
from typing import List, Tuple
from fastapi import UploadFile
import pdfplumber
from docx import Document
from app.config import settings


class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> List[Tuple[int, str]]:
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                return [(page_num, page.extract_text() or "")
                        for page_num, page in enumerate(pdf.pages, start=1)
                        if (page.extract_text() or "").strip()]
        except Exception as e:
            raise ValueError(f"Ошибка парсинга PDF: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> List[Tuple[int, str]]:
        try:
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            return [(1, text)] if text.strip() else []
        except Exception as e:
            raise ValueError(f"Ошибка парсинга DOCX: {str(e)}")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap or settings.chunk_overlap

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                for i in range(end, max(start, end - 200), -1):
                    if text[i] in ' .!?;:':
                        end = i + 1
                        break
            chunks.append(text[start:end].strip())
            start = end - overlap if end < len(text) else end

        return [chunk for chunk in chunks if chunk]

    @staticmethod
    def process_and_chunk(file: UploadFile) -> tuple[str, List[dict]]:
        content = file.file.read()
        file.file.seek(0)

        ext = file.filename.split('.')[-1].lower()

        if ext == 'pdf':
            pages = DocumentProcessor.extract_text_from_pdf(content)
        elif ext == 'docx':
            pages = DocumentProcessor.extract_text_from_docx(content)
        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}")

        document_id = str(uuid.uuid4())
        all_chunks = []
        chunk_counter = 0

        for page_num, page_text in pages:
            for chunk_text in DocumentProcessor.chunk_text(page_text):
                all_chunks.append({
                    "chunk_id": f"{document_id}_{chunk_counter}",
                    "document_id": document_id,
                    "file_name": file.filename,
                    "page_number": page_num,
                    "text": chunk_text,
                    "chunk_index": chunk_counter,
                })
                chunk_counter += 1

        return ext, all_chunks
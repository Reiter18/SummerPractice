# Отчёт по юнит-тестированию бэкенда

## 1. Общая сводка

| Метрика             | Значение |
|---------------------|----------|
| Всего тестов        | 26       |
| Пройдено (PASSED)   | 26       |
| Упало (FAILED)      | 0        |
| Пропущено (SKIPPED) | 0        |
| Процент прохождения | 100%     |

> Все тесты пройдены успешно. Дефект BUG-001, выявленный в предыдущем запуске,
> исправлен в `search.py`.

---

## 2. Результаты запуска
tests/test_health.py::test_health_check PASSED [ 3%]
tests/test_health.py::test_health_check_detailed PASSED [ 7%]
tests/test_search.py::test_search_success PASSED [ 11%]
tests/test_search.py::test_search_returns_cached_result PASSED [ 15%]
tests/test_search.py::test_search_index_not_exists PASSED [ 19%]
tests/test_search.py::test_search_empty_query PASSED [ 23%]
tests/test_search.py::test_search_missing_query PASSED [ 26%]
tests/test_search.py::test_search_pagination PASSED [ 30%]
tests/test_search.py::test_search_size_exceeds_max PASSED [ 34%]
tests/test_search.py::test_search_page_less_than_one PASSED [ 38%]
tests/test_search.py::test_search_no_results PASSED [ 42%]
tests/test_search.py::test_search_uses_highlight_text PASSED [ 46%]
tests/test_upload.py::test_upload_valid_pdf PASSED [ 50%]
tests/test_upload.py::test_upload_invalid_extension_txt PASSED [ 53%]
tests/test_upload.py::test_upload_invalid_extension_jpg PASSED [ 57%]
tests/test_upload.py::test_upload_document_id_is_uuid_format PASSED [ 61%]
tests/test_upload.py::test_upload_missing_file PASSED [ 65%]
tests/test_upload.py::test_upload_wrong_format_from_fixture PASSED [ 69%]
tests/test_upload.py::test_upload_empty_pdf_from_fixture PASSED [ 73%]
tests/test_validators.py::test_validate_file_valid_pdf PASSED [ 76%]
tests/test_validators.py::test_validate_file_valid_docx PASSED [ 80%]
tests/test_validators.py::test_validate_file_invalid_extension_txt PASSED [ 84%]
tests/test_validators.py::test_validate_file_invalid_extension_exe PASSED [ 88%]
tests/test_validators.py::test_validate_file_no_extension PASSED [ 92%]
tests/test_validators.py::test_validate_file_too_large PASSED [ 96%]
tests/test_validators.py::test_validate_file_exactly_max_size PASSED [100%]

---

## 3. Результаты по модулям

### 3.1 `test_health.py` — Работоспособность сервиса

| №  | Тест                         | Описание                               | Статус    |
|----|------------------------------|----------------------------------------|-----------|
| 1  | `test_health_check`          | Сервис отвечает на базовый запрос      | ✅ PASSED |
| 2  | `test_health_check_detailed` | Ответ содержит корректные поля статуса | ✅ PASSED |

**Итого: 2 / 2**

---

### 3.2 `test_validators.py` — Валидация файлов

Тестируется функция `validate_file()` из `app/utils/validators.py`.
Допустимые форматы: `.pdf`, `.docx`. Максимальный размер: `settings.max_file_size_mb`.

| №  | Тест                                        | Описание                                        | Статус    |
|----|---------------------------------------------|-------------------------------------------------|-----------|
| 1  | `test_validate_file_valid_pdf`              | PDF проходит валидацию без исключений           | ✅ PASSED |
| 2  | `test_validate_file_valid_docx`             | DOCX проходит валидацию без исключений          | ✅ PASSED |
| 3  | `test_validate_file_invalid_extension_txt`  | Файл `.txt` → HTTP 400                          | ✅ PASSED |
| 4  | `test_validate_file_invalid_extension_exe`  | Файл `.exe` → HTTP 400                          | ✅ PASSED |
| 5  | `test_validate_file_no_extension`           | Файл без расширения → HTTP 400                  | ✅ PASSED |
| 6  | `test_validate_file_too_large`              | Размер файла превышает лимит → HTTP 400         | ✅ PASSED |
| 7  | `test_validate_file_exactly_max_size`       | Размер файла ровно на границе лимита → проходит | ✅ PASSED |

**Итого: 7 / 7**

---

### 3.3 `test_upload.py` — Загрузка документов

Тестируется эндпоинт `POST /api/v1/documents/upload`.
Зависимости Elasticsearch, PostgreSQL и Redis замокированы.

| №  | Тест                                     | Описание                                          | Статус    |
|----|------------------------------------------|---------------------------------------------------|-----------|
| 1  | `test_upload_valid_pdf`                  | Загрузка валидного PDF → 200, `status: indexed`   | ✅ PASSED |
| 2  | `test_upload_invalid_extension_txt`      | Загрузка `.txt` → 400 Bad Request                 | ✅ PASSED |
| 3  | `test_upload_invalid_extension_jpg`      | Загрузка `.jpg` → 400 Bad Request                 | ✅ PASSED |
| 4  | `test_upload_document_id_is_uuid_format` | В ответе `document_id` соответствует формату UUID | ✅ PASSED |
| 5  | `test_upload_missing_file`               | Запрос без файла → 422 Unprocessable Entity       | ✅ PASSED |
| 6  | `test_upload_wrong_format_from_fixture`  | Недопустимое расширение (фикстура) → 400          | ✅ PASSED |
| 7  | `test_upload_empty_pdf_from_fixture`     | Пустой PDF-файл (фикстура) → корректная обработка | ✅ PASSED |

**Итого: 7 / 7**

---

### 3.4 `test_search.py` — Поиск по документам

Тестируется эндпоинт `GET /api/v1/search/`.
Elasticsearch, Redis и PostgreSQL замокированы через `unittest.mock`.

| №  | Тест                                | Описание                                                        | Статус    |
|----|-------------------------------------|-----------------------------------------------------------------|-----------|
| 1  | `test_search_success`               | ES возвращает результат, `from_cache=False`                     | ✅ PASSED |
| 2  | `test_search_returns_cached_result` | Результат из Redis: `from_cache=True`, ES не вызывается         | ✅ PASSED |
| 3  | `test_search_index_not_exists`      | Индекс `documents` отсутствует → `total=0, results=[]`          | ✅ PASSED |
| 4  | `test_search_empty_query`           | `q=""` → 422 Unprocessable Entity                               | ✅ PASSED |
| 5  | `test_search_missing_query`         | Параметр `q` отсутствует → 422 Unprocessable Entity             | ✅ PASSED |
| 6  | `test_search_pagination`            | `size=5, page=2` → ES вызывается с `from_=5`                   | ✅ PASSED |
| 7  | `test_search_size_exceeds_max`      | `size=200` (максимум 100) → 422 Unprocessable Entity            | ✅ PASSED |
| 8  | `test_search_page_less_than_one`    | `page=0` (минимум 1) → 422 Unprocessable Entity                 | ✅ PASSED |
| 9  | `test_search_no_results`            | ES не находит документов → `total=0, results=[]`                | ✅ PASSED |
| 10 | `test_search_uses_highlight_text`   | Текст результата берётся из поля `highlight`, а не из `_source` | ✅ PASSED |

**Итого: 10 / 10**

---

## 4. Выводы

- **26 из 26 тестов** пройдены успешно — 100% прохождение.
- Дефект **BUG-001** выявлен, задокументирован и исправлен.
- Валидация файлов, загрузка документов и поисковый эндпоинт полностью соответствуют требованиям задания.
- Выявлено одно предупреждение (`PydanticDeprecatedSince20`) — некритично, рекомендуется исправить при обновлении зависимостей.
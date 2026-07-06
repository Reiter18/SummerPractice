# User Guide — Document Search System

**Версия:** 1.0  
**Дата:** 2026-07-05  
**Проект:** SummerPractice — система поиска по документам  

---

## Содержание

1. [Описание системы](#описание-системы)
2. [Требования](#требования)
3. [Запуск системы](#запуск-системы)
4. [Загрузка документов](#загрузка-документов)
5. [Поиск по документам](#поиск-по-документам)
6. [API — справочник эндпоинтов](#api--справочник-эндпоинтов)
7. [Частые ошибки](#частые-ошибки)
8. [Запуск тестов](#запуск-тестов)

---

## Описание системы

Document Search System — веб-приложение для загрузки и полнотекстового поиска по PDF и DOCX документам.

**Стек:**
- **Backend:** Python, FastAPI, PostgreSQL, Elasticsearch 8.0, Redis
- **Frontend:** React / Vue 3, TypeScript
- **Инфраструктура:** Docker, Docker Compose, GitHub Actions

**Основные возможности:**
- Загрузка PDF и DOCX файлов (до 20 МБ)
- Полнотекстовый поиск с подсветкой фрагментов
- Кэширование результатов поиска через Redis (TTL 5 минут)
- Индексация документов в Elasticsearch с русским анализатором
- REST API с документацией Swagger UI

---

## Требования

| Компонент      | Версия     |
|----------------|------------|
| Docker         | 20.x+      |
| Docker Compose | 2.x+       |
| Python         | 3.11+      |
| Node.js        | 18+        |

---

## Запуск системы

### Быстрый старт через Docker Compose

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Reiter18/SummerPractice.git
cd SummerPractice

# 2. Создать файл переменных окружения
cp .env.example .env

# 3. Запустить все сервисы
docker-compose up -d --build
```

После запуска доступны:

| Сервис         | Адрес                        |
|----------------|------------------------------|
| Frontend       | http://localhost:80           |
| Backend API    | http://localhost:8000         |
| Swagger UI     | http://localhost:8000/docs    |
| Elasticsearch  | http://localhost:9200         |

### Локальный запуск бэкенда (без Docker)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

---

## Загрузка документов

### Через веб-интерфейс

1. Открыть http://localhost:80
2. Нажать кнопку **«Загрузить документ»** или перетащить файл в зону Drag & Drop
3. Дождаться сообщения об успешной загрузке
4. Документ автоматически проиндексируется в Elasticsearch

### Через API

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"
```

**Ограничения:**
- Форматы: PDF, DOCX
- Максимальный размер: 20 МБ
- Пустые файлы не принимаются (HTTP 400)

---

## Поиск по документам

### Через веб-интерфейс

1. Ввести поисковый запрос в строку поиска
2. Нажать **Enter** или кнопку **«Найти»**
3. Результаты отображаются в виде карточек с фрагментами текста
4. Для перехода к следующей странице используйте пагинацию

### Через API

```bash
curl "http://localhost:8000/api/v1/search/?q=python&size=10&page=1"
```

**Параметры запроса:**

| Параметр | Тип    | По умолчанию  | Описание                         |
|----------|--------|---------------|----------------------------------|
| `q`      | string | обязательный  | Поисковый запрос (мин. 1 символ) |
| `size`   | int    | 10            | Количество результатов (1–100)   |
| `page`   | int    | 1             | Номер страницы                   |

**Пример ответа:**

```json
{
  "query": "python",
  "total": 5,
  "results": [
    {
      "chunk_id": "abc-123",
      "document_id": "def-456",
      "file_name": "document1.pdf",
      "page": 1,
      "text": "Python — высокоуровневый язык программирования...",
      "score": 4.82
    }
  ],
  "from_cache": false
}
```

---

## API — справочник эндпоинтов

| Метод  | Эндпоинт                          | Описание                          |
|--------|-----------------------------------|-----------------------------------|
| POST   | `/api/v1/auth/login`              | Авторизация, получение JWT токена |
| POST   | `/api/v1/documents/upload`        | Загрузка документа                |
| GET    | `/api/v1/documents/`              | Список всех документов            |
| DELETE | `/api/v1/documents/{document_id}` | Удаление документа                |
| GET    | `/api/v1/search/`                 | Поиск по документам               |
| GET    | `/api/v1/health/`                 | Проверка состояния сервиса        |

Полная интерактивная документация: **http://localhost:8000/docs**

---

## Частые ошибки

| Код | Причина                        | Решение                                 |
|-----|--------------------------------|-----------------------------------------|
| 400 | Неподдерживаемый формат файла  | Используйте только PDF или DOCX         |
| 400 | Пустой документ                | Файл должен содержать извлекаемый текст |
| 413 | Файл превышает 20 МБ           | Уменьшите размер файла                  |
| 422 | Неверные параметры запроса     | Проверьте имена и типы параметров       |
| 500 | Elasticsearch недоступен       | Убедитесь что docker-compose запущен    |

---

## Запуск тестов

```bash
cd backend

# Все тесты
pytest tests/ -v

# Только unit-тесты
pytest tests/test_validators.py tests/test_health.py tests/test_upload.py -v

# E2E тесты (требует запущенного фронтенда)
pytest tests/test_e2e_playwright.py -v

# Тест метрики Precision@3 (требует запущенного бэкенда и ES)
pytest tests/test_precision3.py -v -s

# Нагрузочные тесты
locust -f tests/locustfile.py --host=http://localhost:8000
# Затем открыть http://localhost:8089 → Users: 50, Spawn rate: 5
```

**Отчёты по тестам:**
- Unit-тесты: [`backend/docs/unit_tests_report.md`](unit_tests_report.md)
- E2E-тесты: [`backend/docs/e2e_tests_report.md`](e2e_tests_report.md)
- Нагрузочные тесты: [`backend/docs/load_tests_report.md`](load_tests_report.md)
- Precision@3: [`backend/docs/precision3_report.md`](precision3_report.md)
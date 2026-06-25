## Установка и запуск

### Локальный запуск (без Docker)

```bash
# 1. Перейти в папку бэкенда
cd backend

# 2. Создать виртуальное окружение
python -m venv venv

# 3. Активировать виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Создать .env из примера
cp .env.example .env

# 6. Запустить приложение
uvicorn app.main:app --reload
```

## Запуск через Docker

```bash
# Из корневой папки проекта
docker-compose up -d --build
```

## Документация

Swagger UI: http://localhost:8000/docs

# SummerPractice

## Локальный запуск через Docker
Требования: наличие Docker

```bash
# Клонирование репозитория
git clone https://github.com/Reiter18/SummerPractice.git

# Из корневой папки проекта
docker compose up --build

# (Опционально) Запуск скрипта, добавляющего 10 лекций в базу данных
bash init.sh
```

## Документация

Swagger UI: http://localhost:8000/docs
Frontend: http://localhost:80
Grafana: http://localhost:3000

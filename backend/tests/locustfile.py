"""
Нагрузочные тесты.
Имитация 50 одновременных пользователей, выполняющих поисковые запросы.

Запуск:
    cd backend
    locust -f tests/locustfile.py --host=http://localhost:8000

Затем открыть http://localhost:8089
Установить: Users = 50, Spawn rate = 5, нажать Start
"""

import os
from locust import HttpUser, task, between


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
LOGIN_DATA = {"username": "Furido", "password": "123456"}


def do_login(client):
    """Общая функция логина."""
    for _ in range(3):
        response = client.post(
            "/api/v1/auth/login",
            json=LOGIN_DATA,
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            client.headers.update({"Authorization": f"Bearer {token}"})
            return True
    return False


# ПОЛЬЗОВАТЕЛЬ 1 — выполняет поиск 4/5
class SearchUser(HttpUser):
    weight = 4
    wait_time = between(1, 3)

    def on_start(self):
        do_login(self.client)

    @task(5)
    def search_common_query(self):
        """Обычный поиск."""
        self.client.get(
            "/api/v1/search/",
            params={"q": "документ", "size": 10, "page": 1},
            name="/api/v1/search/ [общий запрос]",
        )

    @task(4)
    def search_specific_query(self):
        """Поиск конкретного термина."""
        self.client.get(
            "/api/v1/search/",
            params={"q": "elasticsearch поиск индекс", "size": 10, "page": 1},
            name="/api/v1/search/ [конкретный запрос]",
        )

    @task(3)
    def search_short_query(self):
        """Короткий однословный запрос."""
        self.client.get(
            "/api/v1/search/",
            params={"q": "python", "size": 5, "page": 1},
            name="/api/v1/search/ [короткий запрос]",
        )

    @task(3)
    def search_pagination_page2(self):
        """Запрос второй страницы результатов."""
        self.client.get(
            "/api/v1/search/",
            params={"q": "документ", "size": 10, "page": 2},
            name="/api/v1/search/ [страница 2]",
        )

    @task(2)
    def search_no_results(self):
        """Запрос без результатов."""
        self.client.get(
            "/api/v1/search/",
            params={"q": "zgxqwerty12345несуществует", "size": 10},
            name="/api/v1/search/ [нет результатов]",
        )

    @task(2)
    def get_documents_list(self):
        """Просмотр списка документов."""
        self.client.get(
            "/api/v1/documents/",
            name="/api/v1/documents/ [список]",
        )

    @task(1)
    def health_check(self):
        """Проверка здоровья сервиса."""
        self.client.get(
            "/health",
            name="/health",
        )


# ПОЛЬЗОВАТЕЛЬ 2 — загружает документы 1/5 от всех пользователей
class UploadUser(HttpUser):
    weight = 1
    wait_time = between(5, 15)

    def on_start(self):
        do_login(self.client)

    @task(1)
    def upload_pdf(self):
        with open(os.path.join(FIXTURES_DIR, "document1.pdf"), "rb") as f:
            self.client.post(
                "/api/v1/documents/upload",
                files={"file": ("loadtest.pdf", f, "application/pdf")},
                name="/api/v1/documents/upload [PDF]",
            )

    @task(2)
    def search_after_upload(self):
        self.client.get(
            "/api/v1/search/",
            params={"q": "loadtest", "size": 10},
            name="/api/v1/search/ [после загрузки]",
        )
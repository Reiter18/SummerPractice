# backend/tests/test_precision3.py
"""
Тест метрики Precision@3.
"""

import os
import pytest
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
LOGIN_DATA = {"username": "Furido", "password": "123456"}

GROUND_TRUTH = [
    ("python",                     ["document1.pdf"]),
    ("elasticsearch поиск индекс", ["document6.pdf"]),
    ("docker контейнер",           ["document5.pdf"]),
    ("postgresql база данных",     ["document2.pdf"]),
    ("машинное обучение",          ["document4.pdf"]),
    ("тестирование pytest",        ["document10.pdf"]),
    ("redis кэш",                  ["document8.pdf"]),
    ("git репозиторий",            ["document9.pdf"]),
    ("fastapi rest api",           ["document7.pdf"]),
    ("алгоритм сортировка",        ["document3.pdf"]),
]


def get_token() -> str:
    r = requests.post(f"{BASE_URL}/api/v1/auth/login", json=LOGIN_DATA)
    r.raise_for_status()
    return r.json()["access_token"]


def do_search(query: str) -> list[str]:
    """Возвращает имена уникальных файлов из топ-3 документов."""
    r = requests.get(
        f"{BASE_URL}/api/v1/search/",
        params={"q": query, "size": 15, "page": 1},  # берём с запасом
    )
    r.raise_for_status()
    results = r.json().get("results", [])

    seen = []
    for item in results:
        fname = item.get("file_name", "")
        if fname not in seen:
            seen.append(fname)
        if len(seen) == 3:
            break
    return seen


def precision_at_k(relevant: list[str], retrieved: list[str], k: int = 3) -> float:
    return round(sum(1 for d in retrieved[:k] if d in relevant) / k, 2)


def upload_all(token: str) -> None:
    """Загружает все 10 документов в систему."""
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(1, 11):
        path = os.path.join(FIXTURES_DIR, f"document{i}.pdf")
        with open(path, "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/api/v1/documents/upload",
                files={"file": (f"document{i}.pdf", f, "application/pdf")},
                headers=headers,
            )
            print(f"  upload document{i}.pdf → {resp.status_code}")


def cleanup_all(token: str) -> None:
    """Удаляет все документы после теста."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        docs = requests.get(
            f"{BASE_URL}/api/v1/documents/", headers=headers
        ).json()
        for doc in docs:
            requests.delete(
                f"{BASE_URL}/api/v1/documents/{doc['document_id']}",
                headers=headers,
            )
        print(f"  cleanup: удалено {len(docs)} документов")
    except Exception as e:
        print(f"  cleanup error: {e}")


@pytest.fixture(scope="module")
def token():
    return get_token()


@pytest.fixture(scope="module", autouse=True)
def prepare(token):
    upload_all(token)
    yield
    cleanup_all(token)


def test_precision3_summary(token):
    """Считает Precision@3 по всем 10 запросам и выводит сводную таблицу."""
    scores = []

    print("\n")
    print(f"{'Запрос':<35} {'Топ-3 результата':<50} {'P@3':>5}")
    print("─" * 93)

    for query, relevant in GROUND_TRUTH:
        retrieved = do_search(query)
        p3 = precision_at_k(relevant, retrieved)
        scores.append(p3)
        top3_str = ", ".join(retrieved[:3]) if retrieved else "нет результатов"
        print(f"{query:<35} {top3_str:<50} {p3:>5.2f}")

    mean_p3 = round(sum(scores) / len(scores), 2)
    print("─" * 93)
    print(f"{'Средний Precision@3':<85} {mean_p3:>5.2f}\n")

    assert mean_p3 >= 0.33, (
        f"Средний Precision@3 = {mean_p3} ниже минимального порога 0.33"
    )


@pytest.mark.parametrize("query,relevant", GROUND_TRUTH)
def test_relevant_in_top3(token, query, relevant):
    """Эталонный документ должен присутствовать в топ-3 результатов."""
    retrieved = do_search(query)
    assert any(doc in retrieved for doc in relevant), (
        f"Запрос '{query}': ожидался {relevant}, получено {retrieved}"
    )
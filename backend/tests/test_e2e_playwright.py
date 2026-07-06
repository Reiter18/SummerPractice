import os
import requests
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(autouse=True)
def cleanup_documents():
    """
    Удаляет все документы после каждого теста.
    """
    yield
    
    try:
        docs = requests.get("http://localhost:8000/api/v1/documents/").json()
        for doc in docs:
            requests.delete(
                f"http://localhost:8000/api/v1/documents/{doc['document_id']}"
            )
    except Exception:
        pass

FRONTEND_URL  = os.getenv("FRONTEND_URL", "http://localhost:80")
FIXTURES_DIR  = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_USER     = "Furido"
TEST_PASSWORD = "123456"

def login(page: Page):
    """Вход через UI."""
    page.goto(FRONTEND_URL)
    page.wait_for_load_state("networkidle")
    page.locator("input[placeholder='Имя пользователя']").fill(TEST_USER)
    page.locator("input[placeholder='Пароль']").fill(TEST_PASSWORD)
    page.locator("button:has-text('Войти')").click()
    page.wait_for_url(
        lambda url: "login" not in url and "auth" not in url,
        timeout=8000
    )
    page.wait_for_load_state("networkidle")


def do_search(page: Page, query: str):
    """Вводит запрос и нажимает кнопку Найти."""
    search_input = page.locator("input[placeholder='Введите поисковый запрос...']")
    search_input.fill(query)
    page.locator("button:has-text('Найти')").click()
    page.wait_for_load_state("networkidle")


def upload_file(page: Page, filename: str):
    """Загружает файл через input[type=file]."""
    path = os.path.join(FIXTURES_DIR, filename)
    page.locator("input[type='file']").first.set_input_files(path)


# СЦЕНАРИЙ 1: логин → загрузка → индексация → поиск → результаты
def test_e2e_upload_and_search(page: Page):
    """
    Главный сценарий:
    1. Логин
    2. Загрузка PDF
    3. Файл показывает статус "Готово" (индексация прошла)
    4. Поиск по ключевому слову
    5. Результаты отображаются на странице
    """
    login(page)

    upload_file(page, "document1.pdf")

    expect(page.locator("text=Готово")).to_be_visible(timeout=15000)

    expect(page.locator("button:has-text('Загрузить ещё')")).to_be_visible(timeout=5000)

    expect(page.get_by_text("document1.pdf").first).to_be_visible(timeout=5000)

    do_search(page, "document")

    page.wait_for_timeout(2000)

    no_results = page.locator("text=По вашему запросу ничего не найдено.")
    assert not no_results.is_visible(), "Поиск не нашёл результаты после загрузки документа"


# СЦЕНАРИЙ 2: Загрузка невалидного файла (.txt) → ошибка

def test_e2e_upload_invalid_file_shows_error(page: Page):
    """
    Загрузка .txt файла — неверный формат.
    """
    login(page)
    upload_file(page, "wrong_format.txt")

    expect(
        page.locator("text=File type must be one of")
    ).to_be_visible(timeout=8000)


# СЦЕНАРИЙ 3: Загрузка пустого PDF → ошибка парсинга
def test_e2e_upload_empty_pdf_shows_error(page: Page):
    """
    Загрузка empty.pdf.
    UI показывает: "Ошибка парсинга PDF" + кнопку "Попробовать снова".
    """
    login(page)
    upload_file(page, "empty.pdf")

    expect(
        page.locator("text=Ошибка парсинга PDF")
    ).to_be_visible(timeout=10000)

    expect(
        page.locator("button:has-text('Попробовать снова')")
    ).to_be_visible(timeout=5000)

    expect(page.locator("text=Ошибка").first).to_be_visible(timeout=5000)


# СЦЕНАРИЙ 4: Поиск без результатов → пустое состояние
def test_e2e_search_no_results(page: Page):
    """
    Поиск несуществующего слова.
    """
    login(page)

    do_search(page, "zgxqwerty12345несуществует")

    expect(
        page.locator("text=По вашему запросу ничего не найдено.")
    ).to_be_visible(timeout=8000)

    expect(
        page.locator("text=Попробуйте изменить формулировку")
    ).to_be_visible(timeout=5000)


# СЦЕНАРИЙ 5: Пагинация — не более 10 результатов
def test_e2e_search_pagination(page: Page):
    login(page)

    for i in range(1, 4):
        upload_file(page, f"document{i}.pdf")
        expect(page.locator("text=Готово").first).to_be_visible(timeout=15000)
        page.locator("button:has-text('Загрузить ещё')").click()
        page.wait_for_timeout(500)

    do_search(page, "document")
    page.wait_for_timeout(3000)

    no_results = page.locator("text=По вашему запросу ничего не найдено.")
    if no_results.is_visible():
        pytest.skip("Нет результатов для проверки пагинации")

    results = page.locator("text=Score:").all()
    if not results:
        results = page.locator("text=Релевантность").all()

    assert len(results) <= 10, (
        f"На странице должно быть не более 10 результатов, получено: {len(results)}"
    )


# СЦЕНАРИЙ 6: Мобильный viewport 375px
def test_e2e_responsive_mobile(page: Page):
    page.set_viewport_size({"width": 375, "height": 812})
    login(page)

    expect(
        page.locator("input[placeholder='Введите поисковый запрос...']")
    ).to_be_visible()

    expect(page.locator("input[type='file']").first).to_be_attached()

    expect(
        page.get_by_role("heading", name="Поиск по базе знаний")
    ).to_be_visible()


# СЦЕНАРИЙ 7: Desktop viewport 1920px
def test_e2e_responsive_desktop(page: Page):
    page.set_viewport_size({"width": 1920, "height": 1080})
    login(page)

    expect(
        page.locator("input[placeholder='Введите поисковый запрос...']")
    ).to_be_visible()

    expect(page.locator("input[type='file']").first).to_be_attached()

    expect(
        page.get_by_role("heading", name="Поиск по базе знаний")
    ).to_be_visible()
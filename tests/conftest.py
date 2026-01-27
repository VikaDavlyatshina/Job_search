import os
import tempfile
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple
from unittest.mock import Mock

import pytest

from src.storage import JSONSaver
from src.vacancy import Vacancy


# 1. ПРОСТАЯ ФАБРИКА ДЛЯ СОЗДАНИЯ ВАКАНСИЙ
@pytest.fixture
def make_vacancy() -> Callable[..., Vacancy]:
    """
    Простая функция для создания тестовой вакансии
    Можно задать только нужные параметры, остальные будут по умолчанию
    """

    def create(
        name: str = "Тестовая вакансия",
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        area: str = "Москва",
        requirement: str = "Требования",
        responsibility: str = "Обязанности",
        schedule: str = "Полный день",
        url: str = "https://test.com/vacancy",
    ) -> Vacancy:
        """
        Создает объект Vacancy

        Примеры использования:
        make_vacancy()  # вакансия со значениями по умолчанию
        make_vacancy(name="Python Dev", salary_from=100000)  # кастомная
        """
        return Vacancy(
            name=name,
            area=area,
            salary_from=salary_from,
            salary_to=salary_to,
            requirement=requirement,
            responsibility=responsibility,
            schedule=schedule,
            url=url,
        )

    return create


# 2. ГОТОВЫЕ ВАКАНСИИ ДЛЯ ТЕСТОВ
@pytest.fixture
def developer_vacancy(make_vacancy: Callable[..., Vacancy]) -> Vacancy:
    """Готовая вакансия разработчика с зарплатой"""
    return make_vacancy(name="Python Developer", salary_from=100000, salary_to=150000)


@pytest.fixture
def intern_vacancy(make_vacancy: Callable[..., Vacancy]) -> Vacancy:
    """Готовая вакансия стажера без зарплаты"""
    return make_vacancy(name="Стажер Python", salary_from=None, salary_to=None)


@pytest.fixture
def middle_vacancy(make_vacancy: Callable[..., Vacancy]) -> Vacancy:
    """Готовая вакансия с зарплатой только 'от'"""
    return make_vacancy(name="Middle Python Developer", salary_from=120000, salary_to=None)


# 3. ДВЕ ВАКАНСИИ ДЛЯ СРАВНЕНИЯ
@pytest.fixture
def junior_and_senior(make_vacancy: Callable[..., Vacancy]) -> Tuple[Vacancy, Vacancy]:
    """Возвращает две вакансии: младшего и старшего разработчика"""
    junior = make_vacancy(name="Junior Python", salary_from=50000, salary_to=70000)

    senior = make_vacancy(name="Senior Python", salary_from=200000, salary_to=300000)

    return junior, senior


# 4. ДАННЫЕ ОТ API (для тестирования метода from_vacancy_hh)
@pytest.fixture
def api_vacancy_with_salary() -> Dict[str, Any]:
    """Пример данных от HH API с зарплатой"""
    return {
        "name": "Python Developer",
        "area": {"name": "Москва"},
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "snippet": {
            "requirement": "Опыт работы от 3 лет. Знание Python и Django.",
            "responsibility": "Разработка backend-части приложений.",
        },
        "schedule": {"name": "Полный день"},
        "alternate_url": "https://hh.ru/vacancy/12345678",
    }


@pytest.fixture
def api_vacancy_no_salary() -> Dict[str, Any]:
    """Пример данных от HH API без зарплаты"""
    return {
        "name": "Стажер Python",
        "area": {"name": "Санкт-Петербург"},
        "salary": None,
        "snippet": {"requirement": "Базовые знания Python.", "responsibility": "Помощь в разработке."},
        "schedule": {"name": "Удаленная работа"},
        "alternate_url": "https://hh.ru/vacancy/87654321",
    }


# 5. ФИКСТУРЫ ДЛЯ API ТЕСТОВ
@pytest.fixture
def mock_api_response() -> Dict[str, Any]:
    """Фикстура возвращает готовые данные API"""
    return {
        "items": [
            {
                "name": "Python Developer",
                "salary": {"from": 100000, "to": 150000},
                "area": {"name": "Москва"},
                "snippet": {"requirement": "Python", "responsibility": "Code"},
                "alternate_url": "https://hh.ru/vacancy/123",
            },
            {
                "name": "Java Developer",
                "salary": None,
                "area": {"name": "Санкт-Петербург"},
                "snippet": {"requirement": "Java", "responsibility": "Code"},
                "alternate_url": "https://hh.ru/vacancy/135",
            },
        ],
        "pages": 1,
        "page": 0,
        "found": 2,
    }


@pytest.fixture
def mock_session(mock_api_response: Dict[str, Any]) -> Mock:
    """Фикстура создаёт готовую mock-сессию"""
    mock_sess = Mock()
    mock_resp = Mock()

    mock_resp.json.return_value = mock_api_response
    mock_resp.raise_for_status.return_value = None
    mock_resp.status_code = 200

    call_count = 0

    def get_side_effect(*args: Any, **kwargs: Any) -> Mock:
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            simple_resp = Mock()
            simple_resp.json.return_value = {"items": [{"id": "test"}], "pages": 1, "found": 1}
            simple_resp.raise_for_status.return_value = None
            simple_resp.status_code = 200
            return simple_resp

        return mock_resp

    mock_sess.get.side_effect = get_side_effect
    mock_sess.headers = {}

    return mock_sess


# 6. ФИКСТУРЫ ДЛЯ ТЕСТОВ STORAGE.PY
@pytest.fixture
def temp_json_file() -> Generator[str, None, None]:
    """
    Создает временный JSON файл для тестов
    Автоматически удаляется после теста
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")  # Пустой список
        temp_path = f.name

    yield temp_path  # Возвращаем путь к файлу

    # После теста удаляем файл
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def json_saver(temp_json_file: str) -> JSONSaver:
    """Создает JSONSaver с временным файлом"""
    return JSONSaver(temp_json_file)


@pytest.fixture
def sample_vacancy() -> Vacancy:
    """Тестовая вакансия Python разработчика"""
    return Vacancy(
        name="Python Developer",
        area="Москва",
        salary_from=100000,
        salary_to=150000,
        requirement="Знать Python",
        responsibility="Писать код",
        schedule="Полный день",
        url="https://hh.ru/vacancy/123",
    )


@pytest.fixture
def java_vacancy() -> Vacancy:
    """Тестовая вакансия Java разработчика"""
    return Vacancy(
        name="Java Developer",
        area="Санкт-Петербург",
        salary_from=120000,
        salary_to=180000,
        requirement="Знать Java",
        responsibility="Разработка",
        schedule="Удаленно",
        url="https://hh.ru/vacancy/456",
    )


@pytest.fixture
def python_developer() -> Vacancy:
    """
    Фикстура: вакансия Python разработчика

    Returns:
        Vacancy: Объект вакансии Python разработчика
    """
    return Vacancy(
        name="Python Developer",
        area="Москва",
        salary_from=100000,
        salary_to=150000,
        requirement="Знание Python и Django",
        responsibility="Разработка веб-приложений",
        schedule="Полный день",
        url="https://hh.ru/vacancy/1",
    )


@pytest.fixture
def java_developer() -> Vacancy:
    """
    Фикстура: вакансия Java разработчика

    Returns:
        Vacancy: Объект вакансии Java разработчика
    """
    return Vacancy(
        name="Java Developer",
        area="Санкт-Петербург",
        salary_from=120000,
        salary_to=180000,
        requirement="Знание Java и Spring",
        responsibility="Разработка backend",
        schedule="Удаленная работа",
        url="https://hh.ru/vacancy/2",
    )


@pytest.fixture
def frontend_developer() -> Vacancy:
    """
    Фикстура: вакансия Frontend разработчика

    Returns:
        Vacancy: Объект вакансии Frontend разработчика
    """
    return Vacancy(
        name="Frontend Developer",
        area="Москва",
        salary_from=90000,
        salary_to=130000,
        requirement="Знание JavaScript, React",
        responsibility="Разработка интерфейсов",
        schedule="Гибкий график",
        url="https://hh.ru/vacancy/3",
    )


@pytest.fixture
def python_intern() -> Vacancy:
    """
    Фикстура: вакансия стажера Python (без зарплаты)

    Returns:
        Vacancy: Объект вакансии стажера Python
    """
    return Vacancy(
        name="Стажер Python",
        area="Москва",
        salary_from=None,
        salary_to=None,
        requirement="Желание учиться",
        responsibility="Помощь команде",
        schedule="Полный день",
        url="https://hh.ru/vacancy/4",
    )


@pytest.fixture
def all_vacancies(
    python_developer: Vacancy,
    java_developer: Vacancy,
    frontend_developer: Vacancy,
    python_intern: Vacancy,
) -> List[Vacancy]:
    """
    Фикстура: все тестовые вакансии вместе

    Returns:
        List[Vacancy]: Список из 4 тестовых вакансий
    """
    return [python_developer, java_developer, frontend_developer, python_intern]

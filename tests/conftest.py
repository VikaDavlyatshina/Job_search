from unittest.mock import Mock
import pytest
from src.vacancy import Vacancy


# 1. ПРОСТАЯ ФАБРИКА ДЛЯ СОЗДАНИЯ ВАКАНСИЙ
@pytest.fixture
def make_vacancy():
    """
    Простая функция для создания тестовой вакансии
    Можно задать только нужные параметры, остальные будут по умолчанию
    """

    def create(name="Тестовая вакансия", salary_from=None, salary_to=None,
               area="Москва", requirement="Требования",
               responsibility="Обязанности", schedule="Полный день",
               url="https://test.com/vacancy"):
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
            url=url
        )

    return create


# 2. ГОТОВЫЕ ВАКАНСИИ ДЛЯ ТЕСТОВ
@pytest.fixture
def developer_vacancy(make_vacancy):
    """Готовая вакансия разработчика с зарплатой"""
    return make_vacancy(
        name="Python Developer",
        salary_from=100000,
        salary_to=150000
    )


@pytest.fixture
def intern_vacancy(make_vacancy):
    """Готовая вакансия стажера без зарплаты"""
    return make_vacancy(
        name="Стажер Python",
        salary_from=None,
        salary_to=None
    )


@pytest.fixture
def middle_vacancy(make_vacancy):
    """Готовая вакансия с зарплатой только 'от'"""
    return make_vacancy(
        name="Middle Python Developer",
        salary_from=120000,
        salary_to=None
    )


# 3. ДВЕ ВАКАНСИИ ДЛЯ СРАВНЕНИЯ
@pytest.fixture
def junior_and_senior(make_vacancy):
    """Возвращает две вакансии: младшего и старшего разработчика"""
    junior = make_vacancy(
        name="Junior Python",
        salary_from=50000,
        salary_to=70000
    )

    senior = make_vacancy(
        name="Senior Python",
        salary_from=200000,
        salary_to=300000
    )

    return junior, senior


# 4. ДАННЫЕ ОТ API (для тестирования метода from_vacancy_hh)
@pytest.fixture
def api_vacancy_with_salary():
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
def api_vacancy_no_salary():
    """Пример данных от HH API без зарплаты"""
    return {
        "name": "Стажер Python",
        "area": {"name": "Санкт-Петербург"},
        "salary": None,
        "snippet": {
            "requirement": "Базовые знания Python.",
            "responsibility": "Помощь в разработке."
        },
        "schedule": {"name": "Удаленная работа"},
        "alternate_url": "https://hh.ru/vacancy/87654321",
    }


# 5. ДЛЯ API ТЕСТОВ
@pytest.fixture
def mock_api_response():
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
def mock_session(mock_api_response):
    """Фикстура создаёт готовую mock-сессию"""
    mock_sess = Mock()
    mock_resp = Mock()

    mock_resp.json.return_value = mock_api_response
    mock_resp.raise_for_status.return_value = None
    mock_resp.status_code = 200

    call_count = 0

    def get_side_effect(*_, **__):
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
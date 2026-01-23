from unittest.mock import Mock

import pytest

from src.vacancy import Vacancy


@pytest.fixture
def sample_hh_vacancy_data():
    """
    Фикстура возвращает типичные данные вакансии от HH API
    Используется для тестирования from_vacancy_hh()

    Тестовые данные, которые имитируют реальный ответ API
    """

    return {
        "name": "Python Developer",
        "area": {"name": "Москва"},
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "snippet": {
            "requirement": "Опыт работы от 3 лет. Знание <strong>Python</strong> и Django.",
            "responsibility": "Разработка backend-части приложений.",
        },
        "schedule": {"name": "Полный день"},
        "alternate_url": "https://hh.ru/vacancy/12345678",
    }


@pytest.fixture
def sample_hh_vacancy_no_salary():
    """
     Фикстура: вакансия БЕЗ зарплаты (частый кейс в HH)
    Проверяем обработку None значений
    """

    return {
        "name": "Стажер Python",
        "area": {"name": "Санкт-Петербург"},
        "salary": None,
        "snippet": {"requirement": "Базовые знания Python.", "responsibility": "Помощь в разработке."},
        "schedule": {"name": "Удаленная работа"},
        "alternate_url": "https://hh.ru/vacancy/87654321",
    }


@pytest.fixture
def sample_hh_vacancy_partial_salary():
    """
    Фикстура: вакансия с ЧАСТИЧНО указанной зарплатой
    Только 'from' или только 'to'
    """
    return {
        "name": "Middle Python Developer",
        "area": {"name": "Новосибирск"},
        "salary": {"from": 120000, "to": None, "currency": "RUR"},  # Только нижняя граница
        "snippet": {"requirement": "Опыт работы от 1 года.", "responsibility": "Разработка и поддержка."},
        "schedule": {"name": "Гибкий график"},
        "alternate_url": "https://hh.ru/vacancy/55555555",
    }


@pytest.fixture
def vacancy_with_salary(sample_hh_vacancy_data):
    """
    Фикстура: создает РЕАЛЬНЫЙ объект Vacancy с зарплатой
    Использует данные из sample_hh_vacancy_data
    """
    return Vacancy.from_vacancy_hh(sample_hh_vacancy_data)


@pytest.fixture
def vacancy_without_salary(sample_hh_vacancy_no_salary):
    """
    Фикстура: создает объект Vacancy БЕЗ зарплаты
    """
    return Vacancy.from_vacancy_hh(sample_hh_vacancy_no_salary)


@pytest.fixture
def vacancy_partial_salary(sample_hh_vacancy_partial_salary):
    """
    Фикстура: создает объект Vacancy с частичной зарплатой
    """
    return Vacancy.from_vacancy_hh(sample_hh_vacancy_partial_salary)


@pytest.fixture
def two_vacancies_for_comparison():
    """
    Фикстура: создает ДВЕ вакансии для тестирования сравнения
    Одна с низкой зарплатой, другая с высокой
    """
    vacancy_low = Vacancy(
        name="Junior Python",
        area="Москва",
        salary_from=50000,
        salary_to=70000,
        requirement="Опыт не требуется",
        responsibility="Обучение",
        schedule="Полный день",
        url="https://hh.ru/vacancy/11111111",
    )

    vacancy_high = Vacancy(
        name="Senior Python",
        area="Москва",
        salary_from=200000,
        salary_to=300000,
        requirement="Опыт от 5 лет",
        responsibility="Разработка архитектуры",
        schedule="Полный день",
        url="https://hh.ru/vacancy/22222222",
    )

    return vacancy_low, vacancy_high


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

    # Счетчик вызовов - чтобы возвращать разные ответы
    call_count = 0

    def get_side_effect(*_, **__):
        nonlocal call_count
        call_count += 1

        # Первый запрос: проверка соединения (_connect)
        if call_count == 1:
            simple_resp = Mock()
            # Минимальный ответ для проверки соединения
            simple_resp.json.return_value = {"items": [{"id": "test"}], "pages": 1, "found": 1}
            simple_resp.raise_for_status.return_value = None
            simple_resp.status_code = 200
            return simple_resp

        # Второй и последующие запросы: возвращаем вакансии
        return mock_resp

    mock_sess.get.side_effect = get_side_effect
    mock_sess.headers = {}

    return mock_sess

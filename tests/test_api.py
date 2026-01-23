import pytest
from unittest.mock import patch, Mock
from src.api import HeadHunterAPI


def test_basic_api_works(mock_session: Mock) -> None:
    """Базовый тест проверки подключения к API"""
    with patch('src.api.requests.Session') as mock_session_class:
        mock_session_class.return_value = mock_session

        api = HeadHunterAPI()
        result = api.get_vacancies("Python", max_pages=1)

        assert len(result) == 2  # Две вакансии из mock_api_response
        assert result[0]["name"] == "Python Developer"
        assert result[1]["name"] == "Java Developer"


def test_empty_response() -> None:
    """Тестирование пустого ответа от API"""

    mock_response = Mock()
    mock_response.json.return_value = {
        "items": [],
        "pages": 0,
        "found": 0
    }

    mock_session = Mock()
    mock_session.get.return_value = mock_response

    with patch('src.api.requests.Session') as mock_session_class:
        mock_session_class.return_value = mock_session

        api = HeadHunterAPI()
        result = api.get_vacancies("НесуществующийЗапрос")

        assert len(result) == 0


def test_validation_errors() -> None:
    """Тестирование ошибки валидации"""
    api = HeadHunterAPI()

    # Тест 1: Пустая строка
    with pytest.raises(ValueError) as exc_info:
        api.get_vacancies("")
    error_msg = str(exc_info.value)
    assert "не может" in error_msg and "пуст" in error_msg.lower()

    # Тест 2: Только пробелы
    with pytest.raises(ValueError) as exc_info:
        api.get_vacancies("   ")
    error_msg = str(exc_info.value)
    assert "пробелов" in error_msg

    # Тест 3: Неправильное количество страниц
    with pytest.raises(ValueError) as exc_info:
        api.get_vacancies("Python", max_pages=-1)
    error_msg = str(exc_info.value)
    assert "положительным" in error_msg


def test_search_with_city(mock_session: Mock) -> None:
    """Поиск вакансий в конкретном городе"""
    with patch('src.api.requests.Session') as mock_session_class:
        mock_session_class.return_value = mock_session

        with patch.object(HeadHunterAPI, '_find_city_id') as mock_find_city:
            mock_find_city.return_value = 1  # ID Москвы

            api = HeadHunterAPI()
            result = api.get_vacancies("Python", city="Москва")

            mock_find_city.assert_called_with("Москва")
            assert len(result) == 2  # Используем mock данные


def test_network_error_handling() -> None:
    """Проверяем, как код обрабатывает ошибки сети"""

    mock_session = Mock()
    mock_session.get.side_effect = Exception("Ошибка сети")

    with patch('src.api.requests.Session') as mock_session_class:
        mock_session_class.return_value = mock_session

        with patch('builtins.print'):
            api = HeadHunterAPI()

        result = api.get_vacancies("Python")
        assert result == []


def test_multiple_pages() -> None:
    """Тест получения нескольких страниц"""

    # Создаем данные для двух страниц
    mock_response_page1 = Mock()
    mock_response_page1.json.return_value = {
        "items": [{"name": f"Vacancy {i}"} for i in range(100)],
        "pages": 2,
        "page": 0,
        "found": 150
    }

    mock_response_page2 = Mock()
    mock_response_page2.json.return_value = {
        "items": [{"name": f"Vacancy {i + 100}"} for i in range(50)],
        "pages": 2,
        "page": 1,
        "found": 150
    }

    mock_response_connect = Mock()
    mock_response_connect.json.return_value = {
        "items": [{"id": "test"}],
        "pages": 1,
        "found": 1
    }

    mock_session = Mock()
    # 3 Запроса - (проверка) + 2 (страницы)
    mock_session.get.side_effect = [
        mock_response_connect,  # запрос #1: проверка соединения
        mock_response_page1,  # запрос #2: страница 1
        mock_response_page2  # запрос #3: страница 2
    ]

    with patch('src.api.requests.Session') as mock_session_class:
        mock_session_class.return_value = mock_session

        api = HeadHunterAPI()
        result = api.get_vacancies("Python", max_pages=2)

        assert mock_session.get.call_count == 3
        assert len(result) == 150


def test_api_parameters(mock_session: Mock) -> None:
    """Проверка правильности параметров запроса"""
    with patch('src.api.requests.Session') as mock_session_class:
        mock_session_class.return_value = mock_session

        api = HeadHunterAPI()

        with patch.object(HeadHunterAPI, '_find_city_id', return_value=1):
            result = api.get_vacancies(
                keyword="Python разработчик",
                max_pages=3,
                city="Москва"
            )

            # Проверяем что метод вызван
            assert mock_session.get.called

            # Проверяем что вернулись mock данные
            assert len(result) == 2
            assert result[0]["name"] == "Python Developer"


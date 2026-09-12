from typing import List

import pytest

from src.utils import (
    filter_vacancies,
    filter_vacancies_by_profession,
    format_salary,
    get_top_vacancies,
    get_vacancies_by_salary,
    print_vacancies,
    sort_vacancies_by_salary,
)
from src.vacancy import Vacancy


def test_filter_by_profession_single_keyword(
    all_vacancies: List[Vacancy],
    python_developer: Vacancy,
    python_intern: Vacancy,
) -> None:
    """
    Тест: фильтрация по одной профессии в названии

    Проверяет, что функция находит вакансии, содержащие
    ключевое слово в названии
    """
    # Действие: ищем вакансии с "Python" в названии
    result = filter_vacancies_by_profession(all_vacancies, ["Python"])

    # Проверка: должны найти 2 вакансии (Python Developer и Стажер Python)
    assert len(result) == 2
    assert python_developer in result
    assert python_intern in result


def test_filter_by_profession_multiple_keywords(
    all_vacancies: List[Vacancy],
    python_developer: Vacancy,
    java_developer: Vacancy,
    python_intern: Vacancy,
) -> None:
    """
    Тест: фильтрация по нескольким профессиям (Python ИЛИ Java)

    Проверяет, что функция находит вакансии, содержащие
    любое из ключевых слов в названии.
    """
    # Действие: ищем вакансии с "Python" или "Java" в названии
    result = filter_vacancies_by_profession(all_vacancies, ["Python", "Java"])

    # Проверка: должны найти 3 вакансии
    assert len(result) == 3
    assert python_developer in result
    assert java_developer in result
    assert python_intern in result


def test_filter_by_profession_case_insensitive(
    all_vacancies: List[Vacancy],
) -> None:
    """
    Тест: фильтрация не зависит от регистра

    Проверяет, что поиск работает одинаково
    для "python", "PYTHON", "Python".
    """
    # Действие: ищем с разным регистром
    result_lower = filter_vacancies_by_profession(all_vacancies, ["python"])
    result_upper = filter_vacancies_by_profession(all_vacancies, ["PYTHON"])

    # Проверка: оба варианта должны найти одинаковое количество вакансий
    assert len(result_lower) == 2
    assert len(result_upper) == 2


def test_filter_by_profession_empty_keywords(
    all_vacancies: List[Vacancy],
) -> None:
    """
    Тест: фильтрация без ключевых слов

    Проверяет, что если не указаны ключевые слова,
    функция возвращает все вакансии.
    """
    # Действие: передаем пустой список ключевых слов
    result = filter_vacancies_by_profession(all_vacancies, [])

    # Проверка: должны вернуть все 4 вакансии
    assert len(result) == 4


def test_filter_by_description_single_keyword(
    all_vacancies: List[Vacancy],
    python_developer: Vacancy,
) -> None:
    """
    Тест: фильтрация по ключевому слову в описании

    Проверяет поиск по требованиям и обязанностям вакансии.
    """
    # Действие: ищем "Python" в описании
    result = filter_vacancies(all_vacancies, ["Python"])

    # Проверка: должен найти только Python Developer
    assert len(result) == 1
    assert result[0] == python_developer


def test_filter_by_description_multiple_keywords(
    all_vacancies: List[Vacancy],
    python_developer: Vacancy,
    java_developer: Vacancy,
) -> None:
    """
    Тест: фильтрация по нескольким ключевым словам в описании

    Проверяет поиск по ИЛИ (Python ИЛИ Java в описании).
    """
    # Действие: ищем "Python" или "Java" в описании
    result = filter_vacancies(all_vacancies, ["Python", "Java"])

    # Проверка: должен найти Python Developer и Java Developer
    assert len(result) == 2
    assert python_developer in result
    assert java_developer in result


def test_filter_by_description_empty_keywords(
    all_vacancies: List[Vacancy],
) -> None:
    """
    Тест: фильтрация без ключевых слов

    Проверяет, что пустой список ключевых слов
    возвращает все вакансии.
    """
    # Действие: передаем пустой список
    result = filter_vacancies(all_vacancies, [])

    # Проверка: должны вернуть все вакансии
    assert len(result) == 4


def test_filter_by_salary_from(
    all_vacancies: List[Vacancy],
    python_intern: Vacancy,
) -> None:
    """
    Тест: фильтрация "зарплата ОТ указанной суммы"

    Проверяет, что функция правильно фильтрует вакансии
    с зарплатой выше указанного порога.
    """
    # Действие: ищем вакансии с зарплатой от 110000
    result = get_vacancies_by_salary(all_vacancies, "от 110000")

    # Проверка: должны найти 3 вакансии (все кроме стажера)
    # Python Developer: средняя 125000 ✓
    # Java Developer: средняя 150000 ✓
    # Frontend Developer: средняя 110000 ✓
    # Стажер: нет зарплаты ✗
    assert len(result) == 3
    assert python_intern not in result


def test_filter_by_salary_to(
    all_vacancies: List[Vacancy],
    python_intern: Vacancy,
) -> None:
    """
    Тест: фильтрация "зарплата ДО указанной суммы"

    Проверяет, что функция правильно фильтрует вакансии
    с зарплатой ниже указанного порога.
    """
    # Действие: ищем вакансии с зарплатой до 140000
    result = get_vacancies_by_salary(all_vacancies, "до 140000")

    assert len(result) == 3  # ✓ Python + Java + Frontend


def test_filter_by_salary_empty(all_vacancies: List[Vacancy]) -> None:
    """
    Тест: фильтрация по зарплате без условия

    Проверяет, что пустая строка зарплаты
    возвращает все вакансии.
    """
    # Действие: передаем пустую строку
    result = get_vacancies_by_salary(all_vacancies, "")

    # Проверка: должны вернуть все вакансии
    assert len(result) == 4


def test_sort_vacancies_by_salary(
    all_vacancies: List[Vacancy],
    java_developer: Vacancy,
    python_developer: Vacancy,
    frontend_developer: Vacancy,
    python_intern: Vacancy,
) -> None:
    """
    Тест: сортировка вакансий по зарплате (от высокой к низкой)

    Проверяет правильный порядок сортировки.
    Вакансии без зарплаты идут последними.
    """
    # Действие: сортируем вакансии
    sorted_list = sort_vacancies_by_salary(all_vacancies)

    # Проверка порядка
    assert len(sorted_list) == 4
    assert sorted_list[0] == java_developer  # 180000 (самая высокая)
    assert sorted_list[1] == python_developer  # 150000
    assert sorted_list[2] == frontend_developer  # 130000
    assert sorted_list[3] == python_intern  # без зарплаты (последний)


def test_get_top_vacancies(
    all_vacancies: List[Vacancy],
    java_developer: Vacancy,
    python_developer: Vacancy,
) -> None:
    """
    Тест: получение топ-N вакансий

    Проверяет, что функция возвращает указанное количество
    самых высокооплачиваемых вакансий.
    """
    # Действие: запрашиваем 2 самые высокооплачиваемые вакансии
    top_2 = get_top_vacancies(all_vacancies, 2)

    # Проверка
    assert len(top_2) == 2
    assert top_2[0] == java_developer  # Первая по зарплате
    assert top_2[1] == python_developer  # Вторая по зарплате


def test_get_top_vacancies_more_than_exists(
    all_vacancies: List[Vacancy],
) -> None:
    """
    Тест: запрос большего количества, чем есть

    Проверяет, что если запросить больше вакансий чем есть,
    функция вернет все доступные.
    """
    # Действие: запрашиваем 10 вакансий (есть только 4)
    top_10 = get_top_vacancies(all_vacancies, 10)

    # Проверка: должны вернуть все 4 вакансии
    assert len(top_10) == 4


def test_get_top_zero_vacancies(all_vacancies: List[Vacancy]) -> None:
    """
    Тест: запрос 0 вакансий

    Проверяет, что функция возвращает пустой список
    при запросе 0 вакансий.
    """
    # Действие: запрашиваем 0 вакансий
    top_0 = get_top_vacancies(all_vacancies, 0)

    # Проверка: должен быть пустой список
    assert len(top_0) == 0
    assert top_0 == []


def test_format_salary() -> None:
    """
    Тест: форматирование зарплаты для отображения

    Проверяет, что числа форматируются с пробелами
    и обрабатываются None-значения.
    """
    # Проверка форматирования чисел
    assert format_salary(100000) == "100 000 руб."
    assert format_salary(150000) == "150 000 руб."

    # Проверка обработки None
    assert format_salary(None) == "Не указана"


def test_print_vacancies_empty(capsys: pytest.CaptureFixture) -> None:
    """
    Тест: вывод пустого списка вакансий

    Проверяет, что функция корректно обрабатывает
    пустой список и выводит сообщение.

    Args:
        capsys: Фикстура pytest для захвата вывода в консоль
    """
    # Действие: печатаем пустой список
    print_vacancies([])

    # Захватываем вывод
    captured = capsys.readouterr()

    # Проверка: должно быть сообщение "Вакансии не найдены"
    assert "Вакансии не найдены" in captured.out


def test_print_vacancies_with_data(
    python_developer: Vacancy,
    capsys: pytest.CaptureFixture,
) -> None:
    """
    Тест: вывод непустого списка вакансий

    Проверяет, что функция выводит информацию о вакансии.

    Args:
        python_developer: Фикстура вакансии Python разработчика
        capsys: Фикстура pytest для захвата вывода в консоль
    """
    # Действие: печатаем список с одной вакансией
    print_vacancies([python_developer])

    # Захватываем вывод
    captured = capsys.readouterr()
    output = captured.out

    # Проверка: в выводе должна быть информация о вакансии
    assert "Python Developer" in output
    assert "Москва" in output
    assert "100 000" in output  # Форматированная зарплата


def test_simple_example() -> None:
    """
    Простой тест-пример для понимания работы функций

    Этот тест показывает базовую логику работы
    всех тестируемых функций на простом примере.
    """
    # Создаем простую тестовую вакансию
    simple_vacancy = Vacancy(
        name="Тестовая вакансия Python",
        area="Москва",
        salary_from=50000,
        salary_to=None,
        requirement="Требуется знание Python",
        responsibility="Разработка на Python",
        schedule="Полный день",
        url="https://test.com",
    )

    # 1. Тест фильтрации по профессии (названию)
    by_profession = filter_vacancies_by_profession([simple_vacancy], ["Python"])
    assert len(by_profession) == 1
    assert by_profession[0].name == "Тестовая вакансия Python"

    # 2. Тест фильтрации по описанию
    by_description = filter_vacancies([simple_vacancy], ["Python"])
    assert len(by_description) == 1
    assert "Python" in by_description[0].requirement

    # 3. Тест форматирования зарплаты
    formatted_salary = format_salary(50000)
    assert formatted_salary == "50 000 руб."

    # 4. Тест фильтрации по зарплате
    by_salary = get_vacancies_by_salary([simple_vacancy], "от 40000")
    assert len(by_salary) == 1

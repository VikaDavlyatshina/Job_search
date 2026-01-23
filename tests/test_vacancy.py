from typing import Any, Callable, Dict, Tuple
import pytest
from src.vacancy import Vacancy


def test_developer_salary(developer_vacancy: Vacancy) -> None:
    """Тест вакансии разработчика"""
    vacancy = developer_vacancy
    assert vacancy.name == "Python Developer"
    assert vacancy.get_estimated_salary() == 125000  # (100k + 150k) / 2


def test_custom_vacancy(make_vacancy: Callable[..., Vacancy]) -> None:
    """Тест создания своей вакансии"""
    my_vacancy = make_vacancy(name="Data Scientist", salary_from=150000, salary_to=250000, area="Санкт-Петербург")

    assert my_vacancy.name == "Data Scientist"
    assert my_vacancy.area == "Санкт-Петербург"


def test_junior_vs_senior(junior_and_senior: Tuple[Vacancy, Vacancy]) -> None:
    """Тест сравнения зарплат"""
    junior, senior = junior_and_senior

    assert junior < senior  # 60k < 250k
    assert senior > junior


@pytest.mark.parametrize(
    "salary_from, salary_to, expected",
    [
        (100000, 150000, 125000),
        (120000, None, 120000),
        (None, 180000, 180000),
    ],
)
def test_salary_calculation(
    make_vacancy: Callable[..., Vacancy], salary_from: int | None, salary_to: int | None, expected: int
) -> None:
    """Параметризованный тест зарплаты"""
    vacancy = make_vacancy(name="Тест", salary_from=salary_from, salary_to=salary_to)

    assert vacancy.get_estimated_salary() == expected


def test_from_api(api_vacancy_with_salary: Dict[str, Any], api_vacancy_no_salary: Dict[str, Any]) -> None:
    """Тест преобразования данных API"""
    # Тест с зарплатой
    vacancy1 = Vacancy.from_vacancy_hh(api_vacancy_with_salary)
    assert vacancy1.name == "Python Developer"
    assert vacancy1.salary_from == 100000

    # Тест без зарплаты
    vacancy2 = Vacancy.from_vacancy_hh(api_vacancy_no_salary)
    assert vacancy2.name == "Стажер Python"
    assert vacancy2.salary_from is None

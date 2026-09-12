import re
from typing import List

from src.vacancy import Vacancy


def filter_vacancies_by_profession(vacancies: List[Vacancy], profession_keywords: List[str]) -> List[Vacancy]:
    """
    Фильтрует вакансии по ключевым словам в Названии вакансии

    Используется для поиска конкретной профессии

    Args:
        vacancies: Список вакансий
        profession_keywords: Ключевые слова для поиска в названии

    Returns:
        Отфильтрованный список
    """
    if not profession_keywords:
        return vacancies

    filtered = []

    for vacancy in vacancies:
        vacancy_name = vacancy.name.lower()

        for keyword in profession_keywords:
            keyword_lower = keyword.lower().strip()

            if not keyword_lower:
                continue

            # Ищем точное слово в названии
            if keyword_lower in vacancy_name:
                filtered.append(vacancy)
                break

    return filtered


def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """
    Фильтрует вакансии по ключевым словам (ищет отдельные слова)
    """
    if not filter_words:
        return vacancies

    filtered = []

    for vacancy in vacancies:
        description = f"{vacancy.requirement or ''} {vacancy.responsibility or ''}".lower()

        # Извлекаем только слова (без знаков препинания)
        words = re.findall(r"\b\w+\b", description)
        word_set = set(words)

        for keyword in filter_words:
            keyword_lower = keyword.lower().strip()

            if not keyword_lower:
                continue

            # Ищем слово целиком
            if keyword_lower in word_set:
                filtered.append(vacancy)
                break

    return filtered


def get_vacancies_by_salary(vacancies: List[Vacancy], salary_range: str) -> List[Vacancy]:
    """
    Фильтрует вакансии по зарплате.
    Поддерживает форматы:
    - '100000' (минимум)
    - '100000-150000' (диапазон)
    - 'от 100000' (минимум)
    - 'до 150000' (максимум)
    """
    if not salary_range or not vacancies:
        return vacancies

    # Очищаем ввод
    salary_range = salary_range.lower().strip().replace(" ", "")

    if not salary_range:
        return vacancies

    try:
        # 1. Просто число: '100000'
        if salary_range.isdigit():
            min_salary = int(salary_range)
            return [
                v
                for v in vacancies
                if (v.salary_from is not None and v.salary_from >= min_salary)
                or (v.salary_to is not None and v.salary_to >= min_salary)
            ]

        # 2. Диапазон: '100000-150000'
        elif "-" in salary_range:
            parts = salary_range.split("-")
            if len(parts) != 2:
                return vacancies

            min_salary = int(parts[0])
            max_salary = int(parts[1])

            if min_salary > max_salary:
                min_salary, max_salary = max_salary, min_salary

            filtered = []
            for v in vacancies:
                # Случай 1: есть обе границы
                if v.salary_from is not None and v.salary_to is not None:
                    # Проверяем пересечение диапазонов
                    if v.salary_from < max_salary and v.salary_to > min_salary:
                        filtered.append(v)
                # Случай 2: только "от"
                elif v.salary_from is not None:
                    if min_salary <= v.salary_from <= max_salary:
                        filtered.append(v)
                # Случай 3: только "до"
                elif v.salary_to is not None:
                    if min_salary <= v.salary_to <= max_salary:
                        filtered.append(v)

            return filtered

        # 3. 'от100000'
        elif salary_range.startswith("от"):
            try:
                min_salary = int(salary_range[2:])
            except ValueError:
                return vacancies

            return [
                v
                for v in vacancies
                if (v.salary_from is not None and v.salary_from >= min_salary)
                or (v.salary_to is not None and v.salary_to >= min_salary)
            ]

        # 4. 'до150000'
        elif salary_range.startswith("до"):
            try:
                max_salary = int(salary_range[2:])
            except ValueError:
                return vacancies

            return [
                v
                for v in vacancies
                if (v.salary_to is not None and v.salary_to <= max_salary)
                or (v.salary_from is not None and v.salary_from <= max_salary)
            ]

        else:
            return vacancies

    except (ValueError, AttributeError):
        return vacancies


def sort_vacancies_by_salary(vacancies: List[Vacancy]) -> List[Vacancy]:
    """
    Сортирует вакансии по зарплате от высокой к низкой.
    Простая и понятная реализация.
    """
    if not vacancies:
        return []

    # Функция для вычисления зарплаты для сортировки
    def calculate_sort_salary(v: Vacancy) -> float:
        # 1. Если есть обе границы - берем среднюю
        if v.salary_from is not None and v.salary_to is not None:
            return (v.salary_from + v.salary_to) / 2.0

        # 2. Если только "от" - берем её
        if v.salary_from is not None:
            return float(v.salary_from)

        # 3. Если только "до" - берем её
        if v.salary_to is not None:
            return float(v.salary_to)

        # 4. Если нет зарплаты - ставим в самый конец
        return float("-inf")

    # Сортируем по убыванию зарплаты
    return sorted(vacancies, key=calculate_sort_salary, reverse=True)


def get_top_vacancies(vacancies: List[Vacancy], top_n: int) -> List[Vacancy]:
    """
    Получение топ-N вакансий
    :param vacancies: Список вакансий
    :param top_n: Количество вакансий для возврата
    :return: Список top_n вакансий
    """

    # Валидация входных данных
    if top_n <= 0:
        # print(f" Запрошено некорректное количество: {top_n}")
        return []

    if not vacancies:
        # print("Список вакансий пуст")
        return []

    # 1. Сортируем вакансии по убыванию зарплаты
    sorted_list = sort_vacancies_by_salary(vacancies)

    # 2. Определяем, сколько вакансий взять.
    # Берём минимум из: запрошенного количества и фактического количества
    n_to_take = min(top_n, len(sorted_list))

    if n_to_take < top_n:
        # print(f"ℹ️  Запрошено {top_n}, но найдено только {len(sorted_vacancies)}")
        pass

    # 3. Возвращаем первые n_to_take вакансий
    return sorted_list[:n_to_take]


def print_vacancies(vacancies: List[Vacancy]) -> None:
    """
    Выводит вакансии в читаемом формате.

    :param vacancies: Список вакансий для вывода
    """
    # 1. Проверяем, есть ли вакансии
    if not vacancies:
        print("📭 Вакансии не найдены.")
        return

    # 2. Выводим заголовок с количеством
    print(f"\n{'=' * 60}")
    print(f"📍 НАЙДЕНО ВАКАНСИЙ: {len(vacancies)}")
    print("=" * 60)

    # 3. Выводим каждую вакансию
    for i, vacancy in enumerate(vacancies, start=1):
        print(f"\n{'─' * 40}")
        print(f"🎯 ВАКАНСИЯ #{i}")
        print(f"{'─' * 40}")

        # Основная информация (используем __str__ метод)
        print(str(vacancy))

        # Дополнительная информация (только если не "Не указано")
        if vacancy.requirement and vacancy.requirement != "Не указано":
            print(f"📋 Требования: {vacancy.requirement}")

        if vacancy.responsibility and vacancy.responsibility != "Не указано":
            print(f"✅ Обязанности: {vacancy.responsibility}")

        if vacancy.schedule and vacancy.schedule != "Не указано":
            print(f"📅 График работы: {vacancy.schedule}")

        # Ссылка (всегда показываем)
        print(f"🔗 Ссылка: {vacancy.url}")

    # 4. Закрывающий разделитель
    print(f"\n{'=' * 60}")
    print("✅ Вывод вакансий завершен!")
    print("=" * 60)


def format_salary(salary: int | None) -> str:
    """
    Форматирует зарплату для красивого вывода.
    Пример: 100000 -> "100 000 руб."
    """
    if salary is None:
        return "Не указана"

    return f"{salary:,} руб.".replace(",", " ")

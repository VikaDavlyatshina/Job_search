from typing import List
from src.vacancy import Vacancy
from src.storage import JSONSaver

def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """
    Фильтрует вакансии по ключевым словам

    :param vacancies:
           Список вакансий для фильтрации
    :param filter_words:
        Список ключевых слов для поиска в описании вакансии
    :return:
          Отфильтрованный список
    """

    # Если нет ключевых слов - возвращаем все вакансии
    if not filter_words:
        return vacancies

    # Пустой список для хранения
    filtered = []

    for vacancy in vacancies:

        description = (vacancy.requirement or "").lower()

        # Проверяем каждое ключевое слово
        for keyword in filter_words:
            keyword_lower = keyword.lower().strip()

            if not keyword_lower:
                continue

            # Если ключевое слово найдено в описании
            if keyword_lower in description:
                filtered.append(vacancy)
                break  # Достаточно одного совпадения

    return filtered

def get_vacancies_by_salary(vacancies: List[Vacancy], salary_range: str) -> List[Vacancy]:
    """
    Фильтрует вакансии по зарплате.
    """

    if not salary_range or not salary_range.strip():
        return vacancies

    salary_range = salary_range.strip().lower()

    # Вспомогательная функция для извлечения чисел
    def extract_number(text: str) -> int:
        """Извлекает число из строки, удаляя все не-цифры"""
        digits = ''.join(filter(lambda x: x.isdigit(), text))
        return int(digits) if digits else 0

    try:
        # 1. "от 100000" - макс. зарплата >= 100000
        if salary_range.startswith("от"):
            min_salary = extract_number(salary_range)
            if min_salary == 0:  # Не удалось извлечь число
                return vacancies

            result = []
            for vacancy in vacancies:
                # Пропускаем вакансии без зарплаты ВООБЩЕ
                if vacancy.salary_from is None and vacancy.salary_to is None:
                    continue

                # Если есть максимальная зарплата И она >= нашему минимуму
                # ИЛИ максимальная зарплата не указана (значит может быть любой)
                if vacancy.salary_to is None or vacancy.salary_to >= min_salary:
                    result.append(vacancy)
            return result

        # 2. "до 150000" - мин. зарплата <= 150000
        elif salary_range.startswith("до"):
            max_salary = extract_number(salary_range)
            if max_salary == 0:  # Не удалось извлечь число
                return vacancies

            result = []
            for vacancy in vacancies:
                # Пропускаем вакансии без зарплаты ВООБЩЕ
                if vacancy.salary_from is None and vacancy.salary_to is None:
                    continue

                # Если есть минимальная зарплата И она <= нашему максимуму
                # ИЛИ минимальная зарплата не указана (значит может быть 0)
                if vacancy.salary_from is None or vacancy.salary_from <= max_salary:
                    result.append(vacancy)
            return result

        # 3. "80000-150000" - пересечение диапазонов
        elif '-' in salary_range:
            # Удаляем пробелы и разбиваем
            parts = salary_range.replace(' ', '').split('-')
            if len(parts) != 2:
                return vacancies

            try:
                min_s = int(parts[0])
                max_s = int(parts[1])
            except ValueError:
                return vacancies

            result = []
            for vacancy in vacancies:
                # Пропускаем вакансии без зарплаты
                if vacancy.salary_from is None and vacancy.salary_to is None:
                    continue

                # Получаем границы вакансии
                vac_from = vacancy.salary_from if vacancy.salary_from is not None else 0
                vac_to = vacancy.salary_to if vacancy.salary_to is not None else 10_000_000_000  # 10 млрд

                # Проверяем пересечение диапазонов
                if vac_from <= max_s and vac_to >= min_s:
                    result.append(vacancy)
            return result

        # 4. "120000" - попадание в диапазон
        else:
            target_salary = extract_number(salary_range)
            if target_salary == 0:
                return vacancies

            result = []
            for vacancy in vacancies:
                if vacancy.salary_from is None and vacancy.salary_to is None:
                    continue

                # Получаем границы
                vac_from = vacancy.salary_from if vacancy.salary_from is not None else 0
                vac_to = vacancy.salary_to if vacancy.salary_to is not None else 10_000_000_000

                # Проверяем, попадает ли target_salary в диапазон
                if vac_from <= target_salary <= vac_to:
                    result.append(vacancy)
            return result

    except Exception as e:
        # Любая ошибка - возвращаем все вакансии
        return vacancies


def sort_vacancies_by_salary(vacancies: List[Vacancy]) -> List[Vacancy]:
    """
    Сортирует вакансии по убыванию зарплаты.
    Сначала идут вакансии с самой высокой МАКСИМАЛЬНОЙ зарплатой.
    """
    if not vacancies:
        return []

    # Создаём функцию для вычисления зарплаты для сортировки
    def get_salary_for_sort(vacancy: Vacancy) -> int:
        # Берём МАКСИМАЛЬНУЮ зарплату (salary_to)
        if vacancy.salary_to is not None:
            return vacancy.salary_to
        # Если нет "до", берём "от"
        elif vacancy.salary_from is not None:
            return vacancy.salary_from
        # Если зарплаты нет совсем
        else:
            return 0

    # Сортируем по убыванию зарплаты
    sorted_list = sorted(
        vacancies,
        key=get_salary_for_sort,
        reverse=True  # По убыванию (от большего к меньшему)
    )

    return sorted_list


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
    print('=' * 60)

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
    print('=' * 60)


def format_salary(salary: int) -> str:
    """
    Форматирует зарплату для красивого вывода.
    Пример: 100000 -> "100 000 руб."
    """
    if salary is None:
        return "Не указана"

    return f"{salary:,} руб.".replace(",", " ")


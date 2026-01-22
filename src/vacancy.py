from typing import Dict, Any, List



class Vacancy:
    """Класс для представления Вакансии"""

     # Список разрешенных атрибутов (для экономии памяти)
    __slots__ = ("name", "area", "salary_from", "salary_to", "requirement", "responsibility", "schedule", "url")

    # Инициализация
    def __init__(
            self,
            name: str,
            area: str| None,
            salary_from: int | None,
            salary_to: int | None,
            requirement: str | None,
            responsibility: str| None,
            schedule: str| None,
            url: str
    ):
        self.name = self.__validate_name(name)                 # Название вакансии
        self.area = area or "Не указано"                      # Город

        # Используем валидацию для зарплаты
        self.salary_from = self.__validate_salary(salary_from)   # Зарплата от
        self.salary_to = self.__validate_salary(salary_to)       # Зарплата до

        self.requirement = requirement or "Не указано"          # Требования
        self.responsibility = responsibility or "Не указано"    # Обязанности
        self.schedule = schedule or "Не указано"                # График работы
        self.url = self.__validate_url(url)                     # Ссылка на вакансию

    # Валидация данных

    @staticmethod
    def __validate_name(name: str) -> str:
        """
        Валидации названия вакансии.

        :param name:  Название вакансии
        :return:
               Возвращает корректные названия вакансии.
        :raises:
              ValueError: Если название пустое
        """

        if not name:
            raise ValueError("У вакансии нет названия!")
        return name

    @staticmethod
    def __validate_salary(salary: int|float|None) -> int|None:
        """
        Валидация зарплаты.

        :param salary: Значение зарплаты (может быть None)
        :return: Валидное значение или None
        """

        # 1. Если None -> None
        if salary is None:
            return None

        # 2. Проверяем тип данных. Если не число -> None
        if not isinstance(salary, (int, float)):
            return None

        # 3. Пробуем преобразовать к int
        try:
            salary_int = int(salary)
        except (ValueError, OverflowError):
            return None

        # 4. Проверяем диапазон
        if salary_int < 0:   # Отрицательная зарплата
            return None

        return salary_int

    @staticmethod
    def __validate_url(url: str|None) -> str:
        """
        Валидация ссылки на вакансию.
        :param url:
                Ссылка вакансии - строка или не указано
        :return:
               Возвращает корректную ссылки вакансий
        :raises:
               ValueError: Если ссылка отсутствует или некорректна
        """

        if not url or not isinstance(url, str):
            raise ValueError("Нет ссылки на вакансию!")
        if not url.startswith("https://"):
            raise ValueError(f"Некорректная ссылка: {url}")
        return url


    def get_estimated_salary(self) -> int| None:
        """
        Возращает предполагаемую зарплату
        1. Если обе границы None → None
        2. Если только from → from
        3. Если только to → to
        4. Если обе → среднее арифметическое
        """

        if  self.salary_from is None and self.salary_to is None:
            return None

        elif self.salary_from is None:
            return self.salary_to

        elif self.salary_to is None:
           return self.salary_from

        else:
           return (self.salary_from + self.salary_to) // 2


    # Методы сравнения
    def __lt__(self, other: "Vacancy") -> bool:
        """
        Сравнение вакансий (меньше чем) по предполагаемой зарплате.
        Если зарплата не указана -> считаем как 0

        :param:
            other: Другая вакансия для сравнения

        :return:
            bool: True если текущая вакансия имеет меньшую зарплату
        """

        if not isinstance(other, Vacancy):
            return NotImplemented

        # Если зарплата не указана - считаем как 0
        self_salary = self.get_estimated_salary() or 0
        other_salary = other.get_estimated_salary() or 0

        return self_salary < other_salary



    def __gt__(self, other: "Vacancy") -> bool:
        """
        Сравнение вакансий (больше чем) по предполагаемой зарплате.

        :param:
            other: Другая вакансия для сравнения

        :return:
            bool: True если текущая вакансия имеет большую зарплату
        """

        if not isinstance(other, Vacancy):
            return NotImplemented

        # Если зарплата не указана - считаем как 0
        self_salary = self.get_estimated_salary() or 0
        other_salary = other.get_estimated_salary() or 0

        return self_salary > other_salary


    def __eq__(self, other: "Vacancy") -> bool:
        """
        Проверка равенства вакансий по предполагаемой зарплате.

        :param:
            other: Другая вакансия для сравнения

        :return:
            bool: True если зарплаты равны
        """
        if not isinstance(other, Vacancy):
            return NotImplemented


        self_salary = self.get_estimated_salary()
        other_salary = other.get_estimated_salary()

        if self_salary is None and other_salary is None:
            return True  # Обе без зарплаты
        if self_salary is None or other_salary is None:
            return False  # Одна с зарплатой, другая без

        return self_salary == other_salary

    def __str__(self) -> str:
        """Для строкового представления вакансий"""

        # Определяем формат зарплаты
        if self.salary_from is None and self.salary_to is None:
            salary_info = "Не указана"

        elif self.salary_from == self.salary_to and self.salary_from is not None:
            # Если зарплата "от" и "до" одинаковые, показываем как фиксированную
            salary_info = f"{self.salary_from:,} руб.".replace(",", " ")

        elif self.salary_from is not None and self.salary_to is not None:
            salary_info = f"{self.salary_from:,} - {self.salary_to:,} руб.".replace(",", " ")

        elif self.salary_from is not None:
            salary_info = f"от {self.salary_from:,} руб.".replace(",", " ")

        else:  # только salary_to указано
            salary_info = f"до {self.salary_to:,} руб.".replace(",", " ")

        return f"Вакансия: {self.name}\nГород: {self.area}\nЗарплата: {salary_info}"


    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект Vacancy в словарь для сохранения в JSON

        :return: Словарь с данными вакансии
        """

        return {
             "name": self.name,
             "area": self.area,
             "salary_from": self.salary_from if self.salary_from is not None else "Не указано",
             "salary_to": self.salary_to if self.salary_to is not None else "Не указано",
             "requirement": self.requirement,
             "responsibility": self.responsibility,
             "schedule": self.schedule,
             "url": self.url
         }


    @classmethod
    def from_vacancy_hh(cls, hh_data: dict) -> "Vacancy":
        """
        Создает экземпляр класса Vacancy из данных ответа API
        :param hh_data: Словарь с данными вакансий от hh.ru
        :return: Возвращает объект класса Vacancy
        """

        # Безопасное получение данных о зарплате
        salary_data = hh_data.get("salary")
        if salary_data:
            salary_from = salary_data.get("from")
            salary_to = salary_data.get("to")
        else:
            salary_from = salary_to = None

        # Создаем один объект класса Vacancy
        return cls(
            name=hh_data.get("name"),
            area=hh_data.get("area", {}).get("name"),
            salary_from = salary_from,  # Может быть None
            salary_to = salary_to,      # Может быть None
            requirement=hh_data.get("snippet", {}).get("requirement"),
            responsibility=hh_data.get("snippet", {}).get("responsibility"),
            schedule=hh_data.get("schedule", {}).get("name"),
            url=hh_data.get("alternate_url"),
        )

    @classmethod
    def cast_to_object_list(cls, hh_data_list: List[Dict]) -> List[Vacancy]:
        """
        Создаем список объектов Vacancy из списка словарей
        :param hh_data_list: Список словарей с данными вакансий от hh.ru
        :return: Возвращает список объектов класса Vacancy
        """

        # Создаём список объектов
        vacancies = []

        # Проходим циклом по всем вакансия
        for item in hh_data_list:
            try:
                # Создаём объект вакансии
                vacancy = cls.from_vacancy_hh(item)
                # Добавляем созданную вакансию к списку вакансий
                vacancies.append(vacancy)

            # Если вакансия битая - пропускаем
            except ValueError as e:
                print(f"Пропущена вакансия: {e}")
                continue

        return vacancies


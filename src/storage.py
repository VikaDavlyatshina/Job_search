import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.vacancy import Vacancy
from pathlib import Path



class BaseStorage(ABC):
    """Абстрактный класс для хранения вакансий"""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавляет вакансию в хранилище"""
        pass

    @abstractmethod
    def get_vacancies(self, **criteria) -> List[Vacancy]:
        """Получает вакансию из хранилища"""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаляет вакансию из хранилища"""
        pass

class JSONSaver(BaseStorage):
    """Класс для сохранения вакансий в JSON-файл"""

    def __init__(self, filename: str = "vacancies.json"):
        """
        Инициализирует сохранение в указанный файл
        :param filename: Имя JSON-файла для сохранения
        """

        self.__filename = filename
        self.__path = Path(self.__filename)

        # Создаём файл, если не существует
        if not self.__path.exists():
            self.__path.write_text("[]", encoding="utf-8")
            print(f"Создан новый файл: {filename}")


    def _load_data(self)-> List[Dict[str, Any]]:
        """Загружает данные из JSON-файла"""

        try:
            with open(self.__path, "r", encoding="utf-8") as file:
                return json.load(file)

        # Если файл не найден или некорректный Json -> возвращаем пустой список
        except (FileNotFoundError, json.JSONDecodeError):
            return []



    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в JSON-файл."""

        with open(self.__path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


    def clear_all(self) -> None:
        """Полностью очищает файл с вакансиями."""
        self._save_data([])


    def _dict_to_vacancy(self, item: Dict[str, Any]) -> Vacancy:
        """Преобразует словарь в объект Vacancy"""

        return Vacancy(
            name=item.get("name", ""),
            area=item.get("area"),
            salary_from=item.get("salary_from"),
            salary_to=item.get("salary_to"),
            requirement=item.get("requirement"),
            responsibility=item.get("responsibility"),
            schedule=item.get("schedule"),
            url=item.get("url", ""),
        )

    def add_vacancy(self, vacancy: Vacancy) -> bool:
        """
        Добавляет вакансию в файл.
        :param vacancy:
               Объект вакансии для сохранения
        :return:
               True - если вакансия добавлена
               False - если вакансия уже существует
        """

        data = self._load_data()

        # Проверяем дубликаты по URL (уникальный идентификатор)
        for item in data:
            if item.get('url') == vacancy.url:
                return False # Вакансия уже существует

        # Используем метод to_dict() из класса Vacancy
        vacancy_dict = vacancy.to_dict()
        data.append(vacancy_dict)

        self._save_data(data)
        return True  # Вакансия успешно добавлена

    def get_vacancies(self, **criteria) -> List[Vacancy]:
        """
         Получает вакансии по указанным критериям.
        :param criteria:
              **criteria: Критерии фильтрации
        :return:
              Список объектов Vacancy, удовлетворяющих критериям
        """

        data = self._load_data()

        # Если нет критериев - возвращаем все
        if not criteria:
            return [self._dict_to_vacancy(item) for item in data]


        # Фильтруем по критериям
        result = []
        for item in data:
            match = True
            for key, value in criteria.items():
                if key not in item or item.get(key) != value:
                    match = False
                    break

            if match:
                result.append(self._dict_to_vacancy(item))

        return result

    def delete_vacancy(self, vacancy: Vacancy) -> bool:
        """
        Удаляет вакансию из файла.
        :param vacancy:
                 Объект вакансии для удаления
        :return:
                True - если вакансия удалена
               False - если вакансия не найдена
        """
        data = self._load_data()
        initial_count = len(data)

        # Оставляем все вакансии, кроме удаляемой (определяем по URL)
        data = [item for item in data if item.get("url") != vacancy.url]

        if len(data) < initial_count:
            self._save_data(data)
            return True
        else:
            return False

    def get_vacancies_by_keyword(self, keyword: str) -> List[Vacancy]:
        """
        Ищет вакансии по ключевому слову в названии и описании.
        :param keyword:
                Ключевое слово для поиска
        :return:
                Список найденных вакансий
        """

        data = self._load_data()
        keyword_lower = keyword.lower()

        result = []
        for item in data:
            # Ищем в разных полях
            search_fields = ['name', 'area', 'requirement', 'responsibility',]
            for field in search_fields:
                field_value = item.get(field, '')
                if keyword_lower in field_value.lower():
                    result.append(self._dict_to_vacancy(item))
                    break

        return result

    def count_vacancies(self) -> int:
        """Возвращает количество сохраненных вакансий."""
        return len(self._load_data())

    def get_all_vacancies(self) -> List[Vacancy]:
        """Возвращает все сохраненные вакансии (удобный алиас)."""
        return self.get_vacancies()

    def is_vacancy_saved(self, url: str) -> bool:
        """Проверяет, сохранена ли вакансия с указанным URL."""
        data = self._load_data()
        return any(item.get('url') == url for item in data)

    def get_top_vacancies(self, n: int) -> List[Vacancy]:
        """
        Возвращает N вакансий
        :param n:
            Количество вакансий для возврата
        :return:
           Список из N-вакансий
        """

        all_vacancies = [self._dict_to_vacancy(item) for item in self._load_data()]
        return all_vacancies[:n]


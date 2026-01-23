import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from src.vacancy import Vacancy


class BaseStorage(ABC):
    """Абстрактный класс для хранения вакансий"""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавляет вакансию в хранилище"""
        pass

    @abstractmethod
    def get_vacancies(self, **criteria: Any) -> List[Vacancy]:
        """Получает вакансию из хранилища"""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаляет вакансию из хранилища"""
        pass


class JSONSaver(BaseStorage):
    """Класс для сохранения вакансий в JSON-файл"""

    def __init__(self, filename: str | None = None):
        """
        Инициализирует сохранение в указанный файл
        :param filename:
                    Имя JSON-файла для сохранения.
                    Если None, используется 'vacancies.json'
        """

        if filename is None:
            self.__filename = "vacancies.json"
        else:
            # Убедимся, что у файла расширение .json
            if not filename.endswith(".json"):
                self.__filename = f"{filename}.json"
            else:
                self.__filename = filename

        self.__path = Path(self.__filename)

        # Создаём файл, если не существует
        if not self.__path.exists():
            self.__path.write_text("[]", encoding="utf-8")
            print(f"Создан новый файл: {self.__filename}")

    @property
    def filename(self) -> str:
        """Возвращает имя файла"""
        return Path(self.__filename).name

    def _load_data(self) -> List[Dict[str, Any]]:
        """Загружает данные из JSON-файла"""

        try:
            with open(self.__path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                # Проверяем, что все элементы - словари
                if all(isinstance(item, dict) for item in data):
                    return data  # Теперь mypy знает, что это List[Dict]
                else:
                    return []  # Если есть не-словари, возвращаем пустой список
            else:
                return []

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

        salary_from = item.get("salary_from")
        salary_to = item.get("salary_to")

        # Преобразуем "Не указано" -> None
        if salary_from == "Не указано":
            salary_from = None
        elif salary_from is not None:
            try:
                salary_from = int(salary_from)
            except (ValueError, TypeError):
                salary_from = None

        if salary_to == "Не указано":
            salary_to = None
        elif salary_to is not None:
            try:
                salary_to = int(salary_to)
            except (ValueError, TypeError):
                salary_to = None

        return Vacancy(
            name=item.get("name", ""),
            area=item.get("area"),
            salary_from=salary_from,
            salary_to=salary_to,
            requirement=item.get("requirement"),
            responsibility=item.get("responsibility"),
            schedule=item.get("schedule"),
            url=item.get("url", ""),
        )

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """
        Добавляет вакансию в файл.
        :param vacancy:
               Объект вакансии для сохранения
        """

        data = self._load_data()

        # Проверяем дубликаты по URL (уникальный идентификатор)
        for item in data:
            if item.get("url") == vacancy.url:
                print(f"Вакансия уже существует: {vacancy.url}")
                return

        # Используем метод to_dict() из класса Vacancy
        vacancy_dict = vacancy.to_dict()
        data.append(vacancy_dict)

        self._save_data(data)

    def get_vacancies(self, **criteria: Any) -> List[Vacancy]:
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
                item_value = item.get(key)

                if item_value is None:
                    match = False
                    break

                if isinstance(item_value, str) and isinstance(value, str):
                    # Для строк: нечёткое сравнение (игнорируем регистр)
                    if value.lower() not in item_value.lower():
                        match = False
                        break
                elif item_value != value:
                    # Для чисел и других типов: строгое сравнение
                    match = False
                    break

            if match:
                result.append(self._dict_to_vacancy(item))

        return result

    def delete_vacancy(self, vacancy: Vacancy) -> None:  # ← ИЗМЕНИЛИ: None вместо bool
        """
        Удаляет вакансию из файла.
        """
        data = self._load_data()

        initial_count = len(data)

        # Оставляем все вакансии, кроме удаляемой
        data = [item for item in data if item.get("url") != vacancy.url]

        if len(data) < initial_count:
            self._save_data(data)
            print(f"Вакансия удалена: {vacancy.url}")
        else:
            print(f"Вакансия не найдена: {vacancy.url}")

    def delete_vacancy_by_url(self, url: str) -> bool:
        """
        Удаляет вакансию по URL
        :param url: URL вакансии
        :return: True если удалено, False если не найдено
        """
        data = self._load_data()
        initial_count = len(data)

        # Оставляем все вакансии, кроме указанной
        data = [item for item in data if item.get("url") != url]

        if len(data) < initial_count:
            self._save_data(data)
            return True
        return False

    def is_vacancy_saved(self, url: str) -> bool:
        """Проверяет, сохранена ли вакансия с указанным URL."""
        data = self._load_data()
        return any(item.get("url") == url for item in data)

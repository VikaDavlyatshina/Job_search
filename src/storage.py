import json
from abc import ABC, abstractmethod
from typing import List
from src.vacancy import Vacancy
from pathlib import Path



class FileHandler(ABC):
    """Абстрактный класс для работы с файлами"""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавляет вакансию в файл"""
        pass

    @abstractmethod
    def get_vacancies(self) -> List[Vacancy]:
        """Получает вакансию из файла"""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаляет вакансию из файла"""
        pass

class JSONSaver(FileHandler):
    """Класс для сохранения вакансий в JSON-файл"""

    def __init__(self, filename: str = "vacancies.json"):
        self.__filename = filename
        self.__path = Path(self.__filename)

        if not self.__path.exists():
            self.__path.write_text("[]", encoding="utf-8")

    def _load_data(self)-> list:
        """Читает из файла"""
        with open(self.__path, "r", encoding="utf-8") as file:
            return json.load(file)


    def _save_data(self, data: list) -> None:
        """Сохранение в файл"""
        with open(self.__path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def add_vacancy(self, vacancy: Vacancy) -> None:
        data = self._load_data()

        vacancy_dict = {
            "name": vacancy.name,
            "area": vacancy.area,
            "salary_from": vacancy.salary_from,
            "salary_to": vacancy.salary_to,
            "requirement": vacancy.requirement,
            "responsibility": vacancy.responsibility,
            "schedule": vacancy.schedule,
            "url": vacancy.url,
        }

        if vacancy_dict not in data:
            data.append(vacancy_dict)

        self._save_data(data)

    def get_vacancies(self) -> List[Vacancy]:
        data = self._load_data()
        return [
            Vacancy(
                name=item["name"],
                area=item["area"],
                salary_from=item["salary_from"],
                salary_to=item["salary_to"],
                requirement=item["requirement"],
                responsibility=item["responsibility"],
                schedule=item["schedule"],
                url=item["url"],
            )
            for item in data
        ]

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        data = self._load_data()
        data = [item for item in data if item["url"] != vacancy.url]
        self._save_data(data)
from abc import ABC, abstractmethod
from typing import List, Dict

import requests


class Parser(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def _connect(self) -> None:
        """Устанавливает соединение с API"""
        pass


class HH(Parser):
    """Класс для подключения к API hh.ru"""

    def __init__(self) -> None:
        self.__base_url = "https://api.hh.ru/vacancies"
        self._headers = {"User-Agent": "HH-User-Agent"}

    def _connect(self) -> None:
        """Проверяет доступность API"""
        response = requests.get(self.__base_url, headers=self._headers)
        if response.status_code != 200:
            raise ConnectionError("API недоступно")

    def get_vacancies(self, keyword: str) -> List[Dict]:
        """Получает список вакансий по ключевому слову"""

        self._connect()
        params ={
            "area": 113,         # Код России
            "text": keyword,     # Ключевое слово
            "page": 0,           # Номер страницы
            "per_page": 100      #  Количество вакансий на странице

        }

        response = requests.get(
            self.__base_url,
            headers=self._headers,
            params=params
        )
        response.raise_for_status()

        return response.json()["items"]


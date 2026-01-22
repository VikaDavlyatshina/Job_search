from abc import ABC, abstractmethod
from typing import List, Dict
import time
import requests


class BaseVacancyApi(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def _connect(self) -> None:
        """Устанавливает соединение с API"""
        pass

    @abstractmethod
    def get_vacancies(self, keyword: str) -> List[Dict]:
        """Получает список вакансий из API"""
        pass


class HeadHunterAPI(BaseVacancyApi):
    """Класс для подключения к API hh.ru"""

    def __init__(self) -> None:
        self.__base_url = "https://api.hh.ru/vacancies"
        self.__session = None
        self._connect()

    def _connect(self) -> None:
        """
        Проверяет доступность API.
        Создает сессию только если API доступно.
        """

        # Если сессия уже есть - считаем что соединение установлено
        if self.__session is not None:
            return

        try:
            # Создаем сессию один раз
            self.__session = requests.Session()

            # Проверяем доступность API используя созданную сессию
            test_response = self.__session.get(
                self.__base_url,
                params={'text': 'test', 'per_page': 1, 'area': 113},
                timeout=10
            )
            test_response.raise_for_status()

            # Дополнительно проверяем формат ответа
            data = test_response.json()
            if 'items' not in data:
                raise ConnectionError("API вернуло неверный формат данных")

        except requests.RequestException as e:
            # Если ошибка - сбрасываем сессию
            self.__session = None
            raise ConnectionError(f"Не удалось подключиться к API hh.ru: {e}")





    def get_vacancies(self, keyword: str, max_pages: int = 5) -> List[Dict]:

        """
        Получает вакансию по ключевому слову с нескольких страниц

        :param keyword: Ключевое слово для поиска
        :param max_pages: Количество страниц для загрузки (по 100 вакансий на странице).
                          По умолчанию загружаем 5 страниц - 500 вакансий. Лимит страниц можно увеличить

        :return: Получаем список словарей с данными вакансий
        """

        # 1. Проверка входных данных
        if not keyword or not isinstance(keyword, str):
            raise ValueError("Ключевое слово должно быть непустой строкой")

        keyword = keyword.strip()
        if not keyword:
            raise ValueError("Ключевое слово не может состоять только из пробелов")

        if max_pages <= 0:
            raise ValueError("Количество страниц должно быть положительным числом")

        # 2. Проверяем соединение
        if self.__session is None:
            self._connect()

        all_vacancies = []     # Собираем вакансии со всех страниц

        # Загружаем данные постранично
        for page in range(max_pages):
            try:
                params = {
                    "text": keyword,
                    "area": 113,  # Россия
                    "page": page,  # Номер страницы (0-based)
                    "per_page": 100,  # Максимум на странице
                    "only_with_salary": False,  # Берем и без зарплаты
                }

                # Делаем запрос
                response = self.__session.get(
                    self.__base_url,
                    params=params,
                    timeout=15
                )
                response.raise_for_status()

                data = response.json()
                page_vacancies = data.get("items", [])
                all_vacancies.extend(page_vacancies)

                # Проверка на последнюю страницу

                # 1. По количеству вакансий на странице
                if len(page_vacancies) < 100:
                    break

                # 2. По общему количеству страниц в ответе
                pages_found = data.get("pages", 0)
                if page >= pages_found - 1:
                    break

                # Добавляем паузы между запросами
                if page < max_pages - 1:
                    time.sleep(0.1)

            except requests.RequestException as e:
                print(f"Ошибка при загрузке страницы {page + 1}: {e}")
                continue

        return all_vacancies





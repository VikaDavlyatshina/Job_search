from abc import ABC, abstractmethod
from typing import List, Dict

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

    def _connect(self) -> None:
        """
        Проверяем доступность API
        1) Пробуем создать сесию
        2) Пробуем сделать тестовый запрос
        3) Используем сесию
        """

        try:
            # Создаём сессию, если она не создана
            if self.__session is None:
                self.__session = requests.Session()

            # Пробуем сделать тестовый запрос
            test_params = {'text': 'test', 'per_page': 1}
            test_response = self.__session.get(
                self.__base_url,
                params=test_params,
                timeout=10
            )

            # Проверяем статус ответа
            test_response.raise_for_status()    # Если ответ не 200 - будет ошибка

        except requests.RequestException as e:
            # Если что-то пошло не так - сбрасываем сесию и выводим сообщение
            self.__session = None
            raise ConnectionError(f"API hh.ru недоступно: {e}")




    def get_vacancies(self, keyword: str, max_pages: int = 5) -> List[Dict]:

        """
        Получает вакансию по ключевому слову с нескольких страниц

        :param keyword: Ключевое слово для поиска
        :param max_pages: Количество страниц для загрузки (по 100 вакансий на странице).
                          По умолчанию загружаем 5 страниц - 500 вакансий. Лимит страниц можно увеличить

        :return: Получаем список словарей с данными вакансий
        """

        # Проверяем соединение
        if self.__session is None:
            self.__session = requests.Session()  # Если нет сесии - создаём

        all_vacancies = []     # Собираем вакансии со всех сраниц

        # Загружаем данные постранично
        for page in range(max_pages):
            # Параметры запроса для текущей страницы
            params = {
                "area": 113,  # Код России
                "text": keyword,  # Ключевое слово
                "page": page,  # Номер страницы
                "per_page": 100  # Количество вакансий на странице
            }

            # Делаем запрос для текущей страницы
            response = self.__session.get(self.__base_url, params=params)
            response.raise_for_status()  # Проверяем успешность

            # Проверяем вакансии текущей страницы
            page_vacancies = response.json()["items"]

            # Добавляем вакансии в общий список
            all_vacancies.extend(page_vacancies)

            # Проверяем, есть ли ещё страницы
            # Если на странице меньше 100 вакансий - значит это последняя страница
            if len(page_vacancies) < 100:
                break

        return all_vacancies





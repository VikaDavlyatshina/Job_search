import time  # Для добавления пауз между запросами
from abc import ABC, abstractmethod  # ABC - для создания абстрактных классов
from typing import Any, Dict, List, Optional, Union

import requests  # Библиотека для HTTP-запросов к API


class BaseVacancyApi(ABC):
    """
    АБСТРАКТНЫЙ КЛАСС - шаблон для работы с любым API вакансий

    Абстрактный класс = "контракт", который обязывает все дочерние классы
    реализовать указанные методы. Это нужно, чтобы:
    1. Гарантировать единый интерфейс для всех API (hh.ru, superjob и т.д.)
    2. Легко добавлять новые платформы
    3. Соблюдать принципы ООП (наследование, полиморфизм)
    """

    @abstractmethod
    def _connect(self) -> None:
        """
        Устанавливает соединение с API
        Каждая платформа реализует это по-своему
        """
        pass

    @abstractmethod
    def get_vacancies(self, keyword: str) -> List[Dict]:
        """
        Получает список вакансий из API

        Args:
            keyword (str): Поисковый запрос (например: "Python разработчик")

        Returns:
            List[Dict]: Список словарей с данными вакансий в формате API
        """
        pass


class HeadHunterAPI(BaseVacancyApi):
    """Класс для подключения к API hh.ru"""

    def __init__(self) -> None:
        """
        Конструктор класса. Вызывается при создании объекта:
        hh_api = HeadHunterAPI()
        """

        # Базовый URL для поиска вакансий - приватный атрибут
        self.__base_url = "https://api.hh.ru/vacancies"

        # URL для поиска ID городов - приватный атрибут
        self.__areas_url = "https://api.hh.ru/suggests/areas"

        # Сессия для HTTP-запросов - пока None, создадим в _connect()
        self.__session: Optional[requests.Session] = None

        # Сразу устанавливаем соединение при создании объекта
        self._connect()

    def _connect(self) -> None:
        """
        Устанавливает соединение с API hh.ru
        Создаёт и настраивает HTTP-сессию, проверяет доступность API.
        """

        if self.__session is None:
            self.__session = requests.Session()

            try:
                if self.__session:
                    params: Dict[str, Union[str, int]] = {"text": "test", "per_page": 1}

                    response = self.__session.get(self.__base_url, params=params, timeout=10)
                    response.raise_for_status()
                    print("✅ Соединение с hh.ru установлено")

            except Exception as e:
                print(f"Внимание: {e}")

    def _find_city_id(self, city_name: str) -> Optional[int]:
        """
        Находит ID города по его названию через API hh.ru
        :param city_name:
                Название города в любом регистре
        :return:
               Optional[int]: ID города или None если город не найден
        """

        # Если передали пустую строку - сразу возвращаем None
        if not city_name:
            return None

        if self.__session is None:
            return None

        try:
            response = self.__session.get(self.__areas_url, params={"text": city_name}, timeout=5)

            if response is None:
                return None

            # Парсим JSON-ответ
            data = response.json()

            if data is None:
                return None

            # Берём первый результат
            items = data.get("items")
            if items and len(items) > 0:
                city_id = items[0].get("id")
                if city_id:
                    return int(city_id)  # Конвертируем строку в число

        except Exception as e:
            # Если ошибка (нет интернета, API не отвечает и т.д.)
            print(f"Ошибка при поиске города '{city_name}': {e}")

        return None

    def get_vacancies(self, keyword: str, **kwargs: Any) -> List[Dict]:
        """
        Получает вакансию по ключевому слову и городу

        Алгоритм работы:
        1. Валидация входных данных
        2. Поиск ID города (если указан)
        3. Последовательный запрос вакансий по страницам
        4. Обработка ошибок и пагинации

        :param keyword:
                Ключевое слово для поиска
        :param kwargs:
        Дополнительные параметры:
            - max_pages: количество страниц (по умолчанию 5)
            - city: город для поиска (опционально)
        :return: Список словарей с данными вакансий
        """

        # Извлекаем параметры из kwargs
        max_pages = kwargs.get("max_pages", 5)
        city = kwargs.get("city", None)

        # Проверяем, что keyword - непустая строка
        if not keyword or not isinstance(keyword, str):
            raise ValueError("Ключевое слово не может быть пустым")

        # 1. Валидация входных данных

        # Убираем лишние пробелы
        keyword = keyword.strip()

        # Проверяем что осталось не только пробелы
        if not keyword:
            raise ValueError("Ключевое слово не может состоять только из пробелов")

        # Количество страниц должно быть положительным
        if max_pages <= 0:
            raise ValueError("Количество страниц должно быть положительным числом")

        # 2. Проверяем соединение

        # Если по какой-то причине сессия не создана - создаём
        if self.__session is None:
            self._connect()
            if self.__session is None:
                print("Не удалось установить соединение с API")
                return []

        # 3. Определяем, где ищем (город или вся Россия)

        area_id = 113  # По умолчанию - вся Россия

        if city:
            # Пытаемся найти ID города
            found_id = self._find_city_id(city)

            if found_id:
                # Город найден, используем его ID
                area_id = found_id
                print(f"Ищем вакансию в городе: {city} ")
            else:
                # Город не найден, ищем по всей России
                print(f"Город '{city}' не найден. Ищем по всей России")

        else:
            # Город не указан - ищем по России
            print("Ищем вакансии по всей России")

        # 4. Постраничный поиск

        # Здесь будем накапливать все найденные вакансии
        all_vacancies = []

        for page in range(max_pages):
            """
            Цикл по страницам:
            page = 0 → первая страница (в hh.ru нумерация с 0)
            page = 1 → вторая страница
            и т.д.
            """

            try:
                if self.__session is None:
                    print(f"Сессия потеряна на странице {page + 1}")
                    break
                # Параметры запроса для текущей страницы
                params: Dict[str, Union[str, int, bool, None]] = {
                    "text": keyword,  # Что ищем
                    "area": area_id,  # Где ищем
                    "page": page,  # Номер страницы
                    "per_page": 100,  # Максимум на странице
                    "only_with_salary": False,  # Включая вакансии без зарплаты
                }

                # Выполняем HTTP GET запрос
                response = self.__session.get(self.__base_url, params=params, timeout=15)

                # Проверяем статус ответа (выбрасывает исключение при ошибке)
                response.raise_for_status()

                # Парсим JSON ответ
                data = response.json()

                # Извлекаем список вакансий с текущей страницы
                if data and isinstance(data, dict):
                    page_vacancies = data.get("items", [])
                else:
                    page_vacancies = []

                # Добавляем вакансии в общий список
                all_vacancies.extend(page_vacancies)

                # Проверка пагинации

                # 1. Сначала проверяем по данным API (главная проверка)
                pages_found = data.get("pages", 0)  # Общее количество страниц
                if page >= pages_found - 1:  # Если текущая страница последняя
                    break

                # 2. Проверяем, есть ли вакансии на странице
                if len(page_vacancies) == 0:  # Если страница пустая
                    break  # Выходим из цикла

                # 3. Пауза между запросами (только если НЕ вышли через break!)
                if page < max_pages - 1:
                    time.sleep(0.1)
            except requests.RequestException as e:
                print(f"Ошибка при загрузке страницы {page + 1}: {e}")
                continue
            except Exception as e:
                print(f"Неожиданная ошибка при загрузке страницы {page + 1}: {e}")
                continue

        return all_vacancies

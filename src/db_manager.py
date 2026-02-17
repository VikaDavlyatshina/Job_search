import psycopg2
from typing import List, Tuple
from config import DB_CONFIG, setup_db_manager_logger

# Создаём logger
logger = setup_db_manager_logger()


class DBManager:
    """
    Класс для работы с данными в БД PostgreSQL
    """

    def __init__(self):
        """Инициализирует подключение к БД"""
        try:
            self.conn = psycopg2.connect(
                dbname=DB_CONFIG["NAME"],
                user=DB_CONFIG["USER"],
                password=DB_CONFIG["PASSWORD"],
                host=DB_CONFIG["HOST"],
                port=DB_CONFIG["PORT"],
            )
            self.cur = self.conn.cursor()
            logger.info("✅ DBManager: подключение к БД установлено")
        except Exception as e:
            logger.error(f"❌ DBManager: ошибка подключения к БД: {e}")
            self.conn = None
            self.cur = None

    def close(self):
        """Явно закрывает соединение с БД"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            logger.debug("✅ Соединение с БД закрыто")

    def _check_connection(self) -> bool:
        """Проверяет, есть ли подключение к БД"""
        if not self.cur or not self.conn:
            logger.debug("❌ Нет подключения к БД")
            return False
        return True

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """
        Получает список всех компаний и количество вакансий у каждой компании
        """
        if not self._check_connection():
            return []

        query = """
            SELECT employers.name, COUNT(vacancies.id) as vacancy_count
            FROM employers
            LEFT JOIN vacancies ON employers.id = vacancies.employer_id
            GROUP BY employers.name
            ORDER BY vacancy_count DESC
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple]:
        """
        Получает список всех вакансий
        """
        if not self._check_connection():
            return []

        query = """
            SELECT employers.name, vacancies.title, 
                   vacancies.salary_from, vacancies.salary_to, vacancies.currency,
                   vacancies.url
            FROM vacancies
            INNER JOIN employers ON vacancies.employer_id = employers.id
            ORDER BY employers.name, vacancies.salary_from DESC NULLS LAST
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям
        """
        if not self._check_connection():
            return 0

        query = """
            SELECT AVG((salary_from + salary_to) / 2) as avg_salary
            FROM vacancies
            WHERE currency = 'RUR' AND salary_from IS NOT NULL AND salary_to IS NOT NULL
        """
        self.cur.execute(query)
        result = self.cur.fetchone()[0]
        return round(result) if result else 0

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """
        Получает вакансии с зарплатой выше средней
        """
        avg_salary = self.get_avg_salary()
        if avg_salary == 0:
            return []

        if not self._check_connection():
            return []

        query = """
            SELECT employers.name, vacancies.title, 
                   vacancies.salary_from, vacancies.salary_to, vacancies.currency,
                   vacancies.url
            FROM vacancies
            INNER JOIN employers ON vacancies.employer_id = employers.id
            WHERE currency = 'RUR' 
            AND salary_from IS NOT NULL
            AND salary_to IS NOT NULL
            AND ((salary_from + salary_to) / 2) > %s
            ORDER BY (salary_from + salary_to) / 2 DESC
        """

        self.cur.execute(query, (avg_salary,))
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """
        Получает вакансии по ключевому слову в названии
        """
        if not keyword:
            return []

        if not self._check_connection():
            return []

        query = """
            SELECT employers.name, vacancies.title, 
                   vacancies.salary_from, vacancies.salary_to, vacancies.currency,
                   vacancies.url
            FROM vacancies
            INNER JOIN employers ON vacancies.employer_id = employers.id
            WHERE vacancies.title ILIKE %s
            ORDER BY employers.name
        """
        self.cur.execute(query, (f"%{keyword}%",))
        return self.cur.fetchall()

    def get_vacancies_by_employer(self, employer_name: str) -> List[Tuple]:
        """
        Получает все вакансии у указанного работодателя (компании)
        :param:
            employer_name: название компании (можно частичное, например "Яндекс")

        :return:
            Список вакансий компании
        """
        if not self._check_connection():
            return []

        try:
            # Используем ILIKE для поиска без учета регистра
            self.cur.execute(
                """
                            SELECT 
                                employers.name,
                                vacancies.title,
                                vacancies.salary_from,
                                vacancies.salary_to,
                                vacancies.currency,
                                vacancies.url
                            FROM vacancies
                            INNER JOIN employers ON vacancies.employer_id = employers.id
                            WHERE employers.name ILIKE %s
                            ORDER BY vacancies.salary_from DESC NULLS LAST, vacancies.title
                        """,
                (f"%{employer_name}%",),
            )

            return self.cur.fetchall()

        except Exception as e:
            logger.error(f"❌ Ошибка в get_vacancies_by_employer: {e}")
            return []

    def get_median_salary(self) -> float:
        """
        Вычисляет медианную зарплату по всем вакансиям
        """

        if not self._check_connection():
            return 0

        try:
            self.cur.execute(
                """
                            SELECT PERCENTILE_CONT(0.5) WITHIN GROUP 
                                   (ORDER BY (salary_from + salary_to) / 2.0) as median
                            FROM vacancies
                            WHERE salary_from IS NOT NULL 
                              AND salary_to IS NOT NULL
                              AND currency = 'RUR'
                        """
            )

            result = self.cur.fetchone()[0]
            return result or 0

        except Exception as e:
            logger.error(f"❌ Ошибка при вычислении медианы: {e}")
            return 0

    def __del__(self):
        """Деструктор - закрывает соединение при удалении объекта"""
        self.close()

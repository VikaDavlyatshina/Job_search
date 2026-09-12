from typing import Optional

import psycopg2

from config import DB_CONFIG, EMPLOYER_IDS, setup_database_logger
from src.api import HeadHunterAPI

# Создаём logger
logger = setup_database_logger()


class DBCreator:
    def __init__(self) -> None:
        """Подключение к серверу PostgreSQL для создания БД."""
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None
        self.connect_to_postgres()

    def connect_to_postgres(self) -> None:
        """Внутренний метод: подключается к служебной БД postgres."""
        try:
            self.conn = psycopg2.connect(
                dbname="postgres",
                user=DB_CONFIG["USER"],
                password=DB_CONFIG["PASSWORD"],
                host=DB_CONFIG["HOST"],
                port=DB_CONFIG["PORT"],
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            self.conn = None
            self.cursor = None
            raise

    def _ensure_connection(self) -> bool:
        """Проверяет, есть ли активное соединение."""
        if self.conn is None or self.cursor is None:
            logger.error("Нет подключения к БД")
            return False
        return True

    def _get_cursor(self) -> psycopg2.extensions.cursor:
        """Безопасно возвращает курсор или вызывает исключение."""
        if self.cursor is None:
            raise RuntimeError("Курсор не инициализирован")
        return self.cursor

    def _get_conn(self) -> psycopg2.extensions.connection:
        """Безопасно возвращает соединение или вызывает исключение."""
        if self.conn is None:
            raise RuntimeError("Соединение не инициализировано")
        return self.conn

    def close_all_connections_to_db(self, db_name: str) -> None:
        """Закрывает все подключения к указанной БД."""
        try:
            cursor = self._get_cursor()
            cursor.execute(
                """
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                  AND pid <> pg_backend_pid();
            """,
                (db_name,),
            )
            logger.info(f"Закрыты все подключения к БД {db_name}")
        except (RuntimeError, psycopg2.Error) as e:
            logger.error(f"Ошибка при закрытии подключений: {e}")

    def database_exists(self) -> bool:
        """Проверяет, существует ли база данных."""
        try:
            cursor = self._get_cursor()
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (DB_CONFIG["NAME"],),
            )
            result = cursor.fetchone()
            return result is not None
        except (RuntimeError, psycopg2.Error) as e:
            logger.error(f"Ошибка при проверке существования БД: {e}")
            return False

    def create_database(self) -> bool:
        """Создает базу данных, если её нет"""
        db_name = DB_CONFIG["NAME"]

        try:
            if self.database_exists():
                logger.info(f"База данных {db_name} уже существует")
                return False

            cursor = self._get_cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ База данных {db_name} создана успешно.")
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании БД: {e}")
            raise
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()

    def recreate_database(self) -> bool:
        """Пересоздает базу данных (удаляет и создает заново)."""

        db_name = DB_CONFIG["NAME"]

        if db_name is None:  # Проверка на None
            logger.error("Имя базы данных не может быть None")
            return False

        try:
            self.close_all_connections_to_db(db_name)  # ✅ Теперь точно str
            cursor = self._get_cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            logger.info(f"Старая БД {db_name} удалена")
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"✅ База данных {db_name} создана заново")

            return True

        except Exception as e:
            logger.error(f"Ошибка при пересоздании БД: {e}")
            raise
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()

    def create_tables(self) -> None:
        """Создает таблицы в БД, если их нет."""
        conn = psycopg2.connect(
            dbname=DB_CONFIG["NAME"],
            user=DB_CONFIG["USER"],
            password=DB_CONFIG["PASSWORD"],
            host=DB_CONFIG["HOST"],
            port=DB_CONFIG["PORT"],
        )
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    url TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            logger.info("✅ Таблица 'employers' создана")

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY,
                    employer_id INTEGER REFERENCES employers(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency VARCHAR(10),
                    url TEXT,
                    requirements TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            logger.info("✅ Таблица 'vacancies' создана")

            conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def is_database_empty(self) -> bool:
        """Проверяет, есть ли данные в таблицах."""
        conn = psycopg2.connect(
            dbname=DB_CONFIG["NAME"],
            user=DB_CONFIG["USER"],
            password=DB_CONFIG["PASSWORD"],
            host=DB_CONFIG["HOST"],
            port=DB_CONFIG["PORT"],
        )
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM employers")
            count = cursor.fetchone()[0]
            return bool(count == 0)
        finally:
            cursor.close()
            conn.close()

    def get_last_update_time(self) -> Optional[str]:
        """Получает время последнего обновления данных."""
        conn = psycopg2.connect(
            dbname=DB_CONFIG["NAME"],
            user=DB_CONFIG["USER"],
            password=DB_CONFIG["PASSWORD"],
            host=DB_CONFIG["HOST"],
            port=DB_CONFIG["PORT"],
        )
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT MAX(created_at) FROM (
                    SELECT created_at FROM employers
                    UNION ALL
                    SELECT created_at FROM vacancies
                ) AS all_dates
            """
            )
            last_update = cursor.fetchone()[0]
            return str(last_update) if last_update else None
        finally:
            cursor.close()
            conn.close()

    def fill_database(self, force_recreate: bool = False) -> None:
        """Заполняет таблицы данными из API HH.ru."""
        if force_recreate or not self.database_exists():
            self.connect_to_postgres()
            self.recreate_database()

        self.create_tables()

        if not force_recreate and not self.is_database_empty():
            last_update = self.get_last_update_time()
            if last_update:
                logger.info(f"📊 База данных уже содержит данные (последнее обновление: {last_update})")
                response = input("Хотите обновить данные? (да/нет): ").strip().lower()
                if response not in ["да", "д", "yes", "y"]:
                    logger.info("Заполнение пропущено")
                    return

        hh = HeadHunterAPI()
        conn = psycopg2.connect(
            dbname=DB_CONFIG["NAME"],
            user=DB_CONFIG["USER"],
            password=DB_CONFIG["PASSWORD"],
            host=DB_CONFIG["HOST"],
            port=DB_CONFIG["PORT"],
        )
        cursor = conn.cursor()

        companies_saved = 0
        vacancies_saved = 0

        try:
            for employer_id in EMPLOYER_IDS:
                logger.info(f"\nОбрабатываем компанию ID: {employer_id}")

                employer_data = hh.get_employer_info(employer_id)
                if not employer_data:
                    logger.warning(f"Не удалось получить данные компании {employer_id}")
                    continue

                cursor.execute(
                    """
                    INSERT INTO employers (id, name, url, description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING""",
                    (
                        employer_data["id"],
                        employer_data["name"],
                        employer_data.get("alternate_url", ""),
                        employer_data.get("description", "")[:1000],
                    ),
                )
                companies_saved += 1
                logger.info(f"✅ Компания сохранена: {employer_data['name']}")

                vacancies_data = hh.get_vacancies_by_employer(employer_id, limit=50)
                logger.info(f"Получено вакансий: {len(vacancies_data)}")

                for vac in vacancies_data:
                    salary_info = vac.get("salary")
                    if salary_info:
                        salary_from = salary_info.get("from")
                        salary_to = salary_info.get("to")
                        currency = salary_info.get("currency")
                    else:
                        salary_from = salary_to = currency = None

                    requirements = vac.get("snippet", {}).get("requirement", "")
                    if requirements and len(requirements) > 1000:
                        requirements = requirements[:997] + "..."

                    cursor.execute(
                        """
                        INSERT INTO vacancies (id, employer_id, title,
                           salary_from, salary_to, currency, url, requirements)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING""",
                        (
                            vac["id"],
                            employer_id,
                            vac["name"],
                            salary_from,
                            salary_to,
                            currency,
                            vac.get("alternate_url", ""),
                            requirements,
                        ),
                    )
                    vacancies_saved += 1

                conn.commit()
                logger.info(f"✅ Сохранено вакансий: {len(vacancies_data)}")

            logger.info("ИТОГИ ЗАПОЛНЕНИЯ:")
            logger.info(f"  Компаний: {companies_saved}/{len(EMPLOYER_IDS)}")
            logger.info(f"  Вакансий: {vacancies_saved}")

        except Exception as e:
            logger.error(f"Ошибка при заполнении БД: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

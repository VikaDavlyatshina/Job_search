import logging
from pathlib import Path
import os

from dotenv import load_dotenv


# Загрузка переменных из .env файла
load_dotenv()

# Базовые пути
PROJECT_ROOT = Path(__file__).parent
LOGS_DIR = PROJECT_ROOT / "logs"

# Создаём папку если её нет
LOGS_DIR.mkdir(exist_ok=True)

# Стандартный формат логов
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# ---------- УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ----------
def create_logger(name: str, log_file: Path) -> logging.Logger:
    """Создаёт и настраивает логгер по имени и пути к файлу."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


# ========== ЛОГГЕРЫ ДЛЯ ОСНОВНОГО ПРИЛОЖЕНИЯ ==========
def setup_database_logger() -> logging.Logger:
    return create_logger("database", LOGS_DIR / "database.log")


def setup_api_logger() -> logging.Logger:
    return create_logger("api", LOGS_DIR / "api.log")


def setup_db_manager_logger() -> logging.Logger:
    return create_logger("db_manager", LOGS_DIR / "db_manager.log")


# ========== НАСТРОЙКА БАЗЫ ДАННЫХ ==========
DB_CONFIG = {
    "NAME": os.getenv("DB_NAME"),
    "USER": os.getenv("DB_USER"),
    "PASSWORD": os.getenv("DB_PASSWORD"),
    "HOST": os.getenv("DB_HOST"),
    "PORT": os.getenv("DB_PORT"),
}


# ========== КОМПАНИИ ДЛЯ СБОРА ==========
EMPLOYER_IDS = [
    "1740",  # Яндекс
    "15478",  # VK
    "78638",  # Тинькофф
    "3529",  # Сбер
    "3776",  # МТС
    "80",  # Альфа-Банк
    "1057",  # Лаборатория касперского
    "41862",  # Контур
    "2180",  # Озон
    "87021",  # Wildberries & Russ (RWB)
]

# ========== НАСТРОЙКИ СБОРА ДАННЫХ ==========
VACANCIES_PER_COMPANY = 50  # Сколько вакансий собирать с каждой компании

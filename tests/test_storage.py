import json
import os
import tempfile

from src.storage import JSONSaver
from src.vacancy import Vacancy


def test_create_saver_default_filename() -> None:
    """Тест: создание JSONSaver с именем файла по умолчанию"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Переходим во временную папку
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        try:
            # Создаем saver без указания файла
            saver = JSONSaver()

            # Проверяем
            assert saver.filename == "vacancies.json"
            assert os.path.exists("vacancies.json")

            # Проверяем содержимое файла
            with open("vacancies.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                assert data == []  # Должен быть пустой список

        finally:
            os.chdir(original_dir)


def test_create_saver_custom_filename() -> None:
    """Тест: создание JSONSaver с указанием имени файла"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Создаем файл с кастомным именем
        custom_file = os.path.join(tmpdir, "my_vacancies.json")
        saver = JSONSaver(custom_file)

        assert saver.filename == "my_vacancies.json"
        assert os.path.exists(custom_file)


def test_create_saver_existing_file() -> None:
    """Тест: создание JSONSaver когда файл уже существует с данными"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        # Создаем файл с данными
        existing_data = [{"name": "Существующая вакансия", "url": "test.com"}]
        json.dump(existing_data, f)
        file_path = f.name

    try:
        # Создаем saver для существующего файла
        saver = JSONSaver(file_path)

        # Проверяем что данные не потерялись
        data = saver._load_data()
        assert len(data) == 1
        assert data[0]["name"] == "Существующая вакансия"

    finally:
        # Удаляем временный файл
        os.unlink(file_path)


# ТЕСТЫ ОСНОВНЫХ ОПЕРАЦИЙ
def test_add_vacancy(json_saver: JSONSaver, sample_vacancy: Vacancy) -> None:
    """Тест: добавление вакансии в файл"""
    # Добавляем вакансию
    json_saver.add_vacancy(sample_vacancy)

    # Проверяем что вакансия сохранилась
    vacancies = json_saver.get_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0].name == "Python Developer"
    assert vacancies[0].url == "https://hh.ru/vacancy/123"


def test_add_duplicate_vacancy(json_saver: JSONSaver, sample_vacancy: Vacancy) -> None:
    """Тест: попытка добавить вакансию дважды (дубликат)"""
    # Добавляем вакансию первый раз
    json_saver.add_vacancy(sample_vacancy)

    # Пытаемся добавить ту же вакансию еще раз
    json_saver.add_vacancy(sample_vacancy)

    # Проверяем что добавилась только одна
    vacancies = json_saver.get_vacancies()
    assert len(vacancies) == 1  # Дубликат не должен добавиться


def test_get_all_vacancies(json_saver: JSONSaver, sample_vacancy: Vacancy, java_vacancy: Vacancy) -> None:
    """Тест: получение всех вакансий из файла"""
    # Добавляем две вакансии
    json_saver.add_vacancy(sample_vacancy)
    json_saver.add_vacancy(java_vacancy)

    # Получаем все вакансии
    vacancies = json_saver.get_vacancies()

    # Проверяем
    assert len(vacancies) == 2
    assert isinstance(vacancies[0], Vacancy)
    assert isinstance(vacancies[1], Vacancy)

    # Проверяем имена
    names = [v.name for v in vacancies]
    assert "Python Developer" in names
    assert "Java Developer" in names


def test_get_vacancies_with_filters(json_saver: JSONSaver, sample_vacancy: Vacancy, java_vacancy: Vacancy) -> None:
    """Тест: фильтрация вакансий по критериям"""
    # Добавляем вакансии
    json_saver.add_vacancy(sample_vacancy)
    json_saver.add_vacancy(java_vacancy)

    # Фильтр по городу
    moscow_vacancies = json_saver.get_vacancies(area="Москва")
    assert len(moscow_vacancies) == 1
    assert moscow_vacancies[0].name == "Python Developer"

    # Фильтр по названию
    python_vacancies = json_saver.get_vacancies(name="Python")
    assert len(python_vacancies) == 1
    assert python_vacancies[0].name == "Python Developer"


def test_delete_vacancy(json_saver: JSONSaver, sample_vacancy: Vacancy, java_vacancy: Vacancy) -> None:
    """Тест: удаление вакансии"""
    # Добавляем две вакансии
    json_saver.add_vacancy(sample_vacancy)
    json_saver.add_vacancy(java_vacancy)

    # Проверяем что две вакансии
    assert len(json_saver.get_vacancies()) == 2

    # Удаляем одну
    json_saver.delete_vacancy(sample_vacancy)

    # Проверяем что осталась одна
    vacancies = json_saver.get_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0].name == "Java Developer"


def test_delete_vacancy_by_url(json_saver: JSONSaver, sample_vacancy: Vacancy) -> None:
    """Тест: удаление вакансии по URL"""
    # Добавляем вакансию
    json_saver.add_vacancy(sample_vacancy)

    # Удаляем по URL
    result = json_saver.delete_vacancy_by_url("https://hh.ru/vacancy/123")

    # Проверяем
    assert result is True  # Вакансия найдена и удалена
    assert len(json_saver.get_vacancies()) == 0  # Файл пустой

    # Пытаемся удалить несуществующую вакансию
    result2 = json_saver.delete_vacancy_by_url("https://nonexistent.com")
    assert result2 is False  # Возвращает False


def test_check_vacancy_saved(json_saver: JSONSaver, sample_vacancy: Vacancy) -> None:
    """Тест: проверка сохранена ли вакансия"""
    # Пока не добавляли - должна быть False
    assert json_saver.is_vacancy_saved("https://hh.ru/vacancy/123") is False

    # Добавляем вакансию
    json_saver.add_vacancy(sample_vacancy)

    # Теперь должна быть True
    assert json_saver.is_vacancy_saved("https://hh.ru/vacancy/123") is True

    # Проверяем несуществующую вакансию
    assert json_saver.is_vacancy_saved("https://nonexistent.com") is False


def test_clear_all_vacancies(json_saver: JSONSaver, sample_vacancy: Vacancy, java_vacancy: Vacancy) -> None:
    """Тест: очистка всех вакансий"""
    # Добавляем две вакансии
    json_saver.add_vacancy(sample_vacancy)
    json_saver.add_vacancy(java_vacancy)

    # Проверяем что добавились
    assert len(json_saver.get_vacancies()) == 2

    # Очищаем все
    json_saver.clear_all()

    # Проверяем что пусто
    assert len(json_saver.get_vacancies()) == 0


# ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ
def test_dict_to_vacancy_conversion() -> None:
    """Тест: преобразование словаря в объект Vacancy"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        file_path = f.name

    try:
        saver = JSONSaver(file_path)

        # Тестовые данные (как они хранятся в JSON)
        test_dict = {
            "name": "Тестовая вакансия",
            "area": "Москва",
            "salary_from": "100000",  # В JSON это строка!
            "salary_to": "150000",  # В JSON это строка!
            "requirement": "Требования",
            "responsibility": "Обязанности",
            "schedule": "Полный день",
            "url": "https://test.com",
        }

        # Преобразуем словарь в Vacancy
        vacancy = saver._dict_to_vacancy(test_dict)

        # Проверяем
        assert isinstance(vacancy, Vacancy)
        assert vacancy.name == "Тестовая вакансия"
        assert vacancy.salary_from == 100000  # Преобразовано из строки в int
        assert vacancy.salary_to == 150000  # Преобразовано из строки в int

    finally:
        os.unlink(file_path)


def test_corrupted_json_file() -> None:
    """Тест: что происходит если JSON файл поврежден"""
    # Создаем файл с неправильным JSON
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        f.write("{это не правильный json")  # Битый JSON
        file_path = f.name

    try:
        # Пытаемся создать saver с битым файлом
        saver = JSONSaver(file_path)

        # Должен создаться пустой список
        data = saver._load_data()
        assert data == []  # При ошибке должен вернуть пустой список

    finally:
        os.unlink(file_path)

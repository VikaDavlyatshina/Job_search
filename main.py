from typing import List

from src.api import HeadHunterAPI
from src.db_manager import DBManager
from src.db_utils import setup_database, show_database_menu
from src.storage import JSONSaver
from src.utils import (
    filter_vacancies,
    filter_vacancies_by_profession,
    get_top_vacancies,
    get_vacancies_by_salary,
    print_vacancies,
    sort_vacancies_by_salary,
)
from src.vacancy import Vacancy


def print_header(title: str, symbol: str = "═", length: int = 50) -> None:
    """
    Печатает красивый заголовок для разделения секций в меню.

    :param:
        title: Текст заголовка
        symbol: Символ для обрамления (по умолчанию '═')
        length: Длина линии (по умолчанию 50)
    """
    print(f"\n{symbol * length}")
    print(f"{title}")
    print(f"{symbol * length}")


def show_saved_vacancies(saver: JSONSaver) -> None:
    """
    Показывает сохранённые вакансии из JSON-файла.
    Выводит первые 20 вакансий с основной информацией.

    :param:
        saver: Экземпляр JSONSaver для работы с файлом
    """
    saved = saver.get_vacancies()

    if not saved:
        print("📭 В файле нет сохранённых вакансий")
        return

    print_header(f"📁 СОХРАНЕНО ВАКАНСИЙ: {len(saved)}", "─")
    print(f"Файл: {saver.filename}")

    # Показываем первые 20 вакансий (чтобы не перегружать экран)
    for i, vacancy in enumerate(saved[:20], 1):
        print(f"\n{'─' * 40}")
        print(f"№{i}. {vacancy.name}")
        print(f"   Город: {vacancy.area}")
        print("   Зарплата: ", end="")

        # Форматируем зарплату в зависимости от наличия данных
        if vacancy.salary_from or vacancy.salary_to:
            if vacancy.salary_from:
                print(f"от {vacancy.salary_from:,}".replace(",", " "), end=" ")
            if vacancy.salary_to:
                print(f"до {vacancy.salary_to:,}".replace(",", " "), end=" ")
            print("руб.")
        else:
            print("Не указана")
        print(f"   Ссылка: {vacancy.url}")

    if len(saved) > 20:
        print(f"\n... и ещё {len(saved) - 20} вакансий")

    input("\nНажмите Enter чтобы продолжить...")


def show_top_vacancies_menu(saver: JSONSaver) -> None:
    """
    Показывает топ-N вакансий по зарплате.
    """
    saved = saver.get_vacancies()

    if not saved:
        print("📭 В файле нет сохранённых вакансий")
        return

    print_header("🏆 ТОП ВАКАНСИЙ ПО ЗАРПЛАТЕ", "─")
    print(f"\n📁 Всего сохранено: {len(saved)} вакансий")

    try:
        # Запрашиваем количество вакансий для отображения
        top_n_input = input("\n🔢 Сколько вакансий показать? (Enter - 10, '0' - отмена): ").strip()

        if top_n_input == "0":
            print("🚫 Отменено")
            return

        if not top_n_input:
            top_n = 10
        else:
            top_n = int(top_n_input)
            if top_n <= 0:
                print("❌ Введите положительное число")
                return

        # Получаем топ-N вакансий
        top_vacancies = get_top_vacancies(saved, top_n)

        if top_vacancies:
            print(f"\n🏆 ТОП-{len(top_vacancies)} ВАКАНСИЙ ПО ЗАРПЛАТЕ:")
            print_vacancies(top_vacancies)

            # Вычисляем диапазон зарплат для статистики
            salaries = []
            for v in top_vacancies:
                # Проверяем на None
                if v.salary_from is not None and v.salary_to is not None:
                    salaries.append((v.salary_from + v.salary_to) / 2)
                elif v.salary_from is not None:
                    salaries.append(float(v.salary_from))
                elif v.salary_to is not None:
                    salaries.append(float(v.salary_to))

            if salaries:
                print(f"\n📊 Диапазон зарплат в топе: {min(salaries):,.0f} - {max(salaries):,.0f} руб.")
        else:
            print("📭 Не удалось получить топ вакансий")

    except ValueError:
        print("❌ Введите число")


def delete_vacancy_menu(saver: JSONSaver) -> None:
    """
    Меню удаления вакансии из JSON-файла по номеру.
    Показывает список вакансий и запрашивает номер для удаления.
    """
    saved = saver.get_vacancies()

    if not saved:
        print("📭 Нет сохранённых вакансий")
        return

    print_header("🗑️  УДАЛЕНИЕ ВАКАНСИИ", "─")
    show_saved_vacancies(saver)

    try:
        num_input = input("\nВведите номер вакансии для удаления (0 для отмены): ").strip()

        if not num_input or num_input == "0":
            return

        num = int(num_input)

        if 1 <= num <= len(saved):
            vacancy_to_delete = saved[num - 1]
            if saver.delete_vacancy_by_url(vacancy_to_delete.url):
                print(f"✅ Вакансия №{num} удалена")
            else:
                print("❌ Ошибка при удалении")
        else:
            print("❌ Неверный номер")
    except ValueError:
        print("❌ Введите число")


def clear_file_menu(saver: JSONSaver) -> None:
    """
    Меню очистки JSON-файла.
    Запрашивает подтверждение перед удалением всех вакансий.
    """
    print_header("🧹 ОЧИСТКА ФАЙЛА", "─")
    print(f"Файл: {saver.filename}")
    print(f"Вакансий в файле: {len(saver.get_vacancies())}")

    confirm = input("\n⚠️  ВЫ УВЕРЕНЫ? Все вакансии будут удалены! (да/нет): ").strip().lower()
    if confirm in ["да", "д", "yes", "y"]:
        saver.clear_all()
        print("✅ Файл очищен")
    else:
        print("❌ Отменено")


def perform_hh_search(api: HeadHunterAPI) -> List[Vacancy]:
    """
    Выполняет поиск через HeadHunter API с пошаговым подтверждением.
    Пользователь может отменить поиск на любом этапе, введя 'm' или '0'.

    :param:
        api: Экземпляр HeadHunterAPI для работы с API

    :return:
        List[Vacancy]: Список найденных вакансий или пустой список
    """
    print_header("🔍 ПОИСК НА HH.RU", "─")

    # ---- ШАГ 1: Ввод поискового запроса ----
    while True:
        search_query = input("\n📝 Введите поисковый запрос (Enter - отмена, 'm'/'0' - выход в меню): ").strip()

        # Проверка на выход в меню
        if search_query.lower() in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
            print("🚫 Поиск отменён")
            return []

        if not search_query:
            print("❌ Поисковый запрос не может быть пустым! Попробуйте снова.")
            continue

        # Подтверждение запроса
        print(f"\n🔎 Ваш запрос: '{search_query}'")
        print("   ✅ Enter - подтвердить")
        print("   🔄 'нет' - ввести заново")
        print("   🚫 'm'/'0' - выход в меню")

        confirm = input("👉 Ваш выбор: ").strip().lower()

        if confirm == "" or confirm in ["да", "д", "yes", "y"]:
            break
        elif confirm in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
            print("🚫 Поиск отменён")
            return []
        else:
            print("🔄 Введите запрос заново...")
            continue

    # ---- ШАГ 2: Ввод города ----
    while True:
        city = input("\n🏙️  Введите город (Enter - Россия, 'm'/'0' - выход): ").strip()

        if city.lower() in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
            print("🚫 Поиск отменён")
            return []

        city_display = city if city else "Вся Россия"
        print(f"\n🏙️  Выбран город: {city_display}")
        print("   ✅ Enter - подтвердить")
        print("   🔄 'нет' - ввести заново")
        print("   🚫 'm'/'0' - выход в меню")

        confirm = input("👉 Ваш выбор: ").strip().lower()

        if confirm == "" or confirm in ["да", "д", "yes", "y"]:
            break
        elif confirm in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
            print("🚫 Поиск отменён")
            return []
        else:
            print("🔄 Введите город заново...")
            continue

    # ---- ШАГ 3: Ввод количества страниц ----
    while True:
        pages_input = input(
            "\n📄 Сколько страниц искать? (1 стр = 100 вакансий, Enter - 2, 'm'/'0' - выход): "
        ).strip()

        if pages_input.lower() in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
            print("🚫 Поиск отменён")
            return []

        # Значение по умолчанию
        if not pages_input:
            max_pages = 2
            print(f"\n📊 Количество страниц: {max_pages} (по умолчанию)")
            print("   ✅ Enter - подтвердить")
            print("   🔄 'нет' - ввести заново")
            print("   🚫 'm'/'0' - выход в меню")

            confirm = input("👉 Ваш выбор: ").strip().lower()

            if confirm == "" or confirm in ["да", "д", "yes", "y"]:
                break
            elif confirm in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
                print("🚫 Поиск отменён")
                return []
            else:
                print("🔄 Введите количество страниц заново...")
                continue

        if pages_input.isdigit():
            max_pages = int(pages_input)
            if 1 <= max_pages <= 10:
                print(f"\n📊 Количество страниц: {max_pages}")
                print("   ✅ Enter - подтвердить")
                print("   🔄 'нет' - ввести заново")
                print("   🚫 'm'/'0' - выход в меню")

                confirm = input("👉 Ваш выбор: ").strip().lower()

                if confirm == "" or confirm in ["да", "д", "yes", "y"]:
                    break
                elif confirm in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
                    print("🚫 Поиск отменён")
                    return []
                else:
                    print("🔄 Введите количество страниц заново...")
                    continue
            else:
                print("❌ Введите от 1 до 10")
        else:
            print("❌ Введите число")

    # ---- ШАГ 4: Финальное подтверждение перед поиском ----
    print_header("📋 ИТОГОВЫЕ ПАРАМЕТРЫ ПОИСКА", "═")
    print(f"🔎 Запрос: {search_query}")
    print(f"🏙️  Город: {city if city else 'Вся Россия'}")
    print(f"📄 Страниц: {max_pages} (≈ {max_pages * 100} вакансий)")
    print("═" * 50)

    print("\n✅ Enter - начать поиск")
    print("🚫 'm'/'0' - выход в меню")
    print("🔄 'нет' - вернуться к вводу параметров")

    final_confirm = input("👉 Ваш выбор: ").strip().lower()

    if final_confirm == "" or final_confirm in ["да", "д", "yes", "y"]:
        pass  # Продолжаем поиск
    elif final_confirm in ["menu", "m", "0", "exit", "q", "quit", "выход", "в"]:
        print("🚫 Поиск отменён")
        return []
    else:
        print("🔄 Возврат к вводу параметров...")
        return perform_hh_search(api)  # Рекурсивный вызов для повторного ввода

    # ---- ВЫПОЛНЕНИЕ ПОИСКА ----
    print(f"\n📡 Ищем вакансии по запросу: '{search_query}'...")
    try:
        hh_vacancies_data = api.get_vacancies(keyword=search_query, max_pages=max_pages, city=city if city else None)

        if not hh_vacancies_data:
            print("📭 API вернул пустой ответ")
            return []

        vacancies_list = Vacancy.cast_to_object_list(hh_vacancies_data)

        if not vacancies_list:
            print(f"📭 По запросу '{search_query}' вакансий не найдено.")
            return []

        print(f"✅ Найдено вакансий: {len(vacancies_list)}")

        # Применяем дополнительные фильтры
        vacancies_list = apply_filters(vacancies_list)

        if not vacancies_list:
            print("\n❌ После фильтрации не осталось подходящих вакансий.")
            retry = input("🔄 Попробовать другой фильтр? (да/нет): ").strip().lower()
            if retry in ["да", "д", "yes", "y"]:
                return perform_hh_search(api)
            else:
                return []

        if vacancies_list:
            print_vacancies(vacancies_list)

        return vacancies_list

    except Exception as e:
        print(f"❌ Ошибка при получении вакансий: {e}")
        return []


def apply_filters(vacancies_list: List[Vacancy]) -> List[Vacancy]:
    """
    Применяет фильтры к списку вакансий с подтверждением каждого шага.
    Пользователь может подтвердить фильтр, ввести заново или пропустить.

    :param:
        vacancies_list: Исходный список вакансий

    :return:
        List[Vacancy]: Отфильтрованный список вакансий
    """
    if not vacancies_list:
        return []

    original_count = len(vacancies_list)

    # ---- ФИЛЬТР 1: По ключевым словам в названии ----
    while True:
        prof_input = input("\n👔 Ключевые слова в названии (Enter чтобы пропустить): ").strip()

        if not prof_input:
            break

        keywords = [w.strip() for w in prof_input.split(",") if w.strip()]
        print(f"\n🔍 Будет применён фильтр по словам: {', '.join(keywords)}")
        print("   ✅ Enter - подтвердить")
        print("   🔄 'нет' - ввести заново")
        print("   🚫 'm'/'0' - пропустить фильтр")

        confirm = input("👉 Ваш выбор: ").strip().lower()

        if confirm == "" or confirm in ["да", "д", "yes", "y"]:
            vacancies_list = filter_vacancies_by_profession(vacancies_list, keywords)
            print(f"✅ После фильтрации: {len(vacancies_list)}")
            break
        elif confirm in ["menu", "m", "0", "exit", "q", "quit", "пропустить"]:
            print("⏩ Фильтр пропущен")
            break
        else:
            print("🔄 Введите ключевые слова заново...")
            continue

    # ---- ФИЛЬТР 2: По ключевым словам в описании ----
    while True:
        skill_input = input("\n🔧 Ключевые слова в описании (Enter чтобы пропустить): ").strip()

        if not skill_input:
            break

        keywords = [w.strip() for w in skill_input.split(",") if w.strip()]
        print(f"\n🔍 Будет применён фильтр по словам: {', '.join(keywords)}")
        print("   ✅ Enter - подтвердить")
        print("   🔄 'нет' - ввести заново")
        print("   🚫 'm'/'0' - пропустить фильтр")

        confirm = input("👉 Ваш выбор: ").strip().lower()

        if confirm == "" or confirm in ["да", "д", "yes", "y"]:
            vacancies_list = filter_vacancies(vacancies_list, keywords)
            print(f"✅ После фильтрации: {len(vacancies_list)}")
            break
        elif confirm in ["menu", "m", "0", "exit", "q", "quit", "пропустить"]:
            print("⏩ Фильтр пропущен")
            break
        else:
            print("🔄 Введите ключевые слова заново...")
            continue

    # ---- ФИЛЬТР 3: По диапазону зарплат ----
    while True:
        salary_input = input("\n💰 Диапазон зарплат (Enter чтобы пропустить): ").strip()

        if not salary_input:
            break

        print(f"\n🔍 Будет применён фильтр по зарплате: {salary_input}")
        print("   ✅ Enter - подтвердить")
        print("   🔄 'нет' - ввести заново")
        print("   🚫 'm'/'0' - пропустить фильтр")

        confirm = input("👉 Ваш выбор: ").strip().lower()

        if confirm == "" or confirm in ["да", "д", "yes", "y"]:
            vacancies_list = get_vacancies_by_salary(vacancies_list, salary_input)
            print(f"✅ После фильтрации: {len(vacancies_list)}")
            break
        elif confirm in ["menu", "m", "0", "exit", "q", "quit", "пропустить"]:
            print("⏩ Фильтр пропущен")
            break
        else:
            print("🔄 Введите диапазон зарплат заново...")
            continue

    # ---- ИТОГОВАЯ СТАТИСТИКА ----
    if len(vacancies_list) == 0:
        print("\n" + "!" * 50)
        print("⚠️  ВНИМАНИЕ! После применения всех фильтров")
        print("   не осталось ни одной подходящей вакансии!")
        print("!" * 50)
    elif len(vacancies_list) < original_count:
        print(f"\n📊 Итого осталось: {len(vacancies_list)} из {original_count} вакансий")

    return vacancies_list


def show_json_menu(saver: JSONSaver, api: HeadHunterAPI) -> None:
    """
    Меню работы с JSON файлом.
    Предоставляет доступ ко всем функциям работы с JSON: поиск, просмотр, удаление.
    """
    while True:
        print_header("📁 МЕНЮ РАБОТЫ С JSON", "═")
        print(f"\nФайл: {saver.filename}")
        print("\n1. 🔍 Новый поиск вакансий на hh.ru")
        print("2. 📋 Показать сохранённые вакансии")
        print("3. 🏆 Топ вакансий по зарплате")
        print("4. 🗑️  Удалить вакансию")
        print("5. 🧹 Очистить файл")
        print("6. 🔙 Назад")

        choice = input("\n👉 Ваш выбор (1-6): ").strip()

        if choice == "1":
            found = perform_hh_search(api)
            if found:
                save_choice = input("\nСохранить найденные вакансии в JSON? (да/нет): ").strip().lower()
                if save_choice in ["да", "д", "yes", "y"]:
                    # Опциональная сортировка перед сохранением
                    use_sort = input("📊 Отсортировать по зарплате перед сохранением? (да/нет): ").strip().lower()

                    if use_sort in ["да", "д", "yes", "y"]:
                        found = sort_vacancies_by_salary(found)
                        print("✅ Вакансии отсортированы")

                    saved = 0
                    for vacancy in found:
                        if not saver.is_vacancy_saved(vacancy.url):
                            saver.add_vacancy(vacancy)
                            saved += 1
                    print(f"✅ Сохранено: {saved}")
        elif choice == "2":
            show_saved_vacancies(saver)
        elif choice == "3":
            show_top_vacancies_menu(saver)
        elif choice == "4":
            delete_vacancy_menu(saver)
        elif choice == "5":
            clear_file_menu(saver)
        elif choice == "6":
            break
        else:
            print("❌ Неверный выбор")


def main() -> None:
    """Главная функция приложения. Точка входа."""
    print_header("🎯 ПРИЛОЖЕНИЕ ДЛЯ ПОИСКА ВАКАНСИЙ", "═")

    # Инициализация основных компонентов
    json_saver = JSONSaver()
    hh_api = HeadHunterAPI()

    print(f"\n💾 JSON файл: {json_saver.filename}")

    # Проверка наличия базы данных
    try:
        db_test = DBManager()
        db_has_data = len(db_test.get_companies_and_vacancies_count()) > 0
        db_test.close()
    except Exception:
        db_has_data = False

    # Предложение создать БД, если её нет
    if not db_has_data:
        print("\n⚠️  База данных не найдена")
        choice = input("Создать базу данных с информацией о 10 компаниях? (да/нет): ").strip().lower()
        if choice in ["да", "д", "yes", "y"]:
            setup_database()

    # Главный цикл меню
    while True:
        print_header("📋 ГЛАВНОЕ МЕНЮ", "═")
        print("\n1. 🔍 Поиск на HH.ru (JSON)")
        print("2. 🗄️  Работа с базой данных")
        print("3. 👋 Выход")

        choice = input("\n👉 Ваш выбор (1-3): ").strip()

        if choice == "1":
            show_json_menu(json_saver, hh_api)
        elif choice == "2":
            show_database_menu()
        elif choice == "3":
            print_header("👋 ДО СВИДАНИЯ!", "─")
            print(f"\n💾 JSON файл: {json_saver.filename}")
            break
        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    main()

from src.api import HeadHunterAPI
from src.utils import *
from typing import List


# Вспомогательные функции (остаются как у тебя)
def show_saved_vacancies(saver: JSONSaver):
    """Показывает сохранённые вакансии"""
    saved = saver.get_vacancies()

    if not saved:
        print("📭 В файле нет сохранённых вакансий")
        return

    print(f"\n📁 СОХРАНЕНО ВАКАНСИЙ: {len(saved)} (файл: {saver.filename})")

    for i, vacancy in enumerate(saved[:20], 1):
        print(f"\n{'─' * 40}")
        print(f"№{i}. {vacancy.name}")
        print(f"   Город: {vacancy.area}")
        print(f"   Зарплата: ", end="")
        if vacancy.salary_from or vacancy.salary_to:
            if vacancy.salary_from:
                print(f"от {vacancy.salary_from}", end=" ")
            if vacancy.salary_to:
                print(f"до {vacancy.salary_to}", end=" ")
            print("руб.")
        else:
            print("Не указана")
        print(f"   Ссылка: {vacancy.url}")

    if len(saved) > 20:
        print(f"\n... и ещё {len(saved) - 20} вакансий")

    input("\nНажмите Enter чтобы продолжить...")


def delete_vacancy_menu(saver: JSONSaver):
    """Меню удаления вакансии"""
    saved = saver.get_vacancies()

    if not saved:
        print("📭 Нет сохранённых вакансий")
        return

    print("\n🗑️  УДАЛЕНИЕ ВАКАНСИИ")
    show_saved_vacancies(saver)

    try:
        num = int(input("\nВведите номер вакансии для удаления (0 для отмены): "))
        if num == 0:
            return

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


def clear_file_menu(saver: JSONSaver):
    """Меню очистки файла"""
    confirm = input("⚠️  ВЫ УВЕРЕНЫ? Все вакансии будут удалены! (да/нет): ").strip().lower()
    if confirm in ['да', 'д', 'yes', 'y']:
        saver.clear_all()
        print("✅ Файл очищен")
    else:
        print("❌ Отменено")


def perform_hh_search(api: HeadHunterAPI) -> List[Vacancy]:
    """Выполняет поиск через HeadHunter API"""
    print("\n" + "─" * 50)
    print("🔍 ПОИСК НА HH.RU")
    print("─" * 50)

    # 1. Получаем поисковый запрос
    search_query = input("Введите поисковый запрос (например: 'Python разработчик'): ").strip()
    if not search_query:
        print("❌ Поисковый запрос не может быть пустым!")
        return []

    # 2. Город
    print("\n🏙️  ВЫБОР ГОРОДА")
    city = input("Введите город (или Enter для поиска по России): ").strip()

    # 3. Количество страниц
    while True:
        pages_input = input("Сколько страниц искать? (1 стр = 100 вакансий, Enter для 2): ").strip()
        if not pages_input:
            max_pages = 2
            break
        elif pages_input.isdigit():
            max_pages = int(pages_input)
            if 1 <= max_pages <= 10:
                break
            else:
                print("❌ Введите от 1 до 10")
        else:
            print("❌ Введите число")

    # 4. Получаем вакансии через API
    print(f"\n📡 Ищем вакансии по запросу: '{search_query}'...")
    try:
        hh_vacancies_data = api.get_vacancies(
            keyword=search_query,
            max_pages=max_pages,
            city=city if city else None
        )
        vacancies_list = Vacancy.cast_to_object_list(hh_vacancies_data)

        if not vacancies_list:
            print(f"📭 По запросу '{search_query}' вакансий не найдено.")
            return []

        print(f"✅ Найдено вакансий: {len(vacancies_list)}")

    except Exception as e:
        print(f"❌ Ошибка при получении вакансий: {e}")
        return []

    # 5. Фильтрация по ключевым словам
    print("\n🔍 ФИЛЬТРАЦИЯ ПО КЛЮЧЕВЫМ СЛОВАМ В ОПИСАНИИ")
    filter_input = input(
        "Введите ключевые слова для поиска в описании через запятую (или Enter чтобы пропустить): ").strip()

    filter_words = []
    if filter_input:
        filter_words = [word.strip() for word in filter_input.split(",") if word.strip()]
        print(f"🔑 Ключевые слова: {filter_words}")

    filtered_vacancies = filter_vacancies(vacancies_list, filter_words)

    if not filtered_vacancies:
        print("📭 После фильтрации по ключевым словам вакансий не осталось.")
        return []

    print(f"✅ После фильтрации осталось: {len(filtered_vacancies)}")

    # 6. Фильтрация по зарплате
    print("\n💰 ФИЛЬТРАЦИЯ ПО ЗАРПЛАТЕ")
    print("   Форматы: '100000', '100000-150000', 'от 100000', 'до 150000'")
    salary_range = input("Введите диапазон зарплат (или Enter чтобы пропустить): ").strip()

    ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)

    if not ranged_vacancies:
        print("📭 После фильтрации по зарплате вакансий не осталось.")
        return []

    print(f"✅ После фильтрации по зарплате: {len(ranged_vacancies)}")

    # 7. Сортировка и выбор топ-N
    print("\n🏆 СОРТИРОВКА И ВЫБОР ТОП-ВАКАНСИЙ")

    while True:
        try:
            top_n_input = input("Сколько топ-вакансий показать? (Enter для всех): ").strip()

            if not top_n_input:
                top_n = len(ranged_vacancies)
                print("📊 Показываю все вакансии:")
                break

            top_n = int(top_n_input)
            if top_n <= 0:
                print("❌ Число должно быть больше 0. Попробуйте снова.")
                continue

            print(f"📊 Показываю топ-{top_n} вакансий:")
            break

        except ValueError:
            print("❌ Пожалуйста, введите число или нажмите Enter.")

    top_vacancies = get_top_vacancies(ranged_vacancies, top_n)

    # 8. Вывод результатов
    print_vacancies(top_vacancies)

    return top_vacancies


def user_interaction() -> None:
    """Главная функция приложения - точка входа"""

    print("═" * 50)
    print("🎯 ПРИЛОЖЕНИЕ ДЛЯ ПОИСКА ВАКАНСИЙ")
    print("═" * 50)

    json_saver = JSONSaver()  # По умолчанию: vacancies.json
    hh_api = HeadHunterAPI()

    print(f"\n💾 Все вакансии будут сохраняться в файл: {json_saver.filename}")

    while True:
        print("\n" + "═" * 50)
        print("📋 ГЛАВНОЕ МЕНЮ")
        print("═" * 50)

        # Показываем статистику
        saved_count = len(json_saver.get_vacancies())
        print(f"💾 В файле сохранено: {saved_count} вакансий")

        print("\n1. 🔍 НОВЫЙ ПОИСК ВАКАНСИЙ")
        print("2. 📋 ПОКАЗАТЬ СОХРАНЁННЫЕ ВАКАНСИИ")
        print("3. 🗑️  УДАЛИТЬ ВАКАНСИЮ")
        print("4. 🧹 ОЧИСТИТЬ ФАЙЛ")
        print("5. 👋 ВЫЙТИ")

        choice = input("\n👉 Ваш выбор (1-5): ").strip()

        if choice == "1":
            # ВЫБОР ПЛАТФОРМЫ ДЛЯ ПОИСКА
            print("\n" + "─" * 50)
            print("📱 ВЫБЕРИТЕ ПЛАТФОРМУ ДЛЯ ПОИСКА:")
            print("  1. HeadHunter (hh.ru)")
            print("  2. SuperJob (в разработке)")
            print("  3. 🔙 Назад")

            try:
                platform_choice = int(input("👉 Ваш выбор: "))
            except ValueError:
                print("❌ Введите число")
                continue

            if platform_choice == 1:
                # HeadHunter
                found_vacancies = perform_hh_search(hh_api)

                if found_vacancies:
                    # Предлагаем сохранить
                    print("\n💾 СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
                    save_choice = input("Сохранить найденные вакансии? (да/нет): ").strip().lower()

                    if save_choice in ['да', 'д', 'yes', 'y']:
                        saved_count = 0
                        already_existed = 0

                        for vacancy in found_vacancies:
                            if not json_saver.is_vacancy_saved(vacancy.url):
                                json_saver.add_vacancy(vacancy)
                                saved_count += 1
                            else:
                                already_existed += 1

                        print(f"✅ Сохранено новых вакансий: {saved_count}")
                        if already_existed > 0:
                            print(f"📌 Уже было в файле: {already_existed}")
                        print(f"💾 Файл: {json_saver.filename}")

                input("\nНажмите Enter чтобы вернуться в меню...")

            elif platform_choice == 2:
                print("❌ SuperJob пока не поддерживается")
                input("\nНажмите Enter чтобы продолжить...")

            elif platform_choice == 3:
                continue
            else:
                print("❌ Неверный выбор")

        elif choice == "2":
            show_saved_vacancies(json_saver)

        elif choice == "3":
            delete_vacancy_menu(json_saver)

        elif choice == "4":
            clear_file_menu(json_saver)

        elif choice == "5":
            print("\n👋 До свидания!")
            print(f"💾 Все ваши вакансии сохранены в файле: {json_saver.filename}")
            break

        else:
            print("❌ Неверный выбор")


# Запускаем программу
if __name__ == "__main__":
    user_interaction()



# 1. Спросить у пользователя:
#    - Что искать? (search_query)
#    - Сколько показать? (top_n)
#    - Какие ключевые слова? (filter_words)
#    - Какой диапазон зарплат? (salary_range)

# 2. Использовать твои классы:
#    api = HeadHunterAPI()
#    raw_data = api.get_vacancies(search_query)

# 3. Преобразовать данные:
#    vacancies = Vacancy.cast_to_object_list(raw_data)

# 4. Применить фильтры (твои функции):
#    filtered = filter_vacancies(vacancies, filter_words)
#    filtered_by_salary = get_vacancies_by_salary(filtered, salary_range)

# 5. Отсортировать:
#    sorted_vac = sort_vacancies(filtered_by_salary)

# 6. Взять топ-N:
#    top = get_top_vacancies(sorted_vac, top_n)

# 7. Показать:
#    print_vacancies(top)

# 8. Сохранить (опционально):
#    saver = JSONSaver()
#    for vacancy in top:
#        saver.add_vacancy(vacancy)
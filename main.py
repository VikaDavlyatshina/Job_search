from src.api import HeadHunterAPI
from src.utils import *


# Вспомогательные функции
def show_saved_vacancies(saver: JSONSaver):
    """Показывает сохранённые вакансии"""
    saved = saver.get_vacancies()

    if not saved:
        print("📭 В файле нет сохранённых вакансий")
        return

    print(f"\n📁 СОХРАНЕНО ВАКАНСИЙ: {len(saved)}")

    # Показываем с номерами для выбора
    for i, vacancy in enumerate(saved[:20], 1):  # Первые 20
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
    print("\n🗑️  УДАЛЕНИЕ ВАКАНСИИ")
    print("1. Удалить по URL")
    print("2. Выбрать из списка")
    print("3. Назад")

    choice = input("👉 Ваш выбор (1-3): ").strip()

    if choice == "1":
        url = input("Введите URL вакансии: ").strip()
        if saver.delete_vacancy_by_url(url):  # ← НУЖНО ДОБАВИТЬ ЭТОТ МЕТОД!
            print("✅ Вакансия удалена")
        else:
            print("❌ Вакансия не найдена")

    elif choice == "2":
        # Показываем список для выбора
        saved = saver.get_vacancies()
        if saved:
            show_saved_vacancies(saver)  # Показываем список
            try:
                num = int(input("\nВведите номер вакансии для удаления: "))
                if 1 <= num <= len(saved):
                    # Получаем вакансию по номеру
                    vacancy_to_delete = saved[num - 1]
                    # Нужен метод delete_vacancy_by_url
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



def user_interaction() -> None:
    """Главная функция приложения Поиск вакансий.
    Связывает между собой все функциональности"""

    print("═" * 50)
    print("🎉 Привет, добро пожаловать в приложение Для поиска вакансий!")
    print("═" * 50)

    while True:
        # 1. Выбор платформы
        print("\n" + "─" * 50)
        print("📱 ВЫБЕРИТЕ ПЛАТФОРМУ ДЛЯ ПОИСКА:")
        print("  1. SuperJob (пока не доступно)")
        print("  2. HeadHunter (hh.ru)")


        try:
            user_choice = int(input("👉 Ваш выбор (Введите число ): "))

        except ValueError:
            print("❌ Пожалуйста, введите число")
            continue

        if user_choice == 1:
            print("❌ SuperJob пока не поддерживается. Используем HeadHunter.")

        if user_choice == 2:
            # 1. Создаем экземпляры классов
            hh_api = HeadHunterAPI()
            json_saver = JSONSaver()

            print("\n" + "─" * 50)
            print("🔍 ПОИСКОВЫЙ ЗАПРОС")

            # 2. Получаем поисковый запрос
            search_query = input("Введите поисковый запрос (например: 'Python разработчик'): ").strip()

            if not search_query:
                print("❌ Поисковый запрос не может быть пустым!")
                continue   # Продолжаем цикл

            print("\n🏙️  ВЫБОР ГОРОДА")
            city = input("Введите город (или Enter для поиска по России): ").strip()

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

            # 3. Получаем вакансии API
            print(f"\n📡 Ищем вакансии по запросу: '{search_query}'...")
            try:
                hh_vacancies_data = hh_api.get_vacancies(
                    keyword=search_query,
                    max_pages=max_pages,
                    city=city if city else None
                )
                vacancies_list = Vacancy.cast_to_object_list(hh_vacancies_data)

                if not vacancies_list:
                    print(f"📭 По запросу '{search_query}' вакансий не найдено.")
                    continue

                print(f"✅ Найдено вакансий: {len(vacancies_list)}")

            except Exception as e:
                print(f"❌ Ошибка при получении вакансий: {e}")
                return

            # 4. Фильтрация по ключевым словам
            print("\n🔍 ФИЛЬТРАЦИЯ ПО КЛЮЧЕВЫМ СЛОВАМ")
            filter_input = input("Введите ключевые слова для поиска через запятую (или Enter чтобы пропустить): ").strip()

            filter_words = []
            if filter_input:
                filter_words = [word.strip() for word in filter_input.split(",") if word.strip()]
                print(f"🔑 Ключевые слова: {filter_words}")

            filtered_vacancies = filter_vacancies(vacancies_list, filter_words)

            if not filtered_vacancies:
                print("📭 После фильтрации по ключевым словам вакансий не осталось.")
                continue

            print(f"✅ После фильтрации осталось: {len(filtered_vacancies)}")

            # 5. Фильтрация по зарплате
            print("\n💰 ФИЛЬТРАЦИЯ ПО ЗАРПЛАТЕ")
            print("   Форматы: '100000', '100000-150000', 'от 100000', 'до 150000'")
            salary_range = input("Введите диапазон зарплат (или Enter чтобы пропустить): ").strip()

            ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)

            if not ranged_vacancies:
                print("📭 После фильтрации по зарплате вакансий не осталось.")
                return

            print(f"✅ После фильтрации по зарплате: {len(ranged_vacancies)}")

            # 6. Сортировка и выбор топ-N
            print("\n🏆 СОРТИРОВКА И ВЫБОР ТОП-ВАКАНСИЙ")

            while True:
                try:
                    top_n_input = input("Сколько топ-вакансий показать? (Enter для всех): ").strip()

                    if not top_n_input:  # Если Enter - показываем все
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

            # 7. Вывод результатов

            print_vacancies(top_vacancies)

            # 8. Сохранение результатов в файл
            print("\n💾  СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
            save_choice = input("Сохранить результаты в файл? (да/нет): ").strip().lower()

            if save_choice in ['да', 'д', 'yes', 'y']:
                try:
                    saved_count = 0
                    already_existed = 0

                    for vacancy in top_vacancies:

                        if not json_saver.is_vacancy_saved(vacancy.url):
                            json_saver.add_vacancy(vacancy)
                            saved_count += 1
                        else:
                            already_existed += 1

                    print(f"✅ Сохранено новых вакансий: {saved_count}")
                    if already_existed > 0:
                        print(f"📌 Уже было в файле: {already_existed}")
                    print(f"💾 Файл: {json_saver.filename}")

                except Exception as e:
                    print(f"❌ Ошибка при сохранении: {e}")

            print("═" * 50)
            print("1. 🔍 Новый поиск вакансий")
            print("2. 📋 Показать сохранённые вакансии")
            print("3. 🗑️  Удалить вакансию")
            print("4. 🧹 Очистить файл")
            print("5. 👋 Выйти")

            choice = input("\n👉 Ваш выбор (1-5): ").strip()

            if choice == "1":
                continue  # НОВЫЙ ПОИСК
            elif choice == "2":
                show_saved_vacancies(json_saver)
            elif choice == "3":
                delete_vacancy_menu(json_saver)
            elif choice == "4":
                clear_file_menu(json_saver)
            elif choice == "5":
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор")


            # 9. Завершение
            print("\n" + "=" * 60)
            print("🎉 ПОИСК ЗАВЕРШЕН УСПЕШНО!")
            print("=" * 60)



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
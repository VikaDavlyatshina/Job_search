from src.vacancy import Vacancy
from src.api import HeadHunterAPI
from src.storage import JSONSaver
from src.utils import *





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
                return

            # 3. Получаем вакансии API
            print(f"\n📡 Ищем вакансии по запросу: '{search_query}'...")
            try:
                hh_vacancies_data = hh_api.get_vacancies(search_query)
                vacancies_list = Vacancy.cast_to_object_list(hh_vacancies_data)

                if not vacancies_list:
                    print(f"📭 По запросу '{search_query}' вакансий не найдено.")
                    return

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
                return

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
                    for vacancy in top_vacancies:
                        json_saver.add_vacancy(vacancy)
                    print(f"✅ Результаты сохранены в файл: {json_saver.filename}")
                except Exception as e:
                    print(f"❌ Ошибка при сохранении: {e}")
            else:
                print("📄 Результаты не сохранены.")

            continue_search = input("\n🔍 Хотите выполнить новый поиск? (да/нет): ").strip().lower()
            if continue_search not in ['да', 'д', 'yes', 'y']:
                print("\n👋 До свидания!")
                break


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
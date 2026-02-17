from typing import List, Optional, Tuple

from src.database import DBCreator
from src.db_manager import DBManager

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========


def format_salary(sal_from: Optional[int], sal_to: Optional[int], currency: Optional[str]) -> str:
    """Форматирование зарплаты для вывода"""
    if sal_from and sal_to:
        return f"{sal_from:,} - {sal_to:,} {currency or 'руб.'}"
    elif sal_from:
        return f"от {sal_from:,} {currency or 'руб.'}"
    elif sal_to:
        return f"до {sal_to:,} {currency or 'руб.'}"
    else:
        return "зарплата не указана"


def print_header(title: str, symbol: str = "═", length: int = 50) -> None:
    """Печатает красивый заголовок"""
    print(f"\n{symbol * length}")
    print(f"{title}")
    print(f"{symbol * length}")


def wait_for_enter() -> None:
    """Ждет нажатия Enter"""
    input("\nНажмите Enter чтобы продолжить...")


# ========== ОСНОВНЫЕ ФУНКЦИИ ДЛЯ БД ==========


def setup_database() -> None:
    """Создание и заполнение базы данных"""
    print_header("🗄️  НАСТРОЙКА БАЗЫ ДАННЫХ", "═")

    creator = DBCreator()

    creator.fill_database(force_recreate=True)

    print_header("✅ БАЗА ДАННЫХ ГОТОВА К РАБОТЕ", "═")


def show_companies_stats() -> None:
    """1. Статистика по компаниям"""
    db = DBManager()
    print_header("📊 СТАТИСТИКА ПО КОМПАНИЯМ", "═")

    companies = db.get_companies_and_vacancies_count()

    if not companies:
        print("📭 В базе данных нет компаний")
        db.close()
        return

    print(f"\nВсего компаний: {len(companies)}")
    print("\n📋 Компании и количество вакансий:")
    print("-" * 40)

    for company, count in companies:
        print(f"• {company}: {count} вакансий")

    db.close()


def show_avg_salary() -> None:
    """3. Средняя зарплата"""
    db = DBManager()
    print_header("💰 СРЕДНЯЯ ЗАРПЛАТА", "═")

    avg = db.get_avg_salary()

    if avg > 0:
        print(f"\nСредняя зарплата по всем вакансиям: {avg:,.2f} руб.")
    else:
        print("\n📭 Нет данных о зарплатах")

    db.close()


def show_higher_salary_vacancies() -> None:
    """4. Вакансии выше средней"""
    db = DBManager()
    print_header("📈 ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ", "═")

    avg = db.get_avg_salary()
    if avg == 0:
        print("\n📭 Нет данных о средней зарплате")
        db.close()
        return

    vacancies = db.get_vacancies_with_higher_salary()

    if not vacancies:
        print(f"\n📭 Нет вакансий с зарплатой выше средней ({avg:,.2f} руб.)")
        db.close()
        return

    print(f"\nСредняя зарплата: {avg:,.2f} руб.")
    print(f"Найдено вакансий: {len(vacancies)}")
    print("\n" + "-" * 60)

    for company, title, sal_from, sal_to, curr, url in vacancies[:15]:
        salary = format_salary(sal_from, sal_to, curr)

        def get_vacancy_avg(s_from: Optional[int], s_to: Optional[int]) -> float:
            if s_from is not None and s_to is not None:
                return (s_from + s_to) / 2.0
            elif s_from is not None:
                return float(s_from)
            elif s_to is not None:
                return float(s_to)
            else:
                return 0.0

        vac_avg = get_vacancy_avg(sal_from, sal_to)

        if vac_avg == 0:
            continue  # пропускаем вакансии без зарплаты

        diff_percent = ((vac_avg / avg) - 1) * 100
        print(f"\n• {company}: {title}")
        print(f"  {salary} (выше на {diff_percent:.1f}%)")
        print(f"  {url}")

    if len(vacancies) > 15:
        print(f"\n... и еще {len(vacancies) - 15} вакансий")

    db.close()


def search_vacancies_in_db() -> None:
    """5. Поиск по ключевому слову"""
    keyword = input("\n🔍 Введите ключевое слово для поиска: ").strip()

    if not keyword:
        print("❌ Ключевое слово не может быть пустым")
        return

    db = DBManager()
    print_header(f"🔎 ПОИСК: '{keyword}'", "═")

    vacancies = db.get_vacancies_with_keyword(keyword)

    if not vacancies:
        print(f"\n📭 Вакансий с '{keyword}' не найдено")
        db.close()
        return

    print(f"\n✅ Найдено вакансий: {len(vacancies)}")
    print("\n" + "-" * 60)

    for company, title, sal_from, sal_to, curr, url in vacancies[:15]:
        salary = format_salary(sal_from, sal_to, curr)
        print(f"\n• {company}: {title}")
        print(f"  {salary}")
        print(f"  {url}")

    if len(vacancies) > 15:
        print(f"\n... и еще {len(vacancies) - 15} вакансий")

    db.close()


def show_all_companies_preview() -> None:
    """
    2. Обзор всех компаний (по 15 вакансий)
    """
    print_header("🏢 ОБЗОР ВСЕХ КОМПАНИЙ (ПО 15 ВАКАНСИЙ)", "═")

    db = DBManager()

    try:
        companies = db.get_companies_and_vacancies_count()

        if not companies:
            print("📭 В базе данных нет компаний")
            return

        print(f"\n📊 Всего компаний в базе: {len(companies)}")

        for company_idx, (company_name, total_vacancies) in enumerate(companies, 1):
            print(f"\n{company_idx}. 🏢 {company_name}")
            print(f"   Всего вакансий: {total_vacancies}")
            print(f"   {'─' * 50}")

            vacancies = db.get_vacancies_by_employer(company_name)

            if not vacancies:
                print("   📭 Нет данных о вакансиях")
                continue

            preview_count = min(15, len(vacancies))
            for i, (_, title, sal_from, sal_to, curr, url) in enumerate(vacancies[:preview_count], 1):
                salary = format_salary(sal_from, sal_to, curr)
                title_display = title[:50] + "..." if len(title) > 50 else title
                print(f"   {i:2}. {title_display}")
                print(f"       Зарплата: {salary}")

            if len(vacancies) > preview_count:
                print(f"       ... и еще {len(vacancies) - preview_count} вакансий")

        print("\n" + "═" * 60)
        choice = input(
            "\n💡 Хотите посмотреть полный список вакансий какой-либо компании?\n"
            "   Введите номер или название (Enter чтобы пропустить): "
        ).strip()

        if choice:
            show_selected_company_full(choice, companies)

    # Закрываем соединение
    finally:
        db.close()


def show_selected_company_full(choice: str, companies: List[Tuple], db: Optional[DBManager] = None) -> None:
    """Показывает все вакансии выбранной компании"""
    should_close = False
    if db is None:
        db = DBManager()
        should_close = True

    company_name = None

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(companies):
            company_name = companies[idx][0]
            print(f"\n✓ Выбрана компания: {company_name}")
        else:
            print(f"\n❌ Нет компании с номером {choice}")
            if should_close:
                db.close()
            return
    else:
        company_name = choice

    all_vacancies = db.get_vacancies_by_employer(company_name)

    if not all_vacancies:
        print(f"\n📭 Вакансий для компании '{company_name}' не найдено")
        if should_close:
            db.close()
        return

    total = len(all_vacancies)
    print_header(f"🏢 {all_vacancies[0][0]} - ВСЕ ВАКАНСИИ ({total})", "═")

    # Постраничный вывод
    page_size = 20
    total_pages = (total + page_size - 1) // page_size

    for page in range(total_pages):
        start = page * page_size
        end = min(start + page_size, total)

        print(f"\n--- Страница {page + 1} из {total_pages} ---")
        print("-" * 60)

        for i, (_, title, sal_from, sal_to, curr, url) in enumerate(all_vacancies[start:end], start + 1):
            salary = format_salary(sal_from, sal_to, curr)
            print(f"\n{i}. {title}")
            print(f"   Зарплата: {salary}")
            print(f"   Ссылка: {url}")

        if page < total_pages - 1:
            nav = input("\nEnter - далее, 'q' - выйти: ").strip().lower()
            if nav == "q":
                break

    _show_company_statistics(all_vacancies)

    if should_close:
        db.close()


def _show_company_statistics(vacancies: List[Tuple]) -> None:
    """Внутренняя функция для статистики по компании"""
    total = len(vacancies)
    with_salary = 0
    salary_sum = 0
    salary_list = []

    for vac in vacancies:
        sal_from = vac[2]
        sal_to = vac[3]

        if sal_from or sal_to:
            with_salary += 1

            if sal_from and sal_to:
                avg = (sal_from + sal_to) / 2
            elif sal_from:
                avg = sal_from
            else:
                avg = sal_to

            salary_sum += avg
            salary_list.append(avg)

    print(f"\n{'─' * 60}")
    print("📊 ПОЛНАЯ СТАТИСТИКА ПО КОМПАНИИ:")
    print(f"{'─' * 60}")
    print(f"   • Всего вакансий: {total}")
    print(f"   • Вакансий с указанной зарплатой: {with_salary}")

    if salary_list:
        salary_list.sort()
        avg_salary = salary_sum / with_salary
        median = salary_list[len(salary_list) // 2]

        print(f"   • Средняя зарплата: {avg_salary:,.2f} руб.")
        print(f"   • Медианная зарплата: {median:,.2f} руб.")
        print(f"   • Минимальная зарплата: {min(salary_list):,.2f} руб.")
        print(f"   • Максимальная зарплата: {max(salary_list):,.2f} руб.")

        above_avg = sum(1 for s in salary_list if s > avg_salary)
        if above_avg > 0:
            percent = (above_avg / with_salary) * 100
            print(f"   • Выше средней: {above_avg} ({percent:.1f}%)")
    else:
        print("   • Нет данных о зарплатах")


def show_database_menu() -> None:
    """Главное меню для работы с БД"""
    while True:
        print_header("🗄️  МЕНЮ РАБОТЫ С БАЗОЙ ДАННЫХ", "─")
        print("\n1. 📊 Статистика по компаниям")
        print("2. 🏢 Обзор всех компаний (по 15 вакансий)")
        print("3. 💰 Средняя зарплата")
        print("4. 📈 Вакансии выше средней")
        print("5. 🔍 Поиск по ключевому слову")
        print("6. 🔄 Обновить базу данных")
        print("7. 🔙 Назад")

        choice = input("\n👉 Ваш выбор (1-7): ").strip()

        if choice == "1":
            show_companies_stats()
        elif choice == "2":
            show_all_companies_preview()
        elif choice == "3":
            show_avg_salary()
        elif choice == "4":
            show_higher_salary_vacancies()
        elif choice == "5":
            search_vacancies_in_db()
        elif choice == "6":
            print("\n⚠️  ВНИМАНИЕ: Все данные будут перезаписаны!")
            confirm = input("Продолжить? (да/нет): ").strip().lower()
            if confirm in ["да", "д", "yes", "y"]:
                setup_database()
        elif choice == "7":
            break
        else:
            print("❌ Неверный выбор")

        if choice in ["1", "2", "3", "4", "5"]:
            wait_for_enter()

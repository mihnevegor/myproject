import os
import sys
from database import init_db
import auth
import duties
from colors import COLORS, get_color_by_date

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_window(title, lines, width=64):
    print(COLORS["WHITE_ON_GREY"] + "╔" + "═" * (width - 2) + "╗")
    print(f"║{title.center(width - 2)}║")
    print("╠" + "═" * (width - 2) + "╣")
    for line in lines:
        # Убираем влияние ANSI кодов на подсчет длины строки
        clean_line = line.replace(COLORS["WHITE_ON_GREY"], "").replace(COLORS["RESET"], "")
        for c in COLORS.values():
            clean_line = clean_line.replace(c, "")
        padding = width - 4 - len(clean_line)
        print(f"║ {line}" + " " * padding + " ║")
    print("╚" + "═" * (width - 2) + "╝" + COLORS["RESET"])

def show_login_screen():
    clear_screen()
    lines = [
        "",
        "Для входа в систему введите данные аккаунта:",
        "",
        "Доступные тестовые аккаунты:",
        "  - Логин: admin | Пароль: admin123  (Полные права)",
        "  - Логин: user1 | Пароль: user123  (Только просмотр)",
        ""
    ]
    draw_window("ОКНО ВХОДА (LOGIN)", lines)
    
    login = input("\nВведите Логин ➔ ").strip()
    password = input("Введите Пароль ➔ ").strip()
    
    if auth.login_user(login, password):
        return True
    else:
        print(COLORS["RED"] + "\n[Ошибка] Неверный логин или пароль!" + COLORS["RESET"])
        input("Нажмите Enter для повтора...")
        return False

def show_dashboard():
    current_view_mode = "Все дежурства"
    filtered_items = None
    
    while True:
        clear_screen()
        all_items = duties.get_all_duties()
        display_items = all_items if filtered_items is None else filtered_items
        
        window_lines = [
            f"Текущий пользователь: {auth.current_user.login} [{auth.current_user.role.upper()}]",
            f"Режим просмотра: {current_view_mode}",
            "─" * 60,
            f"{'ID':<4} | {'ФИО Дежурного':<22} | {'Кабинет':<8} | {'Дата/Время'}",
            "─" * 60
        ]
        
        for d in display_items:
            color = get_color_by_date(d.datetime_str)
            fio = f"{d.first_name} {d.last_name}"
            row_str = f"{color}{d.id:<4} | {fio:<22} | {d.room:<8} | {d.datetime_str}{COLORS['WHITE_ON_GREY']}"
            window_lines.append(row_str)
            
        window_lines.extend([
            "─" * 60,
            "ОБЩИЕ КОМАНДЫ:",
            " 1. Показать все            2. Сортировать по времени",
            " 3. Фильтр по дате (> указанной)  4. Фильтр по месяцу",
            " 5. Фильтр по времени"
        ])
        
        if auth.current_user.role == "admin":
            window_lines.extend([
                "─" * 60,
                "УПРАВЛЕНИЕ ДЛЯ АДМИНИСТРАТОРА:",
                " 6. Добавить дежурство      7. Удалить дежурство"
            ])
            
        window_lines.extend([
            "─" * 60,
            " 0. Выйти из аккаунта"
        ])
        
        draw_window("ГЛАВНОЕ ОКНО СИСТЕМЫ ДЕЖУРСТВ", window_lines, width=66)
        
        choice = input("\nВыберите номер команды ➔ ").strip()
        
        if choice == "0":
            auth.logout()
            break
        elif choice == "1":
            filtered_items = None
            current_view_mode = "Все дежурства"
        elif choice == "2":
            filtered_items = duties.sort_by_time(display_items)
            current_view_mode = "Отсортировано по времени"
        elif choice == "3":
            date_in = input("Введите дату (ГГГГММДД, например 20261005): ").strip()
            filtered_items = duties.filter_by_date(all_items, date_in)
            current_view_mode = f"После даты {date_in}"
        elif choice == "4":
            month_in = input("Введите месяц (ГГГГММ, например 202610): ").strip()
            filtered_items = duties.filter_by_month(all_items, month_in)
            current_view_mode = f"За месяц {month_in}"
        elif choice == "5":
            time_in = input("Введите время (ЧЧ:ММ, например 14:00): ").strip()
            filtered_items = duties.filter_by_time(all_items, time_in)
            current_view_mode = f"Точное время {time_in}"
        elif choice == "6" and auth.current_user.role == "admin":
            clear_screen()
            print("=== ДОБАВЛЕНИЕ ДЕЖУРСТВА ===")
            fn = input("Имя: ").strip()
            ln = input("Фамилия: ").strip()
            room = input("Кабинет: ").strip()
            dt = input("Время (ГГГГММДД ЧЧ:ММ, например 20261005 14:00): ").strip()
            if fn and ln and room and dt:
                duties.add_duty(fn, ln, room, dt)
                print(COLORS["GREEN"] + "Успешно добавлено!" + COLORS["RESET"])
            else:
                print(COLORS["RED"] + "Ошибка: поля пусты!" + COLORS["RESET"])
            input("Enter для возврата...")
        elif choice == "7" and auth.current_user.role == "admin":
            try:
                d_id = int(input("Введите ID дежурства для удаления ➔ "))
                duties.delete_duty(d_id)
                print(COLORS["GREEN"] + "Успешно удалено!" + COLORS["RESET"])
                if filtered_items:
                    filtered_items = [d for d in filtered_items if d.id != d_id]
            except ValueError:
                print(COLORS["RED"] + "Неверный формат ID!" + COLORS["RESET"])
            input("Enter для возврата...")

def main():
    init_db()
    while True:
        if not auth.current_user:
            show_login_screen()
        else:
            show_dashboard()

if __name__ == "__main__":
    main()

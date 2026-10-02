import tkinter as tk
from tkinter import messagebox, ttk
from database import init_db
import auth
import duties
from colors import get_color_by_date

# Перевод цветов ANSI в HEX для графического интерфейса Windows
HEX_COLORS = {
    "\033[91m": "#FFD2D2",  # Понедельник — Светло-красный
    "\033[38;5;208m": "#FFE4C4",  # Вторник — Оранжевый/Бежевый
    "\033[93m": "#FFFFE0",  # Среда — Светло-желтый
    "\033[92m": "#E0FFE0",  # Четверг — Светло-зеленый
    "\033[96m": "#E0FFFF",  # Пятница — Салатовый/Циан
    "\033[90m": "#F0F0F0",  # Выходные — Серый
    "\033[0m": "#FFFFFF"   # По умолчанию — Белый
}

class DutyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система контроля дежурств")
        self.root.geometry("750x500")
        self.root.resizable(False, False)
        
        init_db()
        self.show_login_screen()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_root()
        
        # Контейнер формы авторизации
        frame = tk.LabelFrame(self.root, text=" ОКНО ВХОДА (LOGIN) ", font=("Arial", 12, "bold"), padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=280)
        
        tk.Label(frame, text="Для входа в систему введите данные аккаунта:", font=("Arial", 10)).pack(pady=5)
        
        tk.Label(frame, text="Логин:").pack(anchor="w", pady=2)
        self.login_entry = tk.Entry(frame, font=("Arial", 10))
        self.login_entry.pack(fill="x", pady=2)
        
        tk.Label(frame, text="Пароль:").pack(anchor="w", pady=2)
        self.pass_entry = tk.Entry(frame, show="*", font=("Arial", 10))
        self.pass_entry.pack(fill="x", pady=2)
        
        tk.Button(frame, text="Войти в систему", command=self.handle_login, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=15)
        
        tk.Label(frame, text="Тестовые данные: admin / admin123 или user1 / user123", font=("Arial", 8), fg="gray").pack()

    def handle_login(self):
        login = self.login_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if auth.login_user(login, password):
            self.show_dashboard()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def show_dashboard(self):
        self.clear_root()
        self.current_view_mode = "Все дежурства"
        self.filtered_items = None
        
        # Верхняя информационная панель
        top_frame = tk.Frame(self.root, bg="#ECEFF1", pady=5, padx=10)
        top_frame.pack(fill="x")
        
        user_info = f"Пользователь: {auth.current_user.login} [{auth.current_user.role.upper()}]"
        tk.Label(top_frame, text=user_info, font=("Arial", 10, "bold"), bg="#ECEFF1").pack(side="left")
        
        self.view_label = tk.Label(top_frame, text=f"Режим: {self.current_view_mode}", font=("Arial", 10), bg="#ECEFF1", fg="#555")
        self.view_label.pack(side="right")
        
        # Главный контейнер для таблицы дежурств
        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.pack(fill="both", expand=True)
        
        # Настройка таблицы отображения (Treeview)
        columns = ("id", "fio", "room", "datetime")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("fio", text="ФИО Дежурного")
        self.tree.heading("room", text="Кабинет")
        self.tree.heading("datetime", text="Дата / Время")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fio", width=250, anchor="w")
        self.tree.column("room", width=100, anchor="center")
        self.tree.column("datetime", width=180, anchor="center")
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Панель управления (Кнопки команд)
        btn_frame = tk.LabelFrame(self.root, text=" Панель управления командами ", padx=10, pady=5)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="Показать все", command=self.refresh_all).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Сортировать по времени", command=self.sort_data).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Фильтр по дате", command=self.filter_date).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(btn_frame, text="Фильтр по месяцу", command=self.filter_month).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(btn_frame, text="Фильтр по времени", command=self.filter_time).grid(row=0, column=4, padx=5, pady=5)
        
        if auth.current_user.role == "admin":
            tk.Button(btn_frame, text="Добавить", command=self.open_add_window, bg="#BBDEFB").grid(row=1, column=0, padx=5, pady=5, sticky="we")
            tk.Button(btn_frame, text="Удалить", command=self.delete_item, bg="#FFCDD2").grid(row=1, column=1, padx=5, pady=5, sticky="we")
            
        tk.Button(btn_frame, text="Выйти из аккаунта", command=self.show_login_screen, bg="#B0BEC5").grid(row=1, column=4, padx=5, pady=5, sticky="we")
        
        self.load_table_data()

    def load_table_data(self):
        # Очищаем таблицу перед выводом
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        all_items = duties.get_all_duties()
        display_items = all_items if self.filtered_items is None else self.filtered_items
        
        for d in display_items:
            fio = f"{d.first_name} {d.last_name}"
            ansi_color = get_color_by_date(d.datetime_str)
            hex_bg = HEX_COLORS.get(ansi_color, "#FFFFFF")
            
            # Регистрируем тег цвета для закрашивания строки таблицы
            tag_name = f"tag_{d.id}"
            self.tree.insert("", "end", values=(d.id, fio, d.room, d.datetime_str), tags=(tag_name,))
            self.tree.tag_configure(tag_name, background=hex_bg)
            
        self.view_label.config(text=f"Режим: {self.current_view_mode}")

    def refresh_all(self):
        self.filtered_items = None
        self.current_view_mode = "Все дежурства"
        self.load_table_data()

    def sort_data(self):
        items = duties.get_all_duties() if self.filtered_items is None else self.filtered_items
        self.filtered_items = duties.sort_by_time(items)
        self.current_view_mode = "Отсортировано по времени"
        self.load_table_data()

    def filter_date(self):
        # Простое диалоговое окно ввода в Tkinter
        dialog = tk.Toplevel(self.root)
        dialog.title("Фильтр")
        dialog.geometry("300x120")
        tk.Label(dialog, text="Введите дату (ГГГГММДД):").pack(pady=5)
        entry = tk.Entry(dialog)
        entry.pack(pady=5)
        
        def apply():
            val = entry.get().strip()
            if val:
                self.filtered_items = duties.filter_by_date(duties.get_all_duties(), val)
                self.current_view_mode = f"После даты {val}"
                self.load_table_data()
            dialog.destroy()
            
        tk.Button(dialog, text="Применить", command=apply).pack(pady=5)

    def filter_month(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Фильтр")
        dialog.geometry("300x120")
        tk.Label(dialog, text="Введите месяц (ГГГГММ):").pack(pady=5)
        entry = tk.Entry(dialog)
        entry.pack(pady=5)
        
        def apply():
            val = entry.get().strip()
            if val:
                self.filtered_items = duties.filter_by_month(duties.get_all_duties(), val)
                self.current_view_mode = f"За месяц {val}"
                self.load_table_data()
            dialog.destroy()
            
        tk.Button(dialog, text="Применить", command=apply).pack(pady=5)

    def filter_time(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Фильтр")
        dialog.geometry("300x120")
        tk.Label(dialog, text="Введите точное время (ЧЧ:ММ):").pack(pady=5)
        entry = tk.Entry(dialog)
        entry.pack(pady=5)
        
        def apply():
            val = entry.get().strip()
            if val:
                self.filtered_items = duties.filter_by_time(duties.get_all_duties(), val)
                self.current_view_mode = f"Точное время {val}"
                self.load_table_data()
            dialog.destroy()
            
        tk.Button(dialog, text="Применить", command=apply).pack(pady=5)

    def open_add_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Добавление дежурства")
        add_win.geometry("350x300")
        
        tk.Label(add_win, text="Имя:").pack(anchor="w", padx=10)
        e_fn = tk.Entry(add_win)
        e_fn.pack(fill="x", padx=10, pady=2)
        
        tk.Label(add_win, text="Фамилия:").pack(anchor="w", padx=10)
        e_ln = tk.Entry(add_win)
        e_ln.pack(fill="x", padx=10, pady=2)
        
        tk.Label(add_win, text="Кабинет:").pack(anchor="w", padx=10)
        e_room = tk.Entry(add_win)
        e_room.pack(fill="x", padx=10, pady=2)
        
        tk.Label(add_win, text="Дата и время (ГГГГММДД ЧЧ:ММ):").pack(anchor="w", padx=10)
        e_dt = tk.Entry(add_win)
        e_dt.insert(0, "20261005 14:00")
        e_dt.pack(fill="x", padx=10, pady=2)
        
        def save():
            fn, ln, rm, dt = e_fn.get().strip(), e_ln.get().strip(), e_room.get().strip(), e_dt.get().strip()
            if fn and ln and rm and dt:
                duties.add_duty(fn, ln, rm, dt)
                self.refresh_all()
                add_win.destroy()
            else:
                messagebox.showwarning("Внимание", "Заполните все поля!")
                
        tk.Button(add_win, text="Сохранить", command=save, bg="#4CAF50", fg="white").pack(pady=15, fill="x", padx=10)

    def delete_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Выбор", "Выберите строку в таблице для удаления!")
            return
            
        item_values = self.tree.item(selected_item, "values")
        d_id = int(item_values[0])
        
        if messagebox.askyesno("Подтверждение", f"Удалить дежурство с ID {d_id}?"):
            duties.delete_duty(d_id)
            self.refresh_all()

if __name__ == "__main__":
    root = tk.Tk()
    app = DutyApp(root)
    root.mainloop()
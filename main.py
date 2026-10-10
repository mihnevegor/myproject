import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from database import init_db
import auth
import duties
from colors import COLORS, get_color_by_date

HEX_COLORS = {
    "\033[91m": "#FFD2D2",       # Понедельник
    "\033[38;5;208m": "#FFE4C4", # Вторник
    "\033[93m": "#FFFFE0",       # Среда
    "\033[92m": "#E0FFE0",       # Четверг
    "\033[96m": "#E0FFFF",       # Пятница
    "\033[90m": "#F0F0F0",       # Выходные
    "\033[0m": "#FFFFFF"
}

CONFIG_FILE = "config.txt"

def load_saved_credentials():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if len(lines) >= 2:
                    return lines[0], lines[1], True
        except:
            pass
    return "", "", False

def save_credentials(login, password, remember):
    try:
        if remember:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(f"{login}\n{password}")
        else:
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
    except:
        pass

def format_datetime_str(raw_dt):
    parts = raw_dt.strip().split()
    if len(parts) != 2:
        return raw_dt
    date_part, time_part = parts[0], parts[1]
    if ":" in time_part:
        h, m = time_part.split(":")
        return f"{date_part} {int(h):02d}:{int(m):02d}"
    return raw_dt

def format_time_only(raw_t):
    if ":" in raw_t:
        h, m = raw_t.strip().split(":")
        return f"{int(h):02d}:{int(m):02d}"
    return raw_t

class DutyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система контроля дежурств")
        self.root.geometry("900x530")
        self.root.resizable(False, False)
        init_db()
        self.show_login_screen()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_root()
        frame = tk.LabelFrame(self.root, text=" ОКНО ВХОДА (LOGIN) ", font=("Arial", 12, "bold"), padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=420, height=340)
        
        saved_login, saved_pass, is_saved = load_saved_credentials()
        
        tk.Label(frame, text="Введите данные аккаунта:").pack(pady=5)
        tk.Label(frame, text="Логин:").pack(anchor="w")
        self.login_entry = tk.Entry(frame, font=("Arial", 10))
        self.login_entry.insert(0, saved_login)
        self.login_entry.pack(fill="x", pady=2)
        
        tk.Label(frame, text="Пароль:").pack(anchor="w")
        
        pass_frame = tk.Frame(frame)
        pass_frame.pack(fill="x", pady=2)
        
        self.pass_entry = tk.Entry(pass_frame, show="*", font=("Arial", 10))
        self.pass_entry.insert(0, saved_pass)
        self.pass_entry.pack(side="left", fill="x", expand=True)
        
        self.btn_show_pass = tk.Button(pass_frame, text="👁", width=3, command=self.toggle_password, bg="#E0E0E0")
        self.btn_show_pass.pack(side="right", padx=2)
        
        self.remember_var = tk.BooleanVar(value=is_saved)
        tk.Checkbutton(frame, text="Запомнить меня (сохранить пароль)", variable=self.remember_var).pack(anchor="w", pady=10)
        
        tk.Button(frame, text="Войти в систему", command=self.handle_login, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=5)

    def toggle_password(self):
        if self.pass_entry.cget("show") == "*":
            self.pass_entry.config(show="")
            self.btn_show_pass.config(bg="#BDBDBD")
        else:
            self.pass_entry.config(show="*")
            self.btn_show_pass.config(bg="#E0E0E0")

    def handle_login(self):
        login = self.login_entry.get().strip()
        password = self.pass_entry.get().strip()
        remember = self.remember_var.get()
        
        if auth.login_user(login, password):
            save_credentials(login, password, remember)
            self.show_dashboard()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def show_dashboard(self):
        self.clear_root()
        self.current_view_mode = "Все дежурства"
        self.filtered_items = None
        
        top_frame = tk.Frame(self.root, bg="#ECEFF1", pady=5, padx=10)
        top_frame.pack(fill="x")
        
        tk.Label(top_frame, text=f"Пользователь: {auth.current_user.login} [{auth.current_user.role.upper()}]", font=("Arial", 10, "bold"), bg="#ECEFF1").pack(side="left")
        self.view_label = tk.Label(top_frame, text=f"Режим: {self.current_view_mode}", bg="#ECEFF1", fg="#555")
        self.view_label.pack(side="right")
        
        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.pack(fill="both", expand=True)
        
        columns = ("id", "fio", "room", "datetime_start", "time_end")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=11)
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("fio", text="ФИО Дежурного")
        self.tree.heading("room", text="Кабинет")
        self.tree.heading("datetime_start", text="Начало (Дата / Время)")
        self.tree.heading("time_end", text="Окончание (Время)")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("fio", width=260, anchor="w")
        self.tree.column("room", width=80, anchor="center")
        self.tree.column("datetime_start", width=160, anchor="center")
        self.tree.column("time_end", width=130, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        btn_frame = tk.LabelFrame(self.root, text=" Панель управления командами ", padx=10, pady=5)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="Показать все", command=self.refresh_all).grid(row=0, column=0, padx=4, pady=5)
        tk.Button(btn_frame, text="Сортировать по времени", command=self.sort_data).grid(row=0, column=1, padx=4, pady=5)
        tk.Button(btn_frame, text="Сортировать по ФИО", command=self.sort_data_fio).grid(row=0, column=2, padx=4, pady=5)
        tk.Button(btn_frame, text="Сортировать по кабинету", command=self.sort_data_room).grid(row=0, column=3, padx=4, pady=5)
        
        tk.Button(btn_frame, text="Фильтр по дате", command=self.filter_date).grid(row=0, column=4, padx=4, pady=5)
        tk.Button(btn_frame, text="Фильтр по месяцу", command=self.filter_month).grid(row=0, column=5, padx=4, pady=5)
        tk.Button(btn_frame, text="Фильтр по времени", command=self.filter_time).grid(row=0, column=6, padx=4, pady=5)
        
        if auth.current_user.role == "admin":
            tk.Button(btn_frame, text="Добавить", command=self.open_add_window, bg="#BBDEFB").grid(row=1, column=0, padx=4, pady=5, sticky="we")
            tk.Button(btn_frame, text="Редактировать", command=self.open_edit_window, bg="#FFE0B2").grid(row=1, column=1, padx=4, pady=5, sticky="we")
            tk.Button(btn_frame, text="Удалить", command=self.delete_item, bg="#FFCDD2").grid(row=1, column=2, padx=4, pady=5, sticky="we")
            
        tk.Button(btn_frame, text="Выйти из аккаунта", command=self.show_login_screen, bg="#B0BEC5").grid(row=1, column=6, padx=4, pady=5, sticky="we")
        self.load_table_data()

    def load_table_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        all_items = duties.get_all_duties()
        display_items = all_items if self.filtered_items is None else self.filtered_items
        
        for d in display_items:
            fio = f"{d.last_name} {d.first_name} {d.middle_name}".strip()
            ansi_color = get_color_by_date(d.datetime_str)
            hex_bg = HEX_COLORS.get(ansi_color, "#FFFFFF")
            tag_name = f"tag_{d.id}"
            self.tree.insert("", "end", values=(d.id, fio, d.room, d.datetime_str, d.time_end), tags=(tag_name,))
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

    def sort_data_fio(self):
        items = duties.get_all_duties() if self.filtered_items is None else self.filtered_items
        self.filtered_items = duties.sort_by_fio(items)
        self.current_view_mode = "Отсортировано по ФИО"
        self.load_table_data()

    def sort_data_room(self):
        items = duties.get_all_duties() if self.filtered_items is None else self.filtered_items
        self.filtered_items = duties.sort_by_room(items)
        self.current_view_mode = "Отсортировано по кабинету"
        self.load_table_data()

    def filter_date(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Фильтр по дате")
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
        dialog.title("Фильтр по месяцу")
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
        dialog.title("Фильтр по времени")
        dialog.geometry("300x120")
        tk.Label(dialog, text="Введите точное время (ЧЧ:ММ):").pack(pady=5)
        entry = tk.Entry(dialog)
        entry.pack(pady=5)
        
        def apply():
            val = format_time_only(entry.get().strip())
            if val:
                self.filtered_items = duties.filter_by_time(duties.get_all_duties(), val)
                self.current_view_mode = f"Точное время {val}"
                self.load_table_data()
            dialog.destroy()
        tk.Button(dialog, text="Применить", command=apply).pack(pady=5)

    def validate_inputs(self, fn, ln, mn, rm, dt, te):
        if not (fn and ln and rm and dt and te):
            messagebox.showwarning("Внимание", "Заполните обязательные поля (Имя, Фамилия, Кабинет, Время)!")
            return False
        
        for name_field, name_label in [(fn, "Имя"), (ln, "Фамилия"), (mn, "Отчество")]:
            if name_field and not name_field.replace("-", "").isalpha():
                messagebox.showerror("Ошибка", f"Поле '{name_label}' должно содержать только буквы!")
                return False
        
        try:
            start_dt = datetime.strptime(dt, "%Y%m%d %H:%M")
            end_t = datetime.strptime(te, "%H:%M")
            
            start_time_only = start_dt.time()
            end_time_only = end_t.time()
            
            if end_time_only <= start_time_only:
                messagebox.showerror("Ошибка валидации времени", "Время окончания не может быть меньше или равно времени начала дежурства!")
                return False
                
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат времени (24-часовой формат ГГГГММДД ЧЧ:ММ и ЧЧ:ММ)!")
            return False
        return True

    def open_add_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Добавление дежурства")
        add_win.geometry("360x410")
        add_win.resizable(False, False)
        
        tk.Label(add_win, text="Фамилия:").pack(anchor="w", padx=10)
        e_ln = tk.Entry(add_win); e_ln.pack(fill="x", padx=10)
        tk.Label(add_win, text="Имя:").pack(anchor="w", padx=10)
        e_fn = tk.Entry(add_win); e_fn.pack(fill="x", padx=10)
        tk.Label(add_win, text="Отчество (если есть):").pack(anchor="w", padx=10)
        e_mn = tk.Entry(add_win); e_mn.pack(fill="x", padx=10)
        
        tk.Label(add_win, text="Кабинет:").pack(anchor="w", padx=10)
        e_room = tk.Entry(add_win); e_room.pack(fill="x", padx=10)
        tk.Label(add_win, text="Начало (ГГГГММДД ЧЧ:ММ):").pack(anchor="w", padx=10)
        e_dt = tk.Entry(add_win); e_dt.insert(0, "20261005 14:00"); e_dt.pack(fill="x", padx=10)
        tk.Label(add_win, text="Окончание (ЧЧ:ММ):").pack(anchor="w", padx=10)
        e_te = tk.Entry(add_win); e_te.insert(0, "18:00"); e_te.pack(fill="x", padx=10)
        
        def save():
            fn, ln, mn, rm = e_fn.get().strip(), e_ln.get().strip(), e_mn.get().strip(), e_room.get().strip()
            dt = format_datetime_str(e_dt.get())
            te = format_time_only(e_te.get())
            
            if self.validate_inputs(fn, ln, mn, rm, dt, te):
                duties.add_duty(fn, ln, mn, rm, dt, te)
                self.refresh_all()
                add_win.destroy()
        tk.Button(add_win, text="Сохранить", command=save, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=12, fill="x", padx=10)

    def open_edit_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выбор", "Выберите строку для редактирования!")
            return
        
        item_vals = self.tree.item(selected, "values")
        d_id = int(item_vals[0])
        fio_parts = item_vals[1].split()
        
        old_ln = fio_parts[0] if len(fio_parts) > 0 else ""
        old_fn = fio_parts[1] if len(fio_parts) > 1 else ""
        old_mn = fio_parts[2] if len(fio_parts) > 2 else ""
        
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Редактирование ID {d_id}")
        edit_win.geometry("360x410")
        edit_win.resizable(False, False)
        
        tk.Label(edit_win, text="Фамилия:").pack(anchor="w", padx=10)
        e_ln = tk.Entry(edit_win); e_ln.insert(0, old_ln); e_ln.pack(fill="x", padx=10)
        tk.Label(edit_win, text="Имя:").pack(anchor="w", padx=10)
        e_fn = tk.Entry(edit_win); e_fn.insert(0, old_fn); e_fn.pack(fill="x", padx=10)
        tk.Label(edit_win, text="Отчество:").pack(anchor="w", padx=10)
        e_mn = tk.Entry(edit_win); e_mn.insert(0, old_mn); e_mn.pack(fill="x", padx=10)
        
        tk.Label(edit_win, text="Кабинет:").pack(anchor="w", padx=10)
        e_room = tk.Entry(edit_win); e_room.insert(0, item_vals[2]); e_room.pack(fill="x", padx=10)
        tk.Label(edit_win, text="Начало (ГГГГММДД ЧЧ:ММ):").pack(anchor="w", padx=10)
        e_dt = tk.Entry(edit_win); e_dt.insert(0, item_vals[3]); e_dt.pack(fill="x", padx=10)
        tk.Label(edit_win, text="Окончание (ЧЧ:ММ):").pack(anchor="w", padx=10)
        e_te = tk.Entry(edit_win); e_te.insert(0, item_vals[4]); e_te.pack(fill="x", padx=10)
        
        def save_changes():
            fn, ln, mn, rm = e_fn.get().strip(), e_ln.get().strip(), e_mn.get().strip(), e_room.get().strip()
            dt = format_datetime_str(e_dt.get())
            te = format_time_only(e_te.get())
            
            if self.validate_inputs(fn, ln, mn, rm, dt, te):
                duties.edit_duty(d_id, fn, ln, mn, rm, dt, te)
                self.refresh_all()
                edit_win.destroy()
        tk.Button(edit_win, text="Сохранить изменения", command=save_changes, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(pady=12, fill="x", padx=10)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выбор", "Выберите строку для удаления!")
            return
        d_id = int(self.tree.item(selected, "values")[0])
        if messagebox.askyesno("Подтверждение", f"Удалить дежурство с ID {d_id}?"):
            duties.delete_duty(d_id)
            self.refresh_all()

if __name__ == "__main__":
    root = tk.Tk()
    app = DutyApp(root)
    root.mainloop()

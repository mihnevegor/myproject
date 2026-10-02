from database import get_connection
from models import User

current_user = None

def login_user(login, password):
    global current_user
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, login, password, role FROM users WHERE login = ? AND password = ?", 
            (login, password)
        )
        row = cursor.fetchone()
        if row:
            # Исправлено: передаем элементы кортежа по индексам
            current_user = User(row[0], row[1], row[2], row[3])
            return True
        return False

def logout():
    global current_user
    current_user = None

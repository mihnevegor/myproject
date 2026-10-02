import sqlite3

DB_NAME = "duty.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        
        # Таблица дежурств
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS duties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                room TEXT NOT NULL,
                datetime_str TEXT NOT NULL
            )
        """)
        
        # Создание предустановленных аккаунтов, если таблица пуста
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            accounts = [
                ("admin", "admin123", "admin"),
                ("user1", "user123", "user"),
                ("user2", "user123", "user")
            ]
            cursor.executemany(
                "INSERT INTO users (login, password, role) VALUES (?, ?, ?)", 
                accounts
            )
        conn.commit()
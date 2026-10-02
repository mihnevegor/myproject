from database import get_connection
from models import Duty

def add_duty(first_name, last_name, room, datetime_str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO duties (first_name, last_name, room, datetime_str) VALUES (?, ?, ?, ?)",
            (first_name, last_name, room, datetime_str)
        )
        conn.commit()

def get_all_duties():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, room, datetime_str FROM duties")
        return [Duty(*row) for row in cursor.fetchall()]

def delete_duty(duty_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM duties WHERE id = ?", (duty_id,))
        conn.commit()

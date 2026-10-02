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

def sort_by_time(duties_list):
    return sorted(duties_list, key=lambda d: d.datetime_str)

def filter_by_date(duties_list, target_date):
    return [d for d in duties_list if d.datetime_str.split()[0] > target_date]

def filter_by_month(duties_list, target_month):
    return [d for d in duties_list if d.datetime_str.startswith(target_month)]

def filter_by_time(duties_list, target_time):
    return [d for d in duties_list if len(d.datetime_str.split()) > 1 and d.datetime_str.split()[1] == target_time]

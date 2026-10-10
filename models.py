class User:
    def __init__(self, user_id, login, password, role):
        self.id = user_id
        self.login = login
        self.password = password
        self.role = role

class Duty:
    def __init__(self, duty_id, first_name, last_name, middle_name, room, datetime_str, time_end):
        self.id = duty_id
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name  # Добавлено отчество
        self.room = room
        self.datetime_str = datetime_str  # Начало: YYYYMMDD HH:MM
        self.time_end = time_end          # Окончание: HH:MM

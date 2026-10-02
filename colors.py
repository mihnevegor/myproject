from datetime import datetime

# ANSI-коды для раскраски текста в консоли
COLORS = {
    "RESET": "\033[0m",
    "WHITE_ON_GREY": "\033[37;48;5;240m",
    "RED": "\033[91m",
    "ORANGE": "\033[38;5;208m",
    "YELLOW": "\033[93m",
    "GREEN": "\033[92m",
    "SALAT": "\033[96m",
    "GREY": "\033[90m",
}

def get_color_by_date(datetime_str):
    try:
        # Разбиваем строку "20261005 14:00" на дату и время, берем только дату
        date_part = datetime_str.split()[0]
        dt = datetime.strptime(date_part, "%Y%m%d")
        wd = dt.weekday()  # 0 = Понедельник, 6 = Воскресенье
        
        if wd == 0: return COLORS["RED"]
        if wd == 1: return COLORS["ORANGE"]
        if wd == 2: return COLORS["YELLOW"]
        if wd == 3: return COLORS["GREEN"]
        if wd == 4: return COLORS["SALAT"]
        return COLORS["GREY"]
    except:
        return COLORS["RESET"]

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, cast, Date
from datetime import datetime, timedelta
from collections import defaultdict
from app.models.session import Session


def get_heatmap_data(db: Session, user_id: int, year: int = None) -> dict:
    """Данные для GitHub-style календаря: { '2026-05-20': {'count': 3, 'minutes': 75} }"""
    if year is None:
        year = datetime.now().year

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)

    sessions = db.query(Session).filter(
        Session.user_id == user_id,
        Session.start_time >= start_date,
        Session.start_time <= end_date
    ).all()

    result = defaultdict(lambda: {"count": 0, "minutes": 0})
    for s in sessions:
        date_key = s.start_time.date().isoformat()
        result[date_key]["count"] += 1
        result[date_key]["minutes"] += round(s.duration_minutes)

    return dict(result)


def get_weekly_stats(db: Session, user_id: int, weeks: int = 12) -> list:
    """Статистика по неделям для линейного графика"""
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)

    sessions = db.query(Session).filter(
        Session.user_id == user_id,
        Session.start_time >= start_date
    ).all()

    weekly = defaultdict(lambda: {"sessions": 0, "minutes": 0})
    for s in sessions:
        week = s.start_time.isocalendar()[1]
        year_week = f"{s.start_time.year}-W{week:02d}"
        weekly[year_week]["sessions"] += 1
        weekly[year_week]["minutes"] += round(s.duration_minutes)

    return [{"week": k, **v} for k, v in sorted(weekly.items())]


def get_streaks(db: Session, user_id: int) -> dict:
    """Текущая и лучшая серия дней с сессиями"""
    sessions = db.query(Session).filter(
        Session.user_id == user_id
    ).order_by(Session.start_time.desc()).all()

    if not sessions:
        return {"current": 0, "best": 0, "last_session": None}

    # Получаем уникальные даты с сессиями
    dates = sorted(set(s.start_time.date() for s in sessions), reverse=True)

    # Текущая серия
    current = 0
    today = datetime.now().date()
    for i, date in enumerate(dates):
        if i == 0 and date == today:
            current = 1
        elif i == 0 and date == today - timedelta(days=1):
            current = 1
        elif i > 0 and date == dates[i - 1] - timedelta(days=1):
            current += 1
        elif i > 0:
            break

    # Лучшая серия
    best = 0
    temp = 1
    for i in range(1, len(dates)):
        if dates[i] == dates[i - 1] - timedelta(days=1):
            temp += 1
            best = max(best, temp)
        else:
            temp = 1
    best = max(best, 1 if dates else 0)

    return {
        "current": current,
        "best": best,
        "last_session": dates[0].isoformat() if dates else None
    }


def get_productivity_stats(db: Session, user_id: int) -> dict:
    """Продуктивность по дням недели и часам"""
    sessions = db.query(Session).filter(Session.user_id == user_id).all()

    by_day = defaultdict(lambda: {"count": 0, "minutes": 0})
    by_hour = defaultdict(lambda: {"count": 0, "minutes": 0})

    for s in sessions:
        day_name = s.start_time.strftime("%A")  # Monday, Tuesday...
        hour = s.start_time.hour
        by_day[day_name]["count"] += 1
        by_day[day_name]["minutes"] += round(s.duration_minutes)
        by_hour[hour]["count"] += 1
        by_hour[hour]["minutes"] += round(s.duration_minutes)

    # Порядок дней недели
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_day_ordered = {d: by_day.get(d, {"count": 0, "minutes": 0}) for d in day_order}

    return {
        "by_day": by_day_ordered,
        "by_hour": dict(sorted(by_hour.items()))
    }


def get_achievements(db: Session, user_id: int) -> list:
    """Список достижений пользователя"""
    sessions = db.query(Session).filter(Session.user_id == user_id).all()
    achievements = []

    if sessions:
        total_minutes = sum(s.duration_minutes for s in sessions)
        total_sessions = len(sessions)
        first_date = min(s.start_time.date() for s in sessions)
        days_active = len(set(s.start_time.date() for s in sessions))

        # Достижения
        if total_sessions >= 1:
            achievements.append(
                {"id": "first_session", "name": "🎯 Первая сессия", "desc": "Начал учиться!", "unlocked": True})
        if total_sessions >= 10:
            achievements.append(
                {"id": "ten_sessions", "name": "🔟 Десять сессий", "desc": "Уже 10 раз сел за учёбу!", "unlocked": True})
        if total_minutes >= 100:
            achievements.append(
                {"id": "hundred_minutes", "name": "⏱ 100 минут", "desc": "Целых 100 минут обучения!", "unlocked": True})
        if total_minutes >= 500:
            achievements.append(
                {"id": "five_hours", "name": "🏆 5 часов", "desc": "Получил 5 часов знаний!", "unlocked": True})
        if days_active >= 7:
            achievements.append({"id": "week_warrior", "name": "📅 Неделя активности", "desc": "Учился в 7 разных дней!",
                                 "unlocked": True})
        if any(s.focus_score >= 9 for s in sessions):
            achievements.append(
                {"id": "master_focus", "name": "🧘 Мастер фокуса", "desc": "Оценил сессию на 9-10!", "unlocked": True})

    return achievements
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.goal import Goal
from app.models.session import Session
from app.schemas.goal import GoalCreate, GoalResponse
from datetime import datetime


def create_goal(db: Session, goal_data: GoalCreate, user_id: int) -> GoalResponse:
    """Создаёт цель и возвращает ответ с рассчитанными полями"""
    goal = Goal(**goal_data.model_dump(), user_id=user_id)
    db.add(goal)
    db.commit()
    db.refresh(goal)

    # Возвращаем сразу рассчитанный ответ
    return GoalResponse(
        id=goal.id,
        title=goal.title,
        target_minutes=goal.target_minutes,
        achieved_minutes=0.0,  # только что создана
        progress_percent=0.0,
        deadline=goal.deadline,
        is_active=goal.is_active,
        created_at=goal.created_at
    )


def get_user_goals(db: Session, user_id: int) -> list[GoalResponse]:
    """Получает цели пользователя с рассчитанным прогрессом"""
    goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.is_active == True).all()
    result = []

    for g in goals:
        # Считаем прогресс: сумма минут сессий с момента создания цели
        achieved = db.query(func.sum(Session.duration_minutes)).filter(
            Session.user_id == user_id,
            Session.start_time >= g.created_at,
            Session.start_time <= (g.deadline or datetime.now())
        ).scalar() or 0.0

        progress = min((achieved / g.target_minutes) * 100, 100.0) if g.target_minutes > 0 else 0

        result.append(GoalResponse(
            id=g.id,
            title=g.title,
            target_minutes=g.target_minutes,
            achieved_minutes=round(achieved, 1),
            progress_percent=round(progress, 1),
            deadline=g.deadline,
            is_active=g.is_active,
            created_at=g.created_at
        ))

    return result


def toggle_goal(db: Session, goal_id: int, user_id: int) -> GoalResponse:
    """Переключает активный статус цели"""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        return None

    goal.is_active = not goal.is_active
    db.commit()
    db.refresh(goal)

    # Возвращаем с рассчитанным прогрессом
    achieved = db.query(func.sum(Session.duration_minutes)).filter(
        Session.user_id == user_id,
        Session.start_time >= goal.created_at
    ).scalar() or 0.0
    progress = min((achieved / goal.target_minutes) * 100, 100.0) if goal.target_minutes > 0 else 0

    return GoalResponse(
        id=goal.id,
        title=goal.title,
        target_minutes=goal.target_minutes,
        achieved_minutes=round(achieved, 1),
        progress_percent=round(progress, 1),
        deadline=goal.deadline,
        is_active=goal.is_active,
        created_at=goal.created_at
    )
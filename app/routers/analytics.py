from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.analytics_service import (
    get_heatmap_data, get_weekly_stats, get_streaks,
    get_productivity_stats, get_achievements
)

router = APIRouter(prefix="/analytics", tags=["Аналитика"])

@router.get("/heatmap")
def heatmap(
    year: int = Query(None, description="Год для календаря"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_heatmap_data(db, current_user.id, year)

@router.get("/weekly")
def weekly(
    weeks: int = Query(12, ge=1, le=52),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_weekly_stats(db, current_user.id, weeks)

@router.get("/streaks")
def streaks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_streaks(db, current_user.id)

@router.get("/productivity")
def productivity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_productivity_stats(db, current_user.id)

@router.get("/achievements")
def achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_achievements(db, current_user.id)
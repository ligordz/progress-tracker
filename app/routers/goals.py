from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.goal import GoalCreate, GoalResponse
from app.services.goal_service import create_goal, get_user_goals, toggle_goal
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/goals", tags=["Цели"])

@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_new_goal(goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_goal(db, goal, current_user.id)

@router.get("/", response_model=list[GoalResponse])
def list_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_goals(db, current_user.id)

@router.post("/{goal_id}/toggle", response_model=GoalResponse)
def toggle_goal_status(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = toggle_goal(db, goal_id, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    return updated
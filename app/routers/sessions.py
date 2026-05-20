from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.services.session_service import create_session, get_user_sessions, update_session, delete_session, clear_user_sessions
from app.core.auth import get_current_user
from app.models.user import User
from app.models.session import Session  # ← важно для работы запросов

router = APIRouter(prefix="/sessions", tags=["Учебные сессии"])

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_new_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_session(db, session_data, current_user.id)

@router.get("/", response_model=list[SessionResponse])
def list_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_sessions(db, current_user.id, skip, limit)

@router.post("/clear", status_code=status.HTTP_200_OK)
def clear_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted_count = clear_user_sessions(db, current_user.id)
    return {"message": f"Удалено {deleted_count} сессий", "count": deleted_count}


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(Session).filter(Session.id == session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return session

@router.put("/{session_id}", response_model=SessionResponse)
def edit_session(
    session_id: int,
    update_data: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = update_session(db, session_id, current_user.id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return updated

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)  # ← ЭТО БЫЛО ПРОПУЩЕНО!
def remove_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not delete_session(db, session_id, current_user.id):
        raise HTTPException(status_code=404, detail="Сессия не найдена")
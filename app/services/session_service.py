from sqlalchemy.orm import Session
from datetime import datetime
from app.models.session import Session, Tag
from app.schemas.session import SessionCreate, SessionUpdate


def create_session(db: Session, session_data: SessionCreate, user_id: int) -> Session:
    duration = (session_data.end_time - session_data.start_time).total_seconds() / 60

    db_session = Session(
        user_id=user_id,
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        duration_minutes=round(duration, 2),
        focus_score=session_data.focus_score,
        note=session_data.note,
        goal=session_data.goal
    )

    if session_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(session_data.tag_ids)).all()
        db_session.tags = tags

    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_user_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list:
    return db.query(Session).filter(Session.user_id == user_id).offset(skip).limit(limit).all()


def update_session(db: Session, session_id: int, user_id: int, update_data: SessionUpdate) -> Session:
    db_session = db.query(Session).filter(Session.id == session_id, Session.user_id == user_id).first()
    if not db_session:
        return None

    for field, value in update_data.model_dump(exclude_unset=True).items():
        if field == "tag_ids" and value is not None:
            tags = db.query(Tag).filter(Tag.id.in_(value)).all()
            db_session.tags = tags
        elif hasattr(db_session, field):
            setattr(db_session, field, value)

    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: int, user_id: int) -> bool:
    db_session = db.query(Session).filter(Session.id == session_id, Session.user_id == user_id).first()
    if not db_session:
        return False
    db.delete(db_session)
    db.commit()
    return True


def clear_user_sessions(db: Session, user_id: int) -> int:
    deleted_count = db.query(Session).filter(Session.user_id == user_id).delete()
    db.commit()
    return deleted_count
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, func, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Таблица многие-ко-многим для сессий и тегов
session_tags = Table(
    "session_tags", Base.metadata,
    Column("session_id", Integer, ForeignKey("sessions.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    color = Column(String, default="#3498db")  # HEX-цвет для UI

    sessions = relationship("Session", secondary=session_tags, back_populates="tags")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Float, nullable=False)  # рассчитывается автоматически

    focus_score = Column(Integer, default=5)  # 1-10, оценка концентрации
    note = Column(String, nullable=True)  # заметка о сессии
    goal = Column(String, nullable=True)  # цель сессии

    created_at = Column(DateTime, server_default=func.now())

    # Связи
    tags = relationship("Tag", secondary=session_tags, back_populates="sessions")
    user = relationship("User", back_populates="sessions")

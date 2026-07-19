from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(240))
    project: Mapped[str | None] = mapped_column(String(120), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(240))
    event_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="forest")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(240), default="Untitled")
    content: Mapped[str] = mapped_column(Text, default="")
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    icon: Mapped[str] = mapped_column(String(12), default="📝")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(240))
    summary: Mapped[str] = mapped_column(String(500), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(80), default="General")
    tags: Mapped[str] = mapped_column(String(500), default="")
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentFolder(Base):
    __tablename__ = "document_folders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentFile(Base):
    __tablename__ = "document_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(240))
    original_name: Mapped[str] = mapped_column(String(240))
    url: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size: Mapped[int] = mapped_column(Integer, default=0)
    folder_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Publication(Base):
    __tablename__ = "publications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    authors: Mapped[str] = mapped_column(String(500), default="")
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str] = mapped_column(String(240), default="")
    abstract: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(String(500), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    description: Mapped[str] = mapped_column(String(240))
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(80), default="Other")
    expense_date: Mapped[date] = mapped_column(Date)
    notes: Mapped[str] = mapped_column(String(500), default="")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(String(500), default="")
    language: Mapped[str] = mapped_column(String(60), default="Other")
    visibility: Mapped[str] = mapped_column(String(20), default="Private")
    deployed_url: Mapped[str] = mapped_column(String(500), default="")
    repository_url: Mapped[str] = mapped_column(String(500), default="")
    readme: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Habit(Base):
    __tablename__ = "habits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    frequency: Mapped[str] = mapped_column(String(20), default="daily")
    color: Mapped[str] = mapped_column(String(20), default="forest")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HabitLog(Base):
    __tablename__ = "habit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    habit_id: Mapped[int] = mapped_column(Integer)
    completed_date: Mapped[date] = mapped_column(Date)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(240), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(300))
    github_username: Mapped[str | None] = mapped_column(String(160), nullable=True)
    github_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    openai_api_key: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

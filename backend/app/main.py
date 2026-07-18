from datetime import date
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import Base, engine
from app import models  # noqa: F401 - registers ORM models
from app.routers.tasks import router as tasks_router
from app.routers.calendar import router as calendar_router
from app.routers.notes import router as notes_router
from app.routers.uploads import router as uploads_router
from app.routers.knowledge import router as knowledge_router
from app.routers.documents import router as documents_router
from app.routers.publications import router as publications_router
from app.routers.finance import router as finance_router
from app.routers.ai import router as ai_router
from app.routers.projects import router as projects_router
from app.routers.habits import router as habits_router
from app.routers.analytics import router as analytics_router
from app.routers.settings import router as settings_router
from app.routers.auth import router as auth_router
from app.routers.github import router as github_router
from app.database import SessionLocal
from app.config import settings
from app.models import CalendarEvent, Expense, Publication, Task, User
from app.routers.auth import current_user
from sqlalchemy import String, func, select, text

app = FastAPI(title="Personal OS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
if settings.database_url.startswith("sqlite"):
    with engine.begin() as connection:
        for table in ("tasks", "calendar_events", "notes", "knowledge_articles", "document_folders", "document_files", "publications", "expenses", "projects", "habits", "habit_logs"):
            columns = {row[1] for row in connection.execute(text(f"PRAGMA table_info({table})"))}
            if "owner_id" not in columns:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN owner_id INTEGER"))
        user_columns = {row[1] for row in connection.execute(text("PRAGMA table_info(users)"))}
        if "github_username" not in user_columns: connection.execute(text("ALTER TABLE users ADD COLUMN github_username VARCHAR(160)"))
        if "github_token" not in user_columns: connection.execute(text("ALTER TABLE users ADD COLUMN github_token VARCHAR(500)"))
app.include_router(tasks_router)
app.include_router(calendar_router)
app.include_router(notes_router)
app.include_router(uploads_router)
app.include_router(knowledge_router)
app.include_router(documents_router)
app.include_router(publications_router)
app.include_router(finance_router)
app.include_router(ai_router)
app.include_router(projects_router)
app.include_router(habits_router)
app.include_router(analytics_router)
app.include_router(settings_router)
app.include_router(auth_router)
app.include_router(github_router)
Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "personal-os-api"}


@app.get("/api/v1/dashboard")
def dashboard(user: User = Depends(current_user)) -> dict:
    db = SessionLocal(); today = date.today(); month = today.strftime("%Y-%m")
    try:
        open_tasks = db.scalars(select(Task).where(Task.owner_id == user.id, Task.completed.is_(False)).order_by(Task.due_date, Task.id.desc()).limit(5)).all()
        completed = db.scalar(select(func.count(Task.id)).where(Task.owner_id == user.id, Task.completed.is_(True))) or 0
        spending = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.owner_id == user.id, Expense.expense_date.cast(String).like(f"{month}%"))) or 0
        events = db.scalar(select(func.count(CalendarEvent.id)).where(CalendarEvent.owner_id == user.id, CalendarEvent.event_date >= today)) or 0
        publications = db.scalar(select(func.count(Publication.id)).where(Publication.owner_id == user.id)) or 0
        return {"tasks": {"open": len(open_tasks), "completed": completed, "items": [{"id": t.id, "title": t.title, "project": t.project, "due_date": t.due_date.isoformat() if t.due_date else None} for t in open_tasks]}, "finance": {"month_total": float(spending)}, "calendar": {"upcoming": events}, "publications": publications}
    finally: db.close()

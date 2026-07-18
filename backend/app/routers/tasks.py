from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Task
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    project: str | None = Field(default=None, max_length=120)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    project: str | None = Field(default=None, max_length=120)
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    due_date: date | None = None
    completed: bool | None = None


class TaskRead(TaskCreate):
    id: int
    completed: bool

    model_config = {"from_attributes": True}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.scalars(select(Task).where(Task.owner_id == user.id).order_by(Task.completed, Task.due_date, Task.id.desc())).all()


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    task = Task(**payload.model_dump(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    task = db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for name, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, name, value)
    db.commit()
    db.refresh(task)
    return task

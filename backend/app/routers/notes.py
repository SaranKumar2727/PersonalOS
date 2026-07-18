from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Note
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


class NoteCreate(BaseModel):
    title: str = Field(default="Untitled", min_length=1, max_length=240)
    content: str = ""
    parent_id: int | None = None
    icon: str = Field(default="📝", max_length=12)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    content: str | None = None
    parent_id: int | None = None
    icon: str | None = Field(default=None, max_length=12)


class NoteRead(NoteCreate):
    id: int
    updated_at: datetime
    model_config = {"from_attributes": True}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.scalars(select(Note).where(Note.owner_id == user.id).order_by(Note.updated_at.desc())).all()


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    note = Note(**payload.model_dump(), owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    note = db.scalar(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    if not note:
        raise HTTPException(status_code=404, detail="Page not found")
    for name, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, name, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    note = db.scalar(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    if not note:
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete(note)
    db.commit()

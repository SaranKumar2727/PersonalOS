from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import String, cast, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import CalendarEvent
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/calendar/events", tags=["calendar"])


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    event_date: date
    start_time: str | None = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    color: str = Field(default="forest", pattern="^(forest|purple|orange|blue)$")


class EventRead(EventCreate):
    id: int
    model_config = {"from_attributes": True}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[EventRead])
def list_events(month: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    statement = select(CalendarEvent).where(CalendarEvent.owner_id == user.id).order_by(CalendarEvent.event_date, CalendarEvent.start_time)
    if month:
        statement = statement.where(cast(CalendarEvent.event_date, String).like(f"{month}%"))
    return db.scalars(statement).all()


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    event = CalendarEvent(**payload.model_dump(), owner_id=user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    event = db.scalar(select(CalendarEvent).where(CalendarEvent.id == event_id, CalendarEvent.owner_id == user.id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()

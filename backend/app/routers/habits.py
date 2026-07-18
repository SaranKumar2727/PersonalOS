from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Habit, HabitLog
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/habits", tags=["habits"])
class HabitCreate(BaseModel): name: str = Field(min_length=1, max_length=160); frequency: str = "daily"; color: str = "forest"
class HabitRead(HabitCreate):
    id: int; completed_today: bool; streak: int; week_done: int
    model_config = {"from_attributes": True}
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
def view(habit: Habit, db: Session):
    today=date.today(); dates=set(db.scalars(select(HabitLog.completed_date).where(HabitLog.habit_id==habit.id)).all()); streak=0; cursor=today
    while cursor in dates: streak+=1; cursor-=timedelta(days=1)
    return {**habit.__dict__, 'completed_today':today in dates, 'streak':streak, 'week_done':sum((today-timedelta(days=i)) in dates for i in range(7))}
@router.get("", response_model=list[HabitRead])
def list_habits(db: Session=Depends(get_db), user: User=Depends(current_user)):
    return [view(habit,db) for habit in db.scalars(select(Habit).where(Habit.owner_id == user.id).order_by(Habit.id)).all()]
@router.post("", response_model=HabitRead, status_code=status.HTTP_201_CREATED)
def create_habit(payload: HabitCreate, db: Session=Depends(get_db), user: User=Depends(current_user)):
    habit=Habit(**payload.model_dump(), owner_id=user.id);db.add(habit);db.commit();db.refresh(habit);return view(habit,db)
@router.post("/{habit_id}/toggle", response_model=HabitRead)
def toggle_habit(habit_id:int, db:Session=Depends(get_db), user: User=Depends(current_user)):
    habit=db.scalar(select(Habit).where(Habit.id == habit_id, Habit.owner_id == user.id))
    if not habit: raise HTTPException(status_code=404,detail="Habit not found")
    today=date.today(); log=db.scalar(select(HabitLog).where(HabitLog.habit_id==habit_id,HabitLog.completed_date==today))
    if log: db.delete(log)
    else: db.add(HabitLog(habit_id=habit_id,owner_id=user.id,completed_date=today))
    db.commit();return view(habit,db)
@router.delete("/{habit_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id:int,db:Session=Depends(get_db), user: User=Depends(current_user)):
    habit=db.scalar(select(Habit).where(Habit.id == habit_id, Habit.owner_id == user.id))
    if not habit: raise HTTPException(status_code=404,detail="Habit not found")
    db.query(HabitLog).filter(HabitLog.habit_id==habit_id).delete();db.delete(habit);db.commit()

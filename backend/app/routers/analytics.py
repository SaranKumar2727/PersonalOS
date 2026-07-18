from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import String, func, select
from app.database import SessionLocal
from app.models import Expense, Habit, Publication, Task
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
@router.get("")
def analytics(user: User = Depends(current_user)):
    db=SessionLocal(); month=date.today().strftime('%Y-%m')
    try:
        expenses=db.scalars(select(Expense).where(Expense.owner_id == user.id, Expense.expense_date.cast(String).like(f'{month}%'))).all()
        categories={}
        for item in expenses: categories[item.category]=categories.get(item.category,0)+item.amount
        total_tasks=db.scalar(select(func.count(Task.id)).where(Task.owner_id == user.id)) or 0; completed_tasks=db.scalar(select(func.count(Task.id)).where(Task.owner_id == user.id, Task.completed.is_(True))) or 0
        return {'month':month,'spending':{'total':sum(categories.values()),'by_category':categories},'tasks':{'total':total_tasks,'completed':completed_tasks},'habits':db.scalar(select(func.count(Habit.id)).where(Habit.owner_id == user.id)) or 0,'publications':db.scalar(select(func.count(Publication.id)).where(Publication.owner_id == user.id)) or 0}
    finally: db.close()

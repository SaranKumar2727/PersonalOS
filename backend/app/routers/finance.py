from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import String, select
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Expense
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/finance/expenses", tags=["finance"])
class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=240)
    amount: float = Field(gt=0)
    category: str = Field(default="Other", max_length=80)
    expense_date: date
    notes: str = Field(default="", max_length=500)
class ExpenseRead(ExpenseCreate):
    id: int
    model_config = {"from_attributes": True}
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
@router.get("", response_model=list[ExpenseRead])
def list_expenses(month: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    statement = select(Expense).order_by(Expense.expense_date.desc(), Expense.id.desc())
    statement = statement.where(Expense.owner_id == user.id)
    if month: statement = statement.where(Expense.expense_date.cast(String).like(f"{month}%"))
    return db.scalars(statement).all()
@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = Expense(**payload.model_dump(), owner_id=user.id); db.add(item); db.commit(); db.refresh(item); return item
@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Expense).where(Expense.id == expense_id, Expense.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(item); db.commit()

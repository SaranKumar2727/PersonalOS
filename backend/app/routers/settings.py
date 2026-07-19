from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.models import User
from app.routers.auth import current_user, get_db

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])
class OpenAIKey(BaseModel): key: str = Field(min_length=10, max_length=300)
@router.get("/status")
def status(user: User = Depends(current_user)): return {"openai_configured": bool(user.openai_api_key)}
@router.post("/openai-key")
def set_openai_key(payload: OpenAIKey, user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.openai_api_key = payload.key
    db.commit()
    return {"configured": True}

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.config import settings

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])
class OpenAIKey(BaseModel): key: str = Field(min_length=10, max_length=300)
@router.get("/status")
def status(): return {"openai_configured": bool(settings.openai_api_key)}
@router.post("/openai-key")
def set_openai_key(payload: OpenAIKey):
    settings.openai_api_key = payload.key
    return {"configured": True}

from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.routers.auth import current_user
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=12000)
class ChatRequest(BaseModel):
    messages: list[ChatMessage]

@router.post("/chat")
def chat(payload: ChatRequest, user: User = Depends(current_user)):
    if not user.openai_api_key:
        return {"message": "Your AI assistant is not configured yet. Open Settings → AI integrations and add your OpenAI API key."}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=user.openai_api_key)
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions="You are the Personal OS assistant. Be concise, practical, and help the user organize tasks, notes, calendar, finance, knowledge, documents, and publications. When asked to take an action, explain the next step clearly.",
            input=[{"role": message.role, "content": message.content} for message in payload.messages[-20:]],
        )
        return {"message": response.output_text}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI provider error: {exc}")

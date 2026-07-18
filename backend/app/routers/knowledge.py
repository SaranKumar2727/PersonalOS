from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import KnowledgeArticle
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    summary: str = Field(default="", max_length=500)
    content: str = ""
    category: str = Field(default="General", max_length=80)
    tags: str = Field(default="", max_length=500)
    favorite: bool = False


class ArticleRead(ArticleCreate):
    id: int
    updated_at: datetime
    model_config = {"from_attributes": True}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[ArticleRead])
def list_articles(query: str | None = None, category: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    statement = select(KnowledgeArticle).where(KnowledgeArticle.owner_id == user.id).order_by(KnowledgeArticle.favorite.desc(), KnowledgeArticle.updated_at.desc())
    if query:
        term = f"%{query}%"
        statement = statement.where(KnowledgeArticle.title.ilike(term) | KnowledgeArticle.summary.ilike(term) | KnowledgeArticle.tags.ilike(term))
    if category:
        statement = statement.where(KnowledgeArticle.category == category)
    return db.scalars(statement).all()


@router.post("", response_model=ArticleRead, status_code=status.HTTP_201_CREATED)
def create_article(payload: ArticleCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    article = KnowledgeArticle(**payload.model_dump(), owner_id=user.id)
    db.add(article); db.commit(); db.refresh(article)
    return article


@router.patch("/{article_id}", response_model=ArticleRead)
def update_article(article_id: int, payload: ArticleCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    article = db.scalar(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id, KnowledgeArticle.owner_id == user.id))
    if not article: raise HTTPException(status_code=404, detail="Article not found")
    for name, value in payload.model_dump().items(): setattr(article, name, value)
    db.commit(); db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    article = db.scalar(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id, KnowledgeArticle.owner_id == user.id))
    if not article: raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article); db.commit()

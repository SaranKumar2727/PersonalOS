import re
from io import BytesIO
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
import httpx
from html.parser import HTMLParser

from app.config import settings
from app.database import SessionLocal
from app.models import Publication
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/publications", tags=["publications"])

class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts: list[str] = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}: self.hidden += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self.hidden: self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden and data.strip(): self.parts.append(data.strip())

def extract_paper(url: str) -> str:
    response = httpx.get(url, follow_redirects=True, timeout=25, headers={"User-Agent": "PersonalOS/0.1"})
    response.raise_for_status()
    if "pdf" in response.headers.get("content-type", "").lower() or url.lower().split("?")[0].endswith(".pdf"):
        from pypdf import PdfReader
        return "\n\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(response.content)).pages)
    parser = VisibleTextParser(); parser.feed(response.text)
    return " ".join(parser.parts)

class PublicationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    authors: str = ""
    year: int | None = None
    venue: str = ""
    abstract: str = ""
    url: str = ""
    summary: str = ""
class PublicationRead(PublicationCreate):
    id: int; created_at: datetime
    model_config = {"from_attributes": True}
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("", response_model=list[PublicationRead])
def list_publications(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.scalars(select(Publication).where(Publication.owner_id == user.id).order_by(Publication.year.desc(), Publication.created_at.desc())).all()
@router.post("", response_model=PublicationRead, status_code=status.HTTP_201_CREATED)
def create_publication(payload: PublicationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = Publication(**payload.model_dump(), owner_id=user.id); db.add(item); db.commit(); db.refresh(item); return item
@router.patch("/{publication_id}", response_model=PublicationRead)
def update_publication(publication_id: int, payload: PublicationCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Publication).where(Publication.id == publication_id, Publication.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Publication not found")
    for name, value in payload.model_dump().items(): setattr(item, name, value)
    db.commit(); db.refresh(item); return item
@router.delete("/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_publication(publication_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Publication).where(Publication.id == publication_id, Publication.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Publication not found")
    db.delete(item); db.commit()
@router.post("/{publication_id}/summarize", response_model=PublicationRead)
def summarize_publication(publication_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Publication).where(Publication.id == publication_id, Publication.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Publication not found")
    text = item.abstract.strip()
    source = "abstract"
    if item.url.strip():
        try:
            linked_text = extract_paper(item.url.strip())
            if len(linked_text) >= 500:
                text, source = linked_text, "publication link"
        except Exception:
            pass
    if not text: raise HTTPException(status_code=400, detail="Add an abstract before summarizing")
    if settings.openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            # Keep the prompt explicit: this is a multi-paragraph paper summary, not an abstract paraphrase.
            result = client.responses.create(model="gpt-4o-mini", input=f"Write a clear summary of the full research paper in exactly 4 or 5 substantial paragraphs. Cover the research question, methods, key findings, limitations, and practical implications. Do not mention that you are an AI. Source: {source}.\n\n{text[:120000]}")
            item.summary = result.output_text.strip()
        except Exception:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            item.summary = "\n\n".join(" ".join(sentences[i:i + max(1, len(sentences) // 5)]) for i in range(0, len(sentences), max(1, len(sentences) // 5)))[:8000]
    else:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunk = max(1, len(sentences) // 5)
        item.summary = "\n\n".join(" ".join(sentences[i:i + chunk]) for i in range(0, len(sentences), chunk))[:8000]
    db.commit(); db.refresh(item); return item

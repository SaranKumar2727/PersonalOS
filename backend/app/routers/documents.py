from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import DocumentFile, DocumentFolder
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
DOC_DIR = Path("uploads/documents")
MAX_SIZE = 50 * 1024 * 1024

class FolderCreate(BaseModel): name: str = Field(min_length=1, max_length=120)
class FolderRead(FolderCreate):
    id: int
    model_config = {"from_attributes": True}
class DocumentRead(BaseModel):
    id: int; name: str; original_name: str; url: str; mime_type: str; size: int; folder_id: int | None
    model_config = {"from_attributes": True}
class RenameRequest(BaseModel): name: str = Field(min_length=1, max_length=240)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/folders", response_model=list[FolderRead])
def folders(db: Session = Depends(get_db), user: User = Depends(current_user)): return db.scalars(select(DocumentFolder).where(DocumentFolder.owner_id == user.id).order_by(DocumentFolder.name)).all()

@router.post("/folders", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
def create_folder(payload: FolderCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    folder = DocumentFolder(name=payload.name, owner_id=user.id); db.add(folder); db.commit(); db.refresh(folder); return folder

@router.get("", response_model=list[DocumentRead])
def documents(folder_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    statement = select(DocumentFile).where(DocumentFile.owner_id == user.id).order_by(DocumentFile.created_at.desc())
    if folder_id is not None: statement = statement.where(DocumentFile.folder_id == folder_id)
    return db.scalars(statement).all()

@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), name: str | None = Form(default=None), folder_id: int | None = Form(default=None), db: Session = Depends(get_db), user: User = Depends(current_user)):
    content = await file.read()
    if len(content) > MAX_SIZE: raise HTTPException(status_code=413, detail="Documents must be 50 MB or smaller")
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    original = file.filename or "document"; target = DOC_DIR / f"{uuid4().hex}{Path(original).suffix.lower()}"; target.write_bytes(content)
    if folder_id and not db.scalar(select(DocumentFolder).where(DocumentFolder.id == folder_id, DocumentFolder.owner_id == user.id)): raise HTTPException(status_code=404, detail="Folder not found")
    item = DocumentFile(name=(name or Path(original).stem).strip(), original_name=original, url=f"/uploads/documents/{target.name}", mime_type=file.content_type or "application/octet-stream", size=len(content), folder_id=folder_id, owner_id=user.id)
    db.add(item); db.commit(); db.refresh(item); return item

@router.patch("/{document_id}", response_model=DocumentRead)
def rename_document(document_id: int, payload: RenameRequest, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(DocumentFile).where(DocumentFile.id == document_id, DocumentFile.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Document not found")
    item.name = payload.name; db.commit(); db.refresh(item); return item

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(DocumentFile).where(DocumentFile.id == document_id, DocumentFile.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Document not found")
    db.delete(item); db.commit()

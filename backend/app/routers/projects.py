from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Project
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=500)
    language: str = Field(default="Other", max_length=60)
    visibility: str = Field(default="Private", pattern="^(Private|Public)$")
    deployed_url: str = ""
    repository_url: str = ""
    readme: str = ""
class ProjectRead(ProjectCreate):
    id: int; created_at: datetime
    model_config = {"from_attributes": True}
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db), user: User = Depends(current_user)): return db.scalars(select(Project).where(Project.owner_id == user.id).order_by(Project.created_at.desc())).all()
@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = Project(**payload.model_dump(), owner_id=user.id); db.add(item); db.commit(); db.refresh(item); return item
@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Project).where(Project.id == project_id, Project.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Project not found")
    for name, value in payload.model_dump().items(): setattr(item, name, value)
    db.commit(); db.refresh(item); return item
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(Project).where(Project.id == project_id, Project.owner_id == user.id))
    if not item: raise HTTPException(status_code=404, detail="Project not found")
    db.delete(item); db.commit()

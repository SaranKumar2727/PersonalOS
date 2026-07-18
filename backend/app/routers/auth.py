import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    email: str = Field(min_length=5, max_length=240)
    password: str = Field(min_length=8, max_length=200)
class LoginRequest(BaseModel): email: str; password: str
class UserRead(BaseModel): id: int; name: str; email: str
class TokenRead(BaseModel): access_token: str; token_type: str = "bearer"; user: UserRead
class GitHubProfile(BaseModel): username: str = Field(min_length=1, max_length=160)
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
def password_hash(value: str, salt: str | None = None):
    salt = salt or secrets.token_hex(16); digest = hashlib.pbkdf2_hmac('sha256', value.encode(), salt.encode(), 120000).hex(); return f"{salt}${digest}"
def password_matches(value: str, encoded: str):
    salt, digest = encoded.split('$',1); return secrets.compare_digest(password_hash(value,salt).split('$',1)[1], digest)
def make_token(user: User):
    return jwt.encode({'sub':str(user.id),'exp':datetime.now(timezone.utc)+timedelta(days=7)}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
def serialize(user: User): return {'id':user.id,'name':user.name,'email':user.email}
@router.post("/register", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session=Depends(get_db)):
    email=payload.email.strip().lower()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(status_code=409, detail="Email is already registered")
    user=User(name=payload.name.strip(),email=email,password_hash=password_hash(payload.password));db.add(user);db.commit();db.refresh(user);return {'access_token':make_token(user),'user':serialize(user)}
@router.post("/login", response_model=TokenRead)
def login(payload: LoginRequest, db: Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==payload.email.strip().lower()))
    if not user or not password_matches(payload.password,user.password_hash): raise HTTPException(status_code=401, detail="Invalid email or password")
    return {'access_token':make_token(user),'user':serialize(user)}
def current_user(credentials: HTTPAuthorizationCredentials=Depends(bearer), db: Session=Depends(get_db)):
    if not credentials: raise HTTPException(status_code=401, detail="Authentication required")
    try: user_id=jwt.decode(credentials.credentials,settings.jwt_secret,algorithms=[settings.jwt_algorithm]).get('sub')
    except JWTError: raise HTTPException(status_code=401, detail="Invalid or expired token")
    user=db.get(User,int(user_id)) if user_id else None
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user
@router.get("/me", response_model=UserRead)
def me(user: User=Depends(current_user)): return serialize(user)
@router.patch("/github-profile")
def github_profile(payload: GitHubProfile, user: User = Depends(current_user), db: Session = Depends(get_db)):
    user.github_username = payload.username.strip().removeprefix("https://github.com/").strip("/")
    db.commit()
    return {"github_username": user.github_username}
@router.get("/oauth/{provider}/start")
def oauth_start(provider: str):
    if provider == 'google' and settings.google_client_id:
        return {'url':'https://accounts.google.com/o/oauth2/v2/auth?'+urlencode({'client_id':settings.google_client_id,'redirect_uri':settings.oauth_redirect_url,'response_type':'code','scope':'openid email profile'})}
    if provider == 'github' and settings.github_client_id:
        return {'url':'https://github.com/login/oauth/authorize?'+urlencode({'client_id':settings.github_client_id,'redirect_uri':settings.oauth_redirect_url,'scope':'read:user user:email'})}
    raise HTTPException(status_code=503, detail=f'{provider.title()} OAuth is not configured')

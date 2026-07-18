import httpx
from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.routers.auth import current_user

router = APIRouter(prefix="/api/v1/github", tags=["github"])
@router.get("/repos")
def repositories(username: str | None = None, user: User = Depends(current_user)):
    target = (username or user.github_username or "").strip().removeprefix("https://github.com/").strip("/")
    if not target: raise HTTPException(status_code=400, detail="Add a GitHub username or profile URL in Settings")
    try:
        response = httpx.get(f"https://api.github.com/users/{target}/repos", params={"sort":"updated","per_page":100}, headers={"Accept":"application/vnd.github+json","User-Agent":"PersonalOS"}, timeout=20)
        if response.status_code == 404: raise HTTPException(status_code=404, detail="GitHub profile not found")
        response.raise_for_status()
        return [{"id": repo["id"], "name": repo["name"], "description": repo.get("description") or "", "language": repo.get("language") or "Other", "visibility": "Public", "repository_url": repo["html_url"], "deployed_url": "", "stars": repo.get("stargazers_count", 0), "forks": repo.get("forks_count", 0), "updated_at": repo.get("updated_at")} for repo in response.json()]
    except httpx.HTTPError as exc: raise HTTPException(status_code=502, detail=f"GitHub request failed: {exc}")

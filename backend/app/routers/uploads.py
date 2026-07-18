from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])
UPLOAD_DIR = Path("uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "video/webm"}
MAX_FILE_SIZE = 25 * 1024 * 1024


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Use JPEG, PNG, GIF, WebP, MP4, or WebM files")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Files must be 25 MB or smaller")
    extension = Path(file.filename or "upload").suffix.lower()
    target = UPLOAD_DIR / f"{uuid4().hex}{extension}"
    UPLOAD_DIR.mkdir(exist_ok=True)
    target.write_bytes(content)
    return {"url": f"/uploads/{target.name}", "type": file.content_type}

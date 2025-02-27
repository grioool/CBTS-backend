from datetime import datetime

from fastapi import APIRouter, HTTPException
from google.cloud.storage import bucket

router = APIRouter()

@router.get("/download/{filename}")
async def download_file(filename: str):
    blob = bucket.blob(f"uploads/{filename}")
    if not blob.exists():
        raise HTTPException(status_code=404, detail="File not found")

    url = blob.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15), method="GET")
    return {"url": url}

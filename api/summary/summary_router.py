from fastapi import APIRouter, HTTPException
from google.cloud.storage import bucket

router = APIRouter()


@router.get("/summary/{filename}")
async def get_summary(filename: str):
    blob = bucket.blob(f"summaries/{filename}.txt")
    if not blob.exists():
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary": blob.download_as_text()}

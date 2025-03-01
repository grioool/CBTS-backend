from fastapi import APIRouter, HTTPException
from google.cloud import storage

storage_client = storage.Client()
bucket_name = "cbts-bucket"
bucket = storage_client.bucket(bucket_name)

router = APIRouter()


@router.get("/summary/{filename}")
async def get_summary(filename: str):
    blob = bucket.blob(f"summaries/{filename}.txt")
    if not blob.exists():
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary": blob.download_as_text()}

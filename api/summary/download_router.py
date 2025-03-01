from datetime import datetime

from fastapi import APIRouter, HTTPException
from google.cloud import storage
from fastapi.responses import FileResponse

storage_client = storage.Client()
bucket_name = "cbts-bucket"
bucket = storage_client.bucket(bucket_name)

router = APIRouter()

@router.get("/download/{filename}")
async def download_file(filename: str):
    blob = bucket.blob(f"summaries/{filename}.txt")
    if not blob.exists():
        raise HTTPException(status_code=404, detail="Summary not found")
    tmp_path = f"/tmp/{filename}"
    blob.download_to_filename(tmp_path)

    return FileResponse(
        path=tmp_path,
        media_type="text/plain",
        filename=f"{filename}.txt"
    )
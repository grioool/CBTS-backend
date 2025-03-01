from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from google.cloud import storage

from api.summary.length import Length
from api.summary.style import Style
from api.summary.summary_service import summarize_pdf

storage_client = storage.Client()
bucket_name = "cbts-bucket"
bucket = storage_client.bucket(bucket_name)

router = APIRouter(prefix="/summary")


@router.post("/summarize")
async def summarize_file(length: Length, style: Style, file: UploadFile = File(...)):
    try:
        summary, gcs_path = await summarize_pdf(length, style, file)
        return {"summary": summary, "file_path": gcs_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{filename}")
async def get_summary(filename: str):
    blob = bucket.blob(f"summaries/{filename}.txt")
    if not blob.exists():
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"summary": blob.download_as_text()}


@router.get("/{filename}/download")
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

# api/summary/summary_router.py
import os
import tempfile
from typing import Annotated

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from google.cloud import storage

from api.auth.auth_service import oauth2_scheme
from api.summary.length import Length
from api.summary.style import Style
from api.summary.summary_service import SummaryServiceDep
from config.storage_settings import storage_settings


def get_bucket():
    """Create and return a GCS bucket lazily."""
    client = storage.Client()
    return client.bucket(storage_settings.STORAGE_NAME)


router = APIRouter(prefix="/summary")


@router.post("/summarize")
async def summarize_file(
    length: Length,
    style: Style,
    summary_service: SummaryServiceDep,
    token: Annotated[str, Depends(oauth2_scheme)],
    file: UploadFile = File(...),
):
    try:
        summary, gcs_path = await summary_service.summarize_pdf(length, style, file, token)
        return {"summary": summary, "file_path": gcs_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{summary_id}")
async def get_summary(summary_id: int, summary_service: SummaryServiceDep):
    summary = summary_service.get_by_id(summary_id)
    bucket = get_bucket()
    blob = bucket.blob(f"summaries/{summary.filename_hash}.txt")

    if not blob.exists():
        raise HTTPException(status_code=404, detail="Summary not found")

    return {"summary": blob.download_as_text()}


def remove_file(path: str):
    """Background task to delete a temporary file after response is sent."""
    try:
        os.remove(path)
    except Exception as e:
        print(f"Error removing file {path}: {e}")


@router.get("/{summary_id}/download")
async def download_file(summary_id: int, summary_service: SummaryServiceDep, background_tasks: BackgroundTasks):
    summary = summary_service.get_by_id(summary_id)
    bucket = get_bucket()
    blob = bucket.blob(f"summaries/{summary.filename_hash}.txt")

    if not blob.exists():
        raise HTTPException(status_code=404, detail="Summary not found")

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        blob.download_to_filename(tmp.name)
        tmp_path = tmp.name

    background_tasks.add_task(remove_file, tmp_path)

    return FileResponse(
        path=tmp_path,
        media_type="text/plain",
        filename=f"{summary.filename}.txt",
    )

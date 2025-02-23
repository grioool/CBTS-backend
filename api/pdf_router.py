import pymupdf
from fastapi import APIRouter, UploadFile

router = APIRouter()

@router.post("/upload")
def upload(file: UploadFile):
    return {"file_id": "abc123",
            "status": "processing",
            "message": "File uploaded successfully"}

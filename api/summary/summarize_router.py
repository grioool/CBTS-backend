from fastapi import APIRouter, HTTPException, UploadFile, File

from api.summary.summary_service import summarize_pdf

router = APIRouter()


@router.post("/summarize")
async def summarize_file(file: UploadFile = File(...)):
    try:
        summary, gcs_path = await summarize_pdf(file)
        return {"summary": summary, "file_path": gcs_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

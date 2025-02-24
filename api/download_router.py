from fastapi import APIRouter

router = APIRouter()


@router.get("/summary/download")
def download_summary():
    return {
        "filename": "abc123"
    }

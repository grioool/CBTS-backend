from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
def get_summary():
    return {
  "file_id": "abc123",
  "status": "completed",
  "summary": "This is a summarized version of the document..."
}

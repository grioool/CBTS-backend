from fastapi import APIRouter

router = APIRouter()

@router.get("/user/history")
def get_history():
    return {
  "user_id": "user_789",
  "history": [
    {
      "file_id": "abc123",
      "filename": "report.pdf",
      "date": "2025-02-21",
      "status": "completed"
    },
    {
      "file_id": "xyz456",
      "filename": "thesis.txt",
      "date": "2025-02-18",
      "status": "failed"
    }
  ]
}

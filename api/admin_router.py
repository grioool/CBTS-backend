from fastapi import APIRouter

router = APIRouter()


@router.get("/admin/analytics")
def get_admin_analytics():
    return {
        "total_summaries": 12500,
        "active_users": 3500
    }
